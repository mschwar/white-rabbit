import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any

# The API uses SQLAlchemy's pure-Python path; optional C extensions slow local startup.
os.environ.setdefault("DISABLE_SQLALCHEMY_CEXT_RUNTIME", "1")

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class FeedbackLabel(str, Enum):
    USABLE = "usable"
    WRONG_PERSONA = "wrong_persona"
    BAD_SOURCE = "bad_source"
    BAD_CONTACT = "bad_contact"
    DUPLICATE = "duplicate"


class CorrectionLabel(str, Enum):
    USABLE = "usable"
    WRONG_PERSONA = "wrong_persona"
    BAD_SOURCE = "bad_source"
    BAD_CONTACT = "bad_contact"
    DUPLICATE = "duplicate"
    CORRECTED_FIELD = "corrected_field"


class CorrectionField(str, Enum):
    NAME = "name"
    TITLE = "title"
    ORGANIZATION = "organization"
    EMAIL = "email"
    PHONE = "phone"
    SOURCE = "source"


class Recipe(Base):
    __tablename__ = "recipe"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    query = Column(Text, nullable=False)
    filters = Column(JSON, default=dict)
    source_mix = Column(JSON, default=dict)
    weights = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class RecipeRun(Base):
    __tablename__ = "recipe_run"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(Uuid(as_uuid=True), ForeignKey("recipe.id", ondelete="CASCADE"), nullable=True)
    mode = Column(String(10), nullable=False)  # 'scout' or 'full'
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    operator_minutes = Column(Float, nullable=True)
    api_cost_breakdown = Column(JSON, default=dict)
    lead_count = Column(Integer, nullable=False, default=0)


class Lead(Base):
    __tablename__ = "lead"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(Uuid(as_uuid=True), ForeignKey("recipe_run.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSON, nullable=False)
    fit_score = Column(Float, nullable=True)
    evidence_score = Column(Float, nullable=True)
    contact_score = Column(Float, nullable=True)
    gate_passed = Column(Boolean, nullable=True)
    rank = Column(Integer, nullable=True)


class LeadFeedback(Base):
    __tablename__ = "lead_feedback"

    __table_args__ = (
        CheckConstraint(
            "label IN ('usable', 'wrong_persona', 'bad_source', 'bad_contact', 'duplicate')",
            name="ck_lead_feedback_label",
        ),
    )

    lead_id = Column(Uuid(as_uuid=True), ForeignKey("lead.id", ondelete="CASCADE"), primary_key=True)
    label = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class LeadCorrection(Base):
    __tablename__ = "lead_correction"

    __table_args__ = (
        CheckConstraint(
            "label IN ('usable', 'wrong_persona', 'bad_source', 'bad_contact', 'duplicate', 'corrected_field')",
            name="ck_lead_correction_label",
        ),
        CheckConstraint(
            "field_name IN ('name', 'title', 'organization', 'email', 'phone', 'source')",
            name="ck_lead_correction_field_name",
        ),
    )

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Store synthetic fixture IDs and real UUID strings alike.
    lead_id = Column(Text, nullable=False)
    run_id = Column(Text, nullable=False)
    query = Column(Text, nullable=False)
    label = Column(String(20), nullable=False)
    field_name = Column(String(32), nullable=False)
    previous_value = Column(Text, nullable=True)
    corrected_value = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class BatchJob(Base):
    __tablename__ = "batch_job"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, running, completed, failed
    cap_queries = Column(Integer, nullable=False, default=10)
    cap_max_leads = Column(Integer, nullable=False, default=1000)
    cap_max_spend_usd = Column(Float, nullable=False, default=10.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    total_cost_usd = Column(Float, nullable=False, default=0.0)
    total_leads = Column(Integer, nullable=False, default=0)


class BatchRun(Base):
    __tablename__ = "batch_run"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_job_id = Column(Uuid(as_uuid=True), ForeignKey("batch_job.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(Uuid(as_uuid=True), ForeignKey("recipe.id", ondelete="SET NULL"), nullable=True)
    query = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    lead_count = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Float, nullable=False, default=0.0)
    error_message = Column(Text, nullable=True)


class SandboxState(Base):
    __tablename__ = "sandbox_state"

    id = Column(Integer, primary_key=True)
    total_queries = Column(Integer, nullable=False, default=0)
    total_rows = Column(Integer, nullable=False, default=0)
    max_queries = Column(Integer, nullable=False, default=10)
    max_rows = Column(Integer, nullable=False, default=1000)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    reset_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


def get_engine(database_url: str | None = None):
    url = database_url or os.environ.get("DATABASE_URL")
    if not url:
        if os.environ.get("WR_ENV") == "production":
            raise RuntimeError("DATABASE_URL must be set in production")
        url = "postgresql://white_rabbit:***@localhost:5432/white_rabbit"
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)


def get_session_maker(engine):
    return sessionmaker(bind=engine)
