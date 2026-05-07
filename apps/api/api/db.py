from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator
from uuid import UUID

from sqlalchemy.orm import Session

from api.models import (
    Base,
    Lead,
    LeadFeedback,
    Recipe,
    RecipeRun,
    get_engine,
    get_session_maker,
)

_engine = None
_session_maker = None


def init_db(database_url: str | None = None):
    global _engine, _session_maker
    _engine = get_engine(database_url)
    _session_maker = get_session_maker(_engine)
    Base.metadata.create_all(_engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    if _session_maker is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    session = _session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_recipe(
    session: Session,
    name: str,
    query: str,
    filters: dict[str, Any] | None = None,
    source_mix: dict[str, Any] | None = None,
    weights: dict[str, Any] | None = None,
) -> Recipe:
    recipe = Recipe(
        name=name,
        query=query,
        filters=filters or {},
        source_mix=source_mix or {},
        weights=weights or {},
    )
    session.add(recipe)
    session.flush()
    return recipe


def create_recipe_run(
    session: Session,
    mode: str,
    recipe_id: UUID | None = None,
    lead_count: int = 0,
    api_cost_breakdown: dict[str, Any] | None = None,
) -> RecipeRun:
    run = RecipeRun(
        recipe_id=recipe_id,
        mode=mode,
        lead_count=lead_count,
        api_cost_breakdown=api_cost_breakdown or {},
    )
    session.add(run)
    session.flush()
    return run


def save_leads(
    session: Session,
    run_id: UUID,
    leads: list[dict[str, Any]],
) -> list[Lead]:
    db_leads = []
    for rank, lead_data in enumerate(leads, start=1):
        db_lead = Lead(
            run_id=run_id,
            data=lead_data,
            fit_score=lead_data.get("fit_score"),
            evidence_score=lead_data.get("evidence_score"),
            contact_score=lead_data.get("contact_score"),
            gate_passed=lead_data.get("gate_passed"),
            rank=rank,
        )
        session.add(db_lead)
        db_leads.append(db_lead)
    session.flush()
    return db_leads


def add_lead_feedback(
    session: Session,
    lead_id: UUID,
    label: str,
) -> LeadFeedback:
    feedback = LeadFeedback(lead_id=lead_id, label=label)
    session.add(feedback)
    session.flush()
    return feedback


def get_recipes(session: Session) -> list[Recipe]:
    return session.query(Recipe).order_by(Recipe.created_at.desc()).all()


def get_recipe_by_id(session: Session, recipe_id: UUID) -> Recipe | None:
    return session.query(Recipe).filter(Recipe.id == recipe_id).first()


def get_recipe_runs(session: Session, recipe_id: UUID | None = None) -> list[RecipeRun]:
    query = session.query(RecipeRun)
    if recipe_id:
        query = query.filter(RecipeRun.recipe_id == recipe_id)
    return query.order_by(RecipeRun.started_at.desc()).all()


def get_leads_for_run(session: Session, run_id: UUID) -> list[Lead]:
    return session.query(Lead).filter(Lead.run_id == run_id).order_by(Lead.rank).all()


def close_recipe_run(
    session: Session,
    run_id: UUID,
    operator_minutes: float | None = None,
) -> RecipeRun | None:
    run = session.query(RecipeRun).filter(RecipeRun.id == run_id).first()
    if run:
        run.ended_at = datetime.utcnow()
        run.operator_minutes = operator_minutes
    return run


def get_recipe_scoreboard(session: Session, recipe_id: UUID) -> dict[str, Any] | None:
    recipe = get_recipe_by_id(session, recipe_id)
    if recipe is None:
        return None

    runs = get_recipe_runs(session, recipe_id=recipe_id)
    total_api_cost_usd = 0.0
    total_operator_minutes = 0.0
    total_leads_returned = 0
    usable_lead_count = 0
    feedback_counts: dict[str, int] = {}

    for run in runs:
        total_leads_returned += run.lead_count or 0
        if run.operator_minutes is not None:
            total_operator_minutes += run.operator_minutes
        total_api_cost_usd += float((run.api_cost_breakdown or {}).get("estimated_cost_usd", 0) or 0)

        for lead in get_leads_for_run(session, run.id):
            feedback = session.query(LeadFeedback).filter(LeadFeedback.lead_id == lead.id).first()
            if feedback is None:
                continue

            feedback_counts[feedback.label] = feedback_counts.get(feedback.label, 0) + 1
            if feedback.label == "usable":
                usable_lead_count += 1

    return {
        "recipe_id": recipe.id,
        "recipe_name": recipe.name,
        "total_api_cost_usd": total_api_cost_usd,
        "total_leads_returned": total_leads_returned,
        "usable_lead_count": usable_lead_count,
        "total_operator_minutes": total_operator_minutes,
        "minutes_per_usable_lead": (total_operator_minutes / usable_lead_count) if usable_lead_count else None,
        "api_cost_per_usable_lead": (total_api_cost_usd / usable_lead_count) if usable_lead_count else None,
        "feedback_counts": feedback_counts,
    }
