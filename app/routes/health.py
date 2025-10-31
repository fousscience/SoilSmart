# app/routes/health.py
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {"status": "ok"}
