from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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
    "president",
    "administrator",
    "founder",
    "owner",
)
_ORGANIZATION_NAME_PATTERNS = (
    r"\binc\.?\b",
    r"\bcorp\.?\b",
    r"\bcorporation\b",
    r"\bcompany\b",
    r"\bco\.?\b",
    r"\bllc\b",
    r"\bltd\b",
    r"\blimited\b",
    r"\bgroup\b",
    r"\bholdings\b",
    r"\bsystems\b",
    r"\bsolutions\b",
    r"\bservices\b",
    r"\bpublic schools\b",
    r"\bschool district\b",
    r"\bdistrict\b",
    r"\bhospital\b",
    r"\bclinic\b",
    r"\buniversity\b",
    r"\bcollege\b",
    r"\bacademy\b",
    r"\bdepartment\b",
    r"\bagency\b",
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
FieldValidationStatus = Literal["supported", "unsupported", "missing", "failed"]
ContactStatus = Literal[
    "verified_found",
    "deduced_with_pattern_evidence",
    "missing",
    "failed",
    "unsupported",
]
OutputTier = Literal["high_trust_usable", "review", "organization_only", "not_found", "failed"]

_LEGACY_CONTACT_STATUS_ALIASES = {
    "Found": "verified_found",
    "Deduced": "deduced_with_pattern_evidence",
    "Missing": "missing",
}


def _has_text(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _looks_like_organization(value: str) -> bool:
    lowered = value.lower()
    return any(re.search(pattern, lowered) for pattern in _ORGANIZATION_NAME_PATTERNS)


class FieldValidationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: FieldValidationStatus = Field(
        default="unsupported",
        description="Whether this field is supported by evidence.",
    )
    source_url: str | None = Field(default=None, description="Source URL supporting the field.")
    evidence_snippet: str | None = Field(
        default=None,
        description="Supporting excerpt or extracted text reference.",
    )
    checked_at: str | None = Field(
        default=None,
        description="ISO-8601 timestamp when the validation was checked.",
    )
    notes: str = Field(default="", description="Validation notes.")


class ContactValidationRecord(FieldValidationRecord):
    status: ContactStatus = Field(
        default="unsupported",
        description="Whether this contact field is verified_found, deduced_with_pattern_evidence, missing, failed, or unsupported.",
    )


def _unsupported_validation_record() -> FieldValidationRecord:
    return FieldValidationRecord(status="unsupported")


def _unsupported_contact_validation_record() -> ContactValidationRecord:
    return ContactValidationRecord(status="unsupported")


class CandidateValidation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: FieldValidationRecord = Field(default_factory=_unsupported_validation_record)
    title: FieldValidationRecord = Field(default_factory=_unsupported_validation_record)
    organization: FieldValidationRecord = Field(default_factory=_unsupported_validation_record)
    email: ContactValidationRecord = Field(default_factory=_unsupported_contact_validation_record)
    phone: ContactValidationRecord = Field(default_factory=_unsupported_contact_validation_record)
    source: FieldValidationRecord = Field(default_factory=_unsupported_validation_record)


class CandidateBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None, description="Database lead ID (set after persistence)")
    candidate_category: Literal["person_lead", "organization_only", "not_found", "failed"] = Field(
        description="Explicit row category."
    )
    tier: OutputTier = Field(
        default="review",
        description="Server-computed output tier for operator review and export ordering.",
    )
    primary_filter_reason: str = Field(
        default="Tier has not been computed yet.",
        description="Server-computed primary reason the row is or is not actionable.",
    )
    validation: CandidateValidation = Field(
        default_factory=CandidateValidation,
        description="Field-level validation records for the candidate.",
    )


class Lead(CandidateBase):
    candidate_category: Literal["person_lead"] = Field(
        default="person_lead",
        description="Validated person lead row.",
    )
    name: str = Field(description="Real person's first and last name; omit the lead if unknown")
    title: str = Field(description="Job title")
    organization: str = Field(description="Organization, district, agency, or company name")
    email: str = Field(description="Professional email address, or blank if unavailable")
    email_status: ContactStatus = Field(
        default="unsupported",
        description="Email contact status: verified_found, deduced_with_pattern_evidence, missing, failed, or unsupported",
    )
    phone: str = Field(default="", description="Professional phone number, or blank if unavailable")
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
    fit_score: float = Field(ge=0, le=1, description="Query-fit signal only; not a CRM-readiness score.")
    evidence_score: float = Field(
        ge=0,
        le=1,
        description="Server-capped evidence-support signal derived from field/source validation.",
    )
    contact_score: float = Field(
        ge=0,
        le=1,
        description="Server-capped contact-readiness signal derived from contact validation.",
    )
    gate_passed: bool = Field(description="True if the server-computed evidence gate cleared the thresholds")
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

        if _looks_like_organization(normalized):
            raise ValueError("Lead.name must be a person's name, not an organization.")

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

    @field_validator("email_status", mode="before")
    @classmethod
    def normalize_email_status(cls, value: str) -> str:
        if isinstance(value, str):
            return _LEGACY_CONTACT_STATUS_ALIASES.get(value, value)
        return value

    @model_validator(mode="after")
    def validate_person_candidate(self) -> Lead:
        for field_name in ("name", "title", "organization", "source_url", "why_target", "icebreaker", "explanation"):
            if not _has_text(getattr(self, field_name)):
                raise ValueError(f"Lead.{field_name} is required for person_lead candidates.")
        return self


class OrganizationOnlyCandidate(CandidateBase):
    candidate_category: Literal["organization_only"] = Field(
        default="organization_only",
        description="Organization-only row with no validated person lead.",
    )
    organization: str = Field(description="Account or company that was found")
    source_url: str | None = Field(default=None, description="Source URL supporting the organization-only row")
    explanation: str = Field(
        default="Organization was found, but no usable person was validated.",
        description="Why this row remains organization-only.",
    )

    @model_validator(mode="before")
    @classmethod
    def default_tier(cls, data: object) -> object:
        if isinstance(data, dict):
            data.setdefault("tier", "organization_only")
            data.setdefault("primary_filter_reason", "Organization was found, but no validated person was ready.")
        return data

    @model_validator(mode="after")
    def validate_organization_only_candidate(self) -> OrganizationOnlyCandidate:
        if not _has_text(self.organization):
            raise ValueError("OrganizationOnlyCandidate.organization is required.")
        return self


class NotFoundCandidate(CandidateBase):
    candidate_category: Literal["not_found"] = Field(
        default="not_found",
        description="Search target was found to have no acceptable contact.",
    )
    searched_target: str = Field(description="Target account or persona that was searched")
    organization: str | None = Field(default=None, description="Optional account or organization name")
    source_url: str | None = Field(default=None, description="Source URL supporting the not-found outcome")
    explanation: str = Field(
        default="No acceptable contact was found.",
        description="Why the search did not produce a usable person lead.",
    )

    @model_validator(mode="before")
    @classmethod
    def default_tier(cls, data: object) -> object:
        if isinstance(data, dict):
            data.setdefault("tier", "not_found")
            data.setdefault("primary_filter_reason", "Target was searched, but no acceptable contact was found.")
        return data

    @model_validator(mode="after")
    def validate_not_found_candidate(self) -> NotFoundCandidate:
        if not _has_text(self.searched_target):
            raise ValueError("NotFoundCandidate.searched_target is required.")
        return self


class FailedCandidate(CandidateBase):
    candidate_category: Literal["failed"] = Field(
        default="failed",
        description="Row was rejected because evidence contradicted or did not support it.",
    )
    searched_target: str = Field(description="Target account or persona that was searched")
    failure_reason: str = Field(description="Why the candidate was rejected")
    organization: str | None = Field(default=None, description="Optional account or organization name")
    source_url: str | None = Field(default=None, description="Source URL supporting the failure outcome")
    explanation: str = Field(
        default="The candidate could not be trusted.",
        description="Human-readable explanation for the failure outcome.",
    )

    @model_validator(mode="before")
    @classmethod
    def default_tier(cls, data: object) -> object:
        if isinstance(data, dict):
            data.setdefault("tier", "failed")
            data.setdefault("primary_filter_reason", "Evidence contradicted or failed to support this row.")
        return data

    @model_validator(mode="after")
    def validate_failed_candidate(self) -> FailedCandidate:
        if not _has_text(self.searched_target):
            raise ValueError("FailedCandidate.searched_target is required.")
        if not _has_text(self.failure_reason):
            raise ValueError("FailedCandidate.failure_reason is required.")
        return self


Candidate = Lead | OrganizationOnlyCandidate | NotFoundCandidate | FailedCandidate


class LeadList(BaseModel):
    leads: list[Candidate] = Field(description="List of extracted candidates")
