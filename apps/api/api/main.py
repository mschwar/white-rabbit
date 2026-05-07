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
from core.query_guardrails import QueryGuardrailResult, evaluate_query_guardrails

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
    create_batch_job,
    create_batch_run,
    update_batch_run,
    close_batch_job,
    get_batch_job,
    get_batch_runs,
    list_batch_jobs,
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
    query_guardrail: QueryGuardrailResult | None = None


class FullResponse(BaseModel):
    run_id: UUID
    leads: list[Lead]
    metrics: RunMetrics
    recipe_id: UUID | None = None
    query_guardrail: QueryGuardrailResult | None = None


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


def _query_guardrail_or_422(query: str) -> QueryGuardrailResult:
    guardrail = evaluate_query_guardrails(query)
    if guardrail.status == 'blocked':
        raise HTTPException(
            status_code=422,
            detail={'error': guardrail.message, 'query_guardrail': guardrail.model_dump()},
        )
    return guardrail


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/scout", response_model=ScoutResponse)
async def run_scout(request: ScoutRequest):
    guardrail = _query_guardrail_or_422(request.query)
    try:
        leads, metrics = await scout(request.query, filters=request.filters)
        return ScoutResponse(leads=leads, metrics=metrics, query_guardrail=guardrail if guardrail.status != 'clear' else None)
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
    guardrail = _query_guardrail_or_422(request.query)
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
            query_guardrail=guardrail if guardrail.status != 'clear' else None,
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


class BatchQueryItem(BaseModel):
    query: str
    filters: Optional[dict] = None
    recipe_name: Optional[str] = None


class BatchRequest(BaseModel):
    name: str
    queries: list[BatchQueryItem]
    cap_queries: int = 10
    cap_max_leads: int = 1000
    cap_max_spend_usd: float = 10.0


class BatchRunOut(BaseModel):
    id: UUID
    query: str
    status: str
    lead_count: int
    cost_usd: float
    error_message: str | None = None
    recipe_id: UUID | None = None
    started_at: str | None = None
    ended_at: str | None = None

    model_config = {"from_attributes": True}


class BatchJobOut(BaseModel):
    id: UUID
    name: str
    status: str
    cap_queries: int
    cap_max_leads: int
    cap_max_spend_usd: float
    created_at: str
    started_at: str | None = None
    ended_at: str | None = None
    total_cost_usd: float
    total_leads: int
    runs: list[BatchRunOut]

    model_config = {"from_attributes": True}


@app.post("/batch", response_model=BatchJobOut)
async def run_batch(request: BatchRequest):
    """Run a batch of Full queries sequentially with caps."""
    from datetime import datetime

    with get_db_session() as session:
        job = create_batch_job(
            session,
            name=request.name,
            cap_queries=request.cap_queries or 10,
            cap_max_leads=request.cap_max_leads or 1000,
            cap_max_spend_usd=request.cap_max_spend_usd or 10.0,
        )
        run_records: list[BatchRunOut] = []
        total_cost = 0.0
        total_leads = 0

        job.status = "running"
        job.started_at = datetime.utcnow()
        session.flush()

        for idx, item in enumerate(request.queries[:job.cap_queries]):
            batch_run = create_batch_run(session, job.id, item.query)
            batch_run.status = "running"
            batch_run.started_at = datetime.utcnow()
            session.flush()

            guardrail = evaluate_query_guardrails(item.query)
            if guardrail.status == 'blocked':
                batch_run.status = "failed"
                batch_run.error_message = guardrail.message
                batch_run.ended_at = datetime.utcnow()
                update_batch_run(
                    session,
                    batch_run.id,
                    status="failed",
                    error_message=guardrail.message,
                )
                run_records.append(
                    BatchRunOut(
                        id=batch_run.id,
                        query=item.query,
                        status="failed",
                        lead_count=0,
                        cost_usd=0.0,
                        error_message=guardrail.message,
                    )
                )
                continue

            try:
                leads, metrics = await scout(
                    item.query,
                    filters=item.filters,
                    max_leads=job.cap_max_leads,
                )
            except OrchestratorError as exc:
                import logging
                logging.getLogger("white_rabbit.api").error("Batch orchestrator error: %s", exc, exc_info=True)
                batch_run.status = "failed"
                batch_run.error_message = str(exc)
                batch_run.ended_at = datetime.utcnow()
                update_batch_run(
                    session,
                    batch_run.id,
                    status="failed",
                    error_message=str(exc),
                )
                run_records.append(
                    BatchRunOut(
                        id=batch_run.id,
                        query=item.query,
                        status="failed",
                        lead_count=0,
                        cost_usd=0.0,
                        error_message=str(exc),
                    )
                )
                continue
            except Exception as exc:
                import logging
                logging.getLogger("white_rabbit.api").error("Batch unexpected error: %s", exc, exc_info=True)
                batch_run.status = "failed"
                batch_run.error_message = str(exc)
                batch_run.ended_at = datetime.utcnow()
                update_batch_run(
                    session,
                    batch_run.id,
                    status="failed",
                    error_message=str(exc),
                )
                run_records.append(
                    BatchRunOut(
                        id=batch_run.id,
                        query=item.query,
                        status="failed",
                        lead_count=0,
                        cost_usd=0.0,
                        error_message=str(exc),
                    )
                )
                continue

            cost = metrics.estimated_cost_usd
            lead_count = len(leads)

            # Cap checks
            if total_leads + lead_count > job.cap_max_leads:
                lead_count = job.cap_max_leads - total_leads
                leads = leads[:lead_count]

            if total_cost + cost > job.cap_max_spend_usd:
                # Skip remaining if over spend cap
                batch_run.status = "failed"
                batch_run.error_message = "Spend cap exceeded"
                batch_run.ended_at = datetime.utcnow()
                update_batch_run(
                    session,
                    batch_run.id,
                    status="failed",
                    error_message="Spend cap exceeded",
                )
                run_records.append(
                    BatchRunOut(
                        id=batch_run.id,
                        query=item.query,
                        status="failed",
                        lead_count=0,
                        cost_usd=0.0,
                        error_message="Spend cap exceeded",
                    )
                )
                total_cost += 0.0
                total_leads += 0
                break

            recipe = create_recipe(
                session,
                name=item.recipe_name or item.query,
                query=item.query,
                filters=item.filters,
            )
            run = create_recipe_run(
                session,
                mode="full",
                recipe_id=recipe.id,
                lead_count=lead_count,
                api_cost_breakdown={
                    "input_tokens": metrics.input_tokens,
                    "output_tokens": metrics.output_tokens,
                    "tavily_searches": metrics.tavily_searches,
                    "estimated_cost_usd": cost,
                },
            )
            lead_dicts = [lead.model_dump() for lead in leads]
            save_leads(session, run.id, lead_dicts)

            batch_run.status = "completed"
            batch_run.recipe_id = recipe.id
            batch_run.lead_count = lead_count
            batch_run.cost_usd = cost
            batch_run.ended_at = datetime.utcnow()
            update_batch_run(
                session,
                batch_run.id,
                status="completed",
                recipe_id=recipe.id,
                lead_count=lead_count,
                cost_usd=cost,
            )

            total_cost += cost
            total_leads += lead_count

            run_records.append(
                BatchRunOut(
                    id=batch_run.id,
                    query=item.query,
                    status="completed",
                    lead_count=lead_count,
                    cost_usd=cost,
                    recipe_id=recipe.id,
                    started_at=batch_run.started_at.isoformat() if batch_run.started_at else None,
                    ended_at=batch_run.ended_at.isoformat() if batch_run.ended_at else None,
                )
            )

        final_status = "completed_with_errors" if any(r.status == "failed" for r in run_records) else "completed"
        close_batch_job(session, job.id, status=final_status, total_cost_usd=total_cost, total_leads=total_leads)

        return BatchJobOut(
            id=job.id,
            name=job.name,
            status=final_status,
            cap_queries=job.cap_queries,
            cap_max_leads=job.cap_max_leads,
            cap_max_spend_usd=job.cap_max_spend_usd,
            created_at=job.created_at.isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            ended_at=job.ended_at.isoformat() if job.ended_at else None,
            total_cost_usd=total_cost,
            total_leads=total_leads,
            runs=run_records,
        )


@app.get("/batch", response_model=list[BatchJobOut])
async def list_batch_jobs_endpoint():
    with get_db_session() as session:
        jobs = list_batch_jobs(session)
        result: list[BatchJobOut] = []
        for job in jobs:
            runs = get_batch_runs(session, job.id)
            result.append(
                BatchJobOut(
                    id=job.id,
                    name=job.name,
                    status=job.status,
                    cap_queries=job.cap_queries,
                    cap_max_leads=job.cap_max_leads,
                    cap_max_spend_usd=job.cap_max_spend_usd,
                    created_at=job.created_at.isoformat(),
                    started_at=job.started_at.isoformat() if job.started_at else None,
                    ended_at=job.ended_at.isoformat() if job.ended_at else None,
                    total_cost_usd=job.total_cost_usd,
                    total_leads=job.total_leads,
                    runs=[
                        BatchRunOut(
                            id=r.id,
                            query=r.query,
                            status=r.status,
                            lead_count=r.lead_count,
                            cost_usd=r.cost_usd,
                            error_message=r.error_message,
                            recipe_id=r.recipe_id,
                            started_at=r.started_at.isoformat() if r.started_at else None,
                            ended_at=r.ended_at.isoformat() if r.ended_at else None,
                        )
                        for r in runs
                    ],
                )
            )
        return result


@app.get("/batch/{job_id}", response_model=BatchJobOut)
async def get_batch_job_endpoint(job_id: UUID):
    with get_db_session() as session:
        job = get_batch_job(session, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Batch job not found")
        runs = get_batch_runs(session, job_id)
        return BatchJobOut(
            id=job.id,
            name=job.name,
            status=job.status,
            cap_queries=job.cap_queries,
            cap_max_leads=job.cap_max_leads,
            cap_max_spend_usd=job.cap_max_spend_usd,
            created_at=job.created_at.isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            ended_at=job.ended_at.isoformat() if job.ended_at else None,
            total_cost_usd=job.total_cost_usd,
            total_leads=job.total_leads,
            runs=[
                BatchRunOut(
                    id=r.id,
                    query=r.query,
                    status=r.status,
                    lead_count=r.lead_count,
                    cost_usd=r.cost_usd,
                    error_message=r.error_message,
                    recipe_id=r.recipe_id,
                    started_at=r.started_at.isoformat() if r.started_at else None,
                    ended_at=r.ended_at.isoformat() if r.ended_at else None,
                )
                for r in runs
            ],
        )
