# app/models/schemas.py
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    file_path: str  # Optionnel si on envoie un chemin

class DocumentUpload(BaseModel):
    file_path: str
    metadata: dict = {}
