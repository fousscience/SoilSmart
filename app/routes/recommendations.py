# app/routes/recommendations.py
from fastapi import APIRouter, UploadFile
from app.core.vector_store import VectorStore
import tempfile

router = APIRouter(prefix="/docs", tags=["Documents"])
vstore = VectorStore()

@router.post("/upload")
async def upload_document(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    vstore.add_document(tmp_path, {"filename": file.filename})
    return {"status": "success", "file": file.filename}

@router.get("/query")
async def query_docs(query: str, n: int = 3):
    results = vstore.query(query, n)
    return {"results": results}
