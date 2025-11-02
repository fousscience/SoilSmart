FROM python:3.11-slim

WORKDIR /soilsmart

# Install system dependencies first (build tools and libraries needed for Python packages)
# This layer will be cached if dependencies don't change
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    tesseract-ocr \
    poppler-utils \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-xlib-2.0-dev \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
# This layer will be cached if requirements.txt doesn't change
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Remove build tools to reduce image size (in separate layer for clarity)
RUN apt-get update && \
    apt-get purge -y build-essential gcc g++ && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy application code last (most frequently changing)
COPY . .

EXPOSE 8000 8501

# Use gunicorn with uvicorn workers for better performance
# Workers are set via UVICORN_WORKERS env var (default: 2)
CMD ["bash", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS:-2} & streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
