import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from dotenv import load_dotenv

from core.orchestrator import scout
from core.models import Lead
from core.cost import RunMetrics

load_dotenv()

app = FastAPI(title="White Rabbit API")

class ScoutRequest(BaseModel):
    query: str
    filters: Optional[dict] = None

class ScoutResponse(BaseModel):
    leads: list[Lead]
    metrics: RunMetrics

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/scout", response_model=ScoutResponse)
async def run_scout(request: ScoutRequest):
    try:
        leads, metrics = await scout(request.query)
        return ScoutResponse(leads=leads, metrics=metrics)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
