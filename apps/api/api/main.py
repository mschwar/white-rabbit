from pathlib import Path
import sys
from typing import Any, Optional
from uuid import UUID

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
from core.orchestrator import scout, OrchestratorError

from api.db import (
    init_db,
    get_db_session,
    create_recipe,
    create_recipe_run,
    save_leads,
    close_recipe_run,
    get_recipes,
    get_recipe_runs,
    get_leads_for_run,
    add_lead_feedback,
    get_recipe_scoreboard,
)

load_dotenv()

# Initialize database on startup
init_db()

app = FastAPI(title="White Rabbit API")


class ScoutRequest(BaseModel):
    query: str
    filters: Optional[dict] = None


class FullRequest(BaseModel):
    query: str
    filters: Optional[dict] = None
    recipe_name: Optional[str] = None


class ScoutResponse(BaseModel):
    leads: list[Lead]
    metrics: RunMetrics


class FullResponse(BaseModel):
    run_id: UUID
    leads: list[Lead]
    metrics: RunMetrics
    recipe_id: UUID | None = None


class FeedbackRequest(BaseModel):
    label: str  # usable, wrong_persona, bad_source, bad_contact, duplicate


class RecipeOut(BaseModel):
    id: UUID
    name: str
    query: str
    filters: dict
    created_at: str

    model_config = {"from_attributes": True}


class RecipeRunOut(BaseModel):
    id: UUID
    recipe_id: UUID | None = None
    mode: str
    started_at: str
    ended_at: str | None = None
    operator_minutes: float | None = None
    lead_count: int

    model_config = {"from_attributes": True}


class RecipeScoreboardOut(BaseModel):
    recipe_id: UUID
    recipe_name: str
    total_api_cost_usd: float
    total_leads_returned: int
    usable_lead_count: int
    total_operator_minutes: float
    minutes_per_usable_lead: float | None = None
    api_cost_per_usable_lead: float | None = None
    feedback_counts: dict[str, int]

    model_config = {"from_attributes": True}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/scout", response_model=ScoutResponse)
async def run_scout(request: ScoutRequest):
    try:
        leads, metrics = await scout(request.query, filters=request.filters)
        return ScoutResponse(leads=leads, metrics=metrics)
    except OrchestratorError as exc:
        import logging
        logging.getLogger("white_rabbit.api").error("Orchestrator error: %s", exc, exc_info=True)
        raise HTTPException(status_code=503, detail="The search service is currently unavailable. Please try again later.")
    except Exception as exc:
        import logging
        logging.getLogger("white_rabbit.api").error("Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")


@app.post("/full", response_model=FullResponse)
async def run_full(request: FullRequest):
    """Run a Full query: produces a stored recipe and recipe_run."""
    try:
        leads, metrics = await scout(request.query, filters=request.filters, max_leads=100)
    except OrchestratorError as exc:
        import logging
        logging.getLogger("white_rabbit.api").error("Orchestrator error: %s", exc, exc_info=True)
        raise HTTPException(status_code=503, detail="The search service is currently unavailable. Please try again later.")
    except Exception as exc:
        import logging
        logging.getLogger("white_rabbit.api").error("Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

    with get_db_session() as session:
        recipe = create_recipe(
            session,
            name=request.recipe_name or request.query,
            query=request.query,
            filters=request.filters,
        )
        run = create_recipe_run(
            session,
            mode="full",
            recipe_id=recipe.id,
            lead_count=len(leads),
            api_cost_breakdown={
                "input_tokens": metrics.input_tokens,
                "output_tokens": metrics.output_tokens,
                "tavily_searches": metrics.tavily_searches,
                "estimated_cost_usd": metrics.estimated_cost_usd,
            },
        )
        lead_dicts = [lead.model_dump() for lead in leads]
        save_leads(session, run.id, lead_dicts)

        return FullResponse(
            run_id=run.id,
            leads=leads,
            metrics=metrics,
            recipe_id=recipe.id,
        )


@app.get("/recipes", response_model=list[RecipeOut])
async def list_recipes():
    with get_db_session() as session:
        recipes = get_recipes(session)
        return [
            RecipeOut(
                id=r.id,
                name=r.name,
                query=r.query,
                filters=r.filters,
                created_at=r.created_at.isoformat(),
            )
            for r in recipes
        ]


@app.get("/recipes/{recipe_id}/runs", response_model=list[RecipeRunOut])
async def list_recipe_runs(recipe_id: UUID):
    with get_db_session() as session:
        runs = get_recipe_runs(session, recipe_id=recipe_id)
        return [
            RecipeRunOut(
                id=r.id,
                recipe_id=r.recipe_id,
                mode=r.mode,
                started_at=r.started_at.isoformat(),
                ended_at=r.ended_at.isoformat() if r.ended_at else None,
                operator_minutes=r.operator_minutes,
                lead_count=r.lead_count,
            )
            for r in runs
        ]


@app.get("/recipes/{recipe_id}/scoreboard", response_model=RecipeScoreboardOut)
async def recipe_scoreboard(recipe_id: UUID):
    with get_db_session() as session:
        scoreboard = get_recipe_scoreboard(session, recipe_id)
        if not scoreboard:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return RecipeScoreboardOut(**scoreboard)


@app.post("/leads/{lead_id}/feedback")
async def submit_feedback(lead_id: UUID, request: FeedbackRequest):
    with get_db_session() as session:
        add_lead_feedback(session, lead_id, request.label)
        return {"status": "ok"}


@app.post("/runs/{run_id}/close")
async def close_run(run_id: UUID, operator_minutes: float | None = None):
    with get_db_session() as session:
        run = close_recipe_run(session, run_id, operator_minutes)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return {"status": "ok", "ended_at": run.ended_at.isoformat() if run.ended_at else None}
