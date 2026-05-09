from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


_ROLE_WORDS = (
    "director",
    "manager",
    "officer",
    "vp",
    "vice president",
    "chief",
    "executive",
    "coordinator",
    "supervisor",
    "head of",
    "principal",
    "lead",
)
_EMAIL_PLACEHOLDER_PREFIXES = (
    "not_available@",
    "noreply@",
    "no-reply@",
    "placeholder@",
    "email@",
    "info@",
    "admin@",
    "contact@",
)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Lead(BaseModel):
    id: str | None = Field(default=None, description="Database lead ID (set after persistence)")
    name: str = Field(description="Real person's first and last name; omit the lead if unknown")
    title: str = Field(description="Job title")
    organization: str = Field(description="Organization, district, agency, or company name")
    email: str = Field(description="Professional email address, or blank if unavailable")
    email_status: Literal["Found", "Deduced", "Missing"] = Field(
        description="Email evidence status: Found, Deduced, or Missing"
    )
    source_url: str = Field(description="Best source URL supporting the contact, title, or email")
    confidence: float = Field(
        ge=0,
        le=1,
        description="DEPRECATED: Confidence score from 0.0 to 1.0 based on source strength. Use scores instead.",
    )
    why_target: str = Field(description="1 sentence on why this role/organization fits the user's stated query intent")
    icebreaker: str = Field(
        description="A specific 1-sentence cold email opener referencing their job title, their organization, and one concrete reason their work aligns with the query intent. No template language."
    )

    # New Sprint 1 fields
    fit_score: float = Field(ge=0, le=1, description="Match between person/org and target ICP")
    evidence_score: float = Field(ge=0, le=1, description="Strength and freshness of supporting sources")
    contact_score: float = Field(ge=0, le=1, description="Usability of email/phone/title information")
    gate_passed: bool = Field(description="True if all three scores cleared their thresholds")
    explanation: str = Field(description="Human-readable rationale for ranking")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Lead.name must be a real person's first and last name.")

        normalized = value.strip()
        if len(normalized.split()) < 2:
            raise ValueError("Lead.name must include at least a first and last name.")

        lowered = normalized.lower()
        for role_word in _ROLE_WORDS:
            if role_word in {"head of", "vice president"}:
                if role_word in lowered:
                    raise ValueError("Lead.name must be a person's name, not a role or title.")
                continue

            if re.search(rf"\b{re.escape(role_word)}\b", lowered):
                raise ValueError("Lead.name must be a person's name, not a role or title.")

        return normalized

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if value == "":
            return value

        lowered = value.lower()
        if any(lowered.startswith(prefix) for prefix in _EMAIL_PLACEHOLDER_PREFIXES):
            raise ValueError("Lead.email must not be a placeholder address.")

        if not _EMAIL_RE.match(value):
            raise ValueError("Lead.email must be a valid email address or blank.")

        return value


class LeadList(BaseModel):
    leads: list[Lead] = Field(description="List of extracted leads")
