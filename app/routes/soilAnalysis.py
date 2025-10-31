# app/routes/soil_analysis.py
from fastapi import APIRouter, UploadFile
from app.agents.orchestrator_agent import OrchestratorAgent

router = APIRouter(prefix="/analyze", tags=["Analyse"])

@router.post("/")
async def analyze_pdf(file: UploadFile):
    orchestrator = OrchestratorAgent()
    report = orchestrator.run(file)
    return {"report": report}
