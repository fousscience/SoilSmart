# app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.agents.orchestrator_agent import OrchestratorAgent

app = FastAPI(title="SoilSmart API")

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """Analyzes the soil report PDF and returns a full report in French plus summaries."""
    try:
        orchestrator = OrchestratorAgent()
        # The orchestrator now handles all languages internally
        report_data = orchestrator.run(file, language="fr") 
        return JSONResponse(report_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))