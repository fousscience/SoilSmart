# app/main.py
import hashlib
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.agents.orchestrator_agent import OrchestratorAgent
from app.core.cache import cache

app = FastAPI(title="SoilSense API")

# Reuse orchestrator instance to avoid recreating agents on every request
_orchestrator = None

def get_orchestrator():
    """Get or create orchestrator instance (singleton pattern)"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """Analyzes the soil report PDF and returns a full report in French plus summaries."""
    try:
        # Read file content for cache key generation
        file_content = await file.read()
        
        # Generate cache key from file hash
        file_hash = hashlib.md5(file_content).hexdigest()
        cache_key = cache._generate_key("report", file_hash)
        
        # Try to get from cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            return JSONResponse(cached_result)
        
        # Create a wrapper object that mimics UploadFile interface
        # The orchestrator expects an object with .file.read() method
        from io import BytesIO
        
        class FileWrapper:
            def __init__(self, content, filename):
                self.content = content
                self.filename = filename
                self.file = BytesIO(content)
            
            def read(self):
                return self.content
        
        file_wrapper = FileWrapper(file_content, file.filename)
        
        # If not in cache, process the file
        orchestrator = get_orchestrator()
        # The orchestrator now handles all languages internally
        report_data = orchestrator.run(file_wrapper, language="fr")
        
        # Cache the result (TTL from settings, default 1 hour)
        cache.set(cache_key, report_data)
        
        return JSONResponse(report_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "cache": "redis" if cache.redis_client else "memory"}