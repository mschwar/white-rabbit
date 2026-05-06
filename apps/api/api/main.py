from pathlib import Path
import sys
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_SRC = REPO_ROOT / "packages" / "core" / "src"
for candidate in (CORE_SRC, REPO_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from core.cost import RunMetrics
from core.models import Lead
from core.orchestrator import scout

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
        leads, metrics = await scout(request.query, filters=request.filters)
        return ScoutResponse(leads=leads, metrics=metrics)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
