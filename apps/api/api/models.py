import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Recipe(Base):
    __tablename__ = "recipe"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    query = Column(Text, nullable=False)
    filters = Column(JSON, default=dict)
    source_mix = Column(JSON, default=dict)
    weights = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class RecipeRun(Base):
    __tablename__ = "recipe_run"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipe.id", ondelete="CASCADE"), nullable=True)
    mode = Column(String(10), nullable=False)  # 'scout' or 'full'
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    operator_minutes = Column(Float, nullable=True)
    api_cost_breakdown = Column(JSON, default=dict)
    lead_count = Column(Integer, nullable=False, default=0)


class Lead(Base):
    __tablename__ = "lead"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("recipe_run.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSON, nullable=False)
    fit_score = Column(Float, nullable=True)
    evidence_score = Column(Float, nullable=True)
    contact_score = Column(Float, nullable=True)
    gate_passed = Column(Boolean, nullable=True)
    rank = Column(Integer, nullable=True)


class LeadFeedback(Base):
    __tablename__ = "lead_feedback"

    lead_id = Column(UUID(as_uuid=True), ForeignKey("lead.id", ondelete="CASCADE"), primary_key=True)
    label = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


def get_engine(database_url: str | None = None):
    url = database_url or "postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit"
    return create_engine(url)


def get_session_maker(engine):
    return sessionmaker(bind=engine)
