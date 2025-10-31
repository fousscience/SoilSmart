FROM python:3.11-slim

WORKDIR /soilsmart

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# OCR dependencies
RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils

COPY . .

EXPOSE 8000 8501

CMD ["bash", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
