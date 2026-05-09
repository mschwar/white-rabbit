from __future__ import annotations
from pathlib import Path
from datetime import datetime
import sys
import secrets
from typing import Annotated, Any, Optional
from uuid import UUID, uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger("white_rabbit.api")

REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_SRC = REPO_ROOT / "packages" / "core" / "src"
for candidate in (CORE_SRC, REPO_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from core.cost import RunMetrics
from core.models import Lead
from core.orchestrator import scout, OrchestratorError, DEFAULT_MODEL
from core.query_guardrails import QueryGuardrailResult, evaluate_query_guardrails

from api.models import FeedbackLabel

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
    get_sandbox_state,
    get_sandbox_state_for_update,
    reset_sandbox_state,
    record_sandbox_rows,
)

load_dotenv()

INTERNAL_API_TOKEN_HEADER = "x-white-rabbit-internal-token"
INTERNAL_API_TOKEN_ENV = "WR_API_INTERNAL_TOKEN"

# Initialize database on startup (must happen before any endpoint uses it)
init_db()


def _preflight_check():
    """Validate required env vars and vendor connectivity at startup."""
    if "pytest" in sys.modules:
        return

    env = os.environ.get("WR_ENV", "").lower()
    _is_production = env == "production"

    required = [
        "OPENAI_API_KEY",
        "TAVILY_API_KEY",
        "WR_SHARED_PASSWORD",
        "WR_SESSION_SECRET",
        INTERNAL_API_TOKEN_ENV,
    ]
    if _is_production:
        required.append("DATABASE_URL")

    missing = [r for r in required if not os.environ.get(r)]
    if missing:
        raise RuntimeError(f"Missing required env: {', '.join(missing)}")

    # Verify OpenAI connectivity
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        client.models.retrieve(model)
    except Exception as exc:
        resolved_url = base_url or "https://api.openai.com/v1"
        raise RuntimeError(
            f"OpenAI model unreachable: {model} @ {resolved_url} — {exc}"
        ) from exc

    db_url = os.environ.get("DATABASE_URL")
    logger.info("OpenAI: %s @ %s", model, base_url or "https://api.openai.com/v1")
    logger.info("Postgres: %s", db_url or "localhost (default)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _preflight_check()
    yield


app = FastAPI(title="White Rabbit API", lifespan=lifespan)


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
    sandbox_usage: SandboxUsageOut | None = None


class FullResponse(BaseModel):
    run_id: UUID
    leads: list[Lead]
    metrics: RunMetrics
    recipe_id: UUID | None = None
    query_guardrail: QueryGuardrailResult | None = None
    sandbox_usage: SandboxUsageOut | None = None


class FeedbackRequest(BaseModel):
    label: FeedbackLabel


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


class SandboxUsageOut(BaseModel):
    total_queries: int
    total_rows: int
    max_queries: int
    max_rows: int
    remaining_queries: int
    remaining_rows: int
    reset_at: str


class SandboxResetOut(BaseModel):
    sandbox_usage: SandboxUsageOut


SANDBOX_SCOUT_MAX_ROWS_PER_QUERY = 15
SANDBOX_FULL_MAX_ROWS_PER_QUERY = 100
SANDBOX_BATCH_MAX_ROWS_PER_QUERY = 100


def require_internal_api_access(request: Request) -> None:
    expected_token = os.environ.get(INTERNAL_API_TOKEN_ENV)
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail=f"Internal API token is not configured ({INTERNAL_API_TOKEN_ENV}).",
        )

    provided_token = request.headers.get(INTERNAL_API_TOKEN_HEADER)
    if not provided_token or not secrets.compare_digest(provided_token, expected_token):
        raise HTTPException(status_code=401, detail="Missing or invalid internal API token.")


ProtectedApiAccess = Annotated[None, Depends(require_internal_api_access)]


def _sandbox_usage_out(session) -> SandboxUsageOut:
    state = get_sandbox_state(session)
    return SandboxUsageOut(
        total_queries=state.total_queries,
        total_rows=state.total_rows,
        max_queries=state.max_queries,
        max_rows=state.max_rows,
        remaining_queries=max(0, state.max_queries - state.total_queries),
        remaining_rows=max(0, state.max_rows - state.total_rows),
        reset_at=state.reset_at.isoformat(),
    )


def _sandbox_reserve_query_or_429(session, planned_rows: int) -> SandboxUsageOut:
    state = get_sandbox_state_for_update(session)
    remaining_queries = state.max_queries - state.total_queries
    remaining_rows = state.max_rows - state.total_rows
    if remaining_queries <= 0:
        raise HTTPException(
            status_code=429,
            detail={
                'error': 'Sandbox query cap reached. Reset the sandbox before running more queries.',
                'sandbox_usage': _sandbox_usage_out(session).model_dump(),
            },
        )
    if remaining_rows < planned_rows:
        raise HTTPException(
            status_code=429,
            detail={
                'error': 'Sandbox row cap reached. Reset the sandbox before running another lead search.',
                'sandbox_usage': _sandbox_usage_out(session).model_dump(),
            },
        )

    state.total_queries += 1
    state.updated_at = datetime.utcnow()
    return _sandbox_usage_out(session)
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
async def run_scout(request: ScoutRequest, _: ProtectedApiAccess):
    guardrail = _query_guardrail_or_422(request.query)
    with get_db_session() as session:
        sandbox_usage = _sandbox_reserve_query_or_429(session, SANDBOX_SCOUT_MAX_ROWS_PER_QUERY)
    try:
        leads, metrics = await scout(request.query, filters=request.filters)
        with get_db_session() as session:
            record_sandbox_rows(session, len(leads))
            sandbox_usage = _sandbox_usage_out(session)
        return ScoutResponse(
            leads=leads,
            metrics=metrics,
            query_guardrail=guardrail if guardrail.status != 'clear' else None,
            sandbox_usage=sandbox_usage,
        )
    except OrchestratorError as exc:
        import logging
        logging.getLogger("white_rabbit.api").error("Orchestrator error: %s", exc, exc_info=True)
        raise HTTPException(status_code=503, detail=_orchestrator_error_response(exc))
    except Exception as exc:
        import logging
        logging.getLogger("white_rabbit.api").error("Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=_internal_error_response(exc))


def _resolve_error_code(exc: OrchestratorError) -> str:
    msg = str(exc).lower()
    if "tavily" in msg:
        return "tavily_failed"
    if "openai" in msg or "llm" in msg:
        return "openai_failed"
    if "parse" in msg or "json" in msg or "validation" in msg:
        return "llm_parse_failed"
    return "orchestrator_error"


def _orchestrator_error_response(exc: OrchestratorError) -> dict:
    return {
        "error_code": _resolve_error_code(exc),
        "message": str(exc),
        "request_id": str(uuid4()),
    }


def _internal_error_response(exc: Exception) -> dict:
    return {
        "error_code": "internal_error",
        "message": "An unexpected error occurred.",
        "request_id": str(uuid4()),
    }


@app.post("/full", response_model=FullResponse)
async def run_full(request: FullRequest, _: ProtectedApiAccess):
    """Run a Full query: produces a stored recipe and recipe_run."""
    guardrail = _query_guardrail_or_422(request.query)
    with get_db_session() as session:
        sandbox_usage = _sandbox_reserve_query_or_429(session, SANDBOX_FULL_MAX_ROWS_PER_QUERY)
    try:
        leads, metrics = await scout(request.query, filters=request.filters, max_leads=100)
        with get_db_session() as session:
            record_sandbox_rows(session, len(leads))
            sandbox_usage = _sandbox_usage_out(session)
    except OrchestratorError as exc:
        import logging
        logging.getLogger("white_rabbit.api").error("Orchestrator error: %s", exc, exc_info=True)
        raise HTTPException(status_code=503, detail=_orchestrator_error_response(exc))
    except Exception as exc:
        import logging
        logging.getLogger("white_rabbit.api").error("Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=_internal_error_response(exc))

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
        db_leads = save_leads(session, run.id, lead_dicts)

        # Inject persisted lead IDs back into the response leads
        for lead, db_lead in zip(leads, db_leads):
            lead.id = str(db_lead.id)

        return FullResponse(
            run_id=run.id,
            leads=leads,
            metrics=metrics,
            recipe_id=recipe.id,
            query_guardrail=guardrail if guardrail.status != 'clear' else None,
            sandbox_usage=sandbox_usage,
        )


@app.get("/recipes", response_model=list[RecipeOut])
async def list_recipes(_: ProtectedApiAccess):
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
async def list_recipe_runs(recipe_id: UUID, _: ProtectedApiAccess):
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
async def recipe_scoreboard(recipe_id: UUID, _: ProtectedApiAccess):
    with get_db_session() as session:
        scoreboard = get_recipe_scoreboard(session, recipe_id)
        if not scoreboard:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return RecipeScoreboardOut(**scoreboard)


@app.get("/sandbox", response_model=SandboxUsageOut)
async def get_sandbox_usage(_: ProtectedApiAccess):
    with get_db_session() as session:
        return _sandbox_usage_out(session)


@app.post("/sandbox/reset", response_model=SandboxResetOut)
async def reset_sandbox(_: ProtectedApiAccess):
    with get_db_session() as session:
        state = reset_sandbox_state(session)
        return SandboxResetOut(sandbox_usage=_sandbox_usage_out(session))


@app.post("/leads/{lead_id}/feedback")
async def submit_feedback(lead_id: UUID, request: FeedbackRequest, _: ProtectedApiAccess):
    with get_db_session() as session:
        add_lead_feedback(session, lead_id, request.label)
        return {"status": "ok"}


@app.post("/runs/{run_id}/close")
async def close_run(run_id: UUID, _: ProtectedApiAccess, operator_minutes: float | None = None):
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
async def run_batch(request: BatchRequest, _: ProtectedApiAccess):
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
                _sandbox_reserve_query_or_429(
                    session,
                    min(job.cap_max_leads, SANDBOX_BATCH_MAX_ROWS_PER_QUERY),
                )
                leads, metrics = await scout(
                    item.query,
                    filters=item.filters,
                    max_leads=min(job.cap_max_leads, SANDBOX_BATCH_MAX_ROWS_PER_QUERY),
                )
            except HTTPException as exc:
                batch_run.status = "failed"
                batch_run.error_message = exc.detail["error"] if isinstance(exc.detail, dict) and "error" in exc.detail else str(exc.detail)
                batch_run.ended_at = datetime.utcnow()
                update_batch_run(
                    session,
                    batch_run.id,
                    status="failed",
                    error_message=batch_run.error_message,
                )
                run_records.append(
                    BatchRunOut(
                        id=batch_run.id,
                        query=item.query,
                        status="failed",
                        lead_count=0,
                        cost_usd=0.0,
                        error_message=batch_run.error_message,
                    )
                )
                break
            except OrchestratorError as exc:
                import logging
                logging.getLogger("white_rabbit.api").error("Batch orchestrator error: %s", exc, exc_info=True)
                err = _orchestrator_error_response(exc)
                batch_run.status = "failed"
                batch_run.error_message = err["message"]
                batch_run.ended_at = datetime.utcnow()
                update_batch_run(
                    session,
                    batch_run.id,
                    status="failed",
                    error_message=err["message"],
                )
                run_records.append(
                    BatchRunOut(
                        id=batch_run.id,
                        query=item.query,
                        status="failed",
                        lead_count=0,
                        cost_usd=0.0,
                        error_message=err["message"],
                    )
                )
                continue
            except Exception as exc:
                import logging
                logging.getLogger("white_rabbit.api").error("Batch unexpected error: %s", exc, exc_info=True)
                err = _internal_error_response(exc)
                batch_run.status = "failed"
                batch_run.error_message = err["message"]
                batch_run.ended_at = datetime.utcnow()
                update_batch_run(
                    session,
                    batch_run.id,
                    status="failed",
                    error_message=err["message"],
                )
                run_records.append(
                    BatchRunOut(
                        id=batch_run.id,
                        query=item.query,
                        status="failed",
                        lead_count=0,
                        cost_usd=0.0,
                        error_message=err["message"],
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
            record_sandbox_rows(session, lead_count)

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
async def list_batch_jobs_endpoint(_: ProtectedApiAccess):
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
async def get_batch_job_endpoint(job_id: UUID, _: ProtectedApiAccess):
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
