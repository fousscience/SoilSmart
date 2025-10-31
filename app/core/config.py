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

settings = Settings()
