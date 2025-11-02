import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CHROMA_PATH = os.getenv("CHROMA_PATH", "app/data/chroma_db")
    MODEL_NAME = "gpt-4o-mini"  # ou GPT-4-turbo
    EMBEDDING_MODEL = "text-embedding-3-large"
    REPORT_LANGUAGE = os.getenv("REPORT_LANGUAGE", "fr")  # fr, wo (wolof), bm (bambara)
    DJELIA_API_KEY = os.getenv("DJELIA_API_KEY")
    # Redis cache settings (optional, falls back to in-memory cache)
    # Supports both URL format (redis://host:port) and host/port format
    REDIS_HOST = os.getenv("REDIS_HOST") or os.getenv("REDIS_URL", None)
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    REDIS_TTL = int(os.getenv("REDIS_TTL", "3600"))  # 1 hour default
    # Uvicorn workers (0 = auto-detect based on CPU)
    UVICORN_WORKERS = int(os.getenv("UVICORN_WORKERS", "2"))

settings = Settings()
