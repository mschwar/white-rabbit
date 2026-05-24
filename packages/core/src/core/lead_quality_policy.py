from __future__ import annotations

from typing import Any, Literal

from .models import Candidate, Lead

ReadyBlocker = Literal[
    "no_contact_source",
    "no_validated_domain_pattern",
    "source_inaccessible",
    "title_unsupported",
    "persona_mismatch",
    "organization_only",
    "conflicting_evidence",
    "privacy_refusal",
]

SUPPORTED_FIELD_STATUS = "supported"
READY_CONTACT_STATUSES = {"verified_found", "deduced_with_pattern_evidence"}
READY_SCORE_THRESHOLD = 0.6
READY_PERSONA_FIELDS = ("name", "title", "organization")
READY_SOURCE_FIELDS = ("source",)
READY_FIELD_SUPPORT = (*READY_PERSONA_FIELDS, *READY_SOURCE_FIELDS)


def validation_status(candidate: Candidate, field_name: str, *, default: str = "unsupported") -> str:
    validation = getattr(candidate, "validation", None)
    record = getattr(validation, field_name, None)
    return getattr(record, "status", default) or default


def validation_note(candidate: Candidate, field_name: str) -> str:
    validation = getattr(candidate, "validation", None)
    record = getattr(validation, field_name, None)
    return getattr(record, "notes", "") or ""


def lead_has_persona_support(candidate: Candidate) -> bool:
    return isinstance(candidate, Lead) and all(
        validation_status(candidate, field_name) == SUPPORTED_FIELD_STATUS for field_name in READY_PERSONA_FIELDS
    )


def lead_has_source_support(candidate: Candidate) -> bool:
    return isinstance(candidate, Lead) and all(
        validation_status(candidate, field_name) == SUPPORTED_FIELD_STATUS for field_name in READY_SOURCE_FIELDS
    )


def lead_has_contact_support(candidate: Candidate) -> bool:
    return isinstance(candidate, Lead) and validation_status(candidate, "email") in READY_CONTACT_STATUSES


def lead_has_ready_scores(candidate: Candidate, *, threshold: float = READY_SCORE_THRESHOLD) -> bool:
    if not isinstance(candidate, Lead):
        return False
    return (
        candidate.fit_score >= threshold
        and candidate.evidence_score >= threshold
        and candidate.contact_score >= threshold
    )


def lead_is_ready_eligible(candidate: Candidate, *, threshold: float = READY_SCORE_THRESHOLD) -> bool:
    if not isinstance(candidate, Lead) or candidate.candidate_category != "person_lead":
        return False
    return (
        lead_has_persona_support(candidate)
        and lead_has_source_support(candidate)
        and lead_has_contact_support(candidate)
        and lead_has_ready_scores(candidate, threshold=threshold)
    )


def _record_notes(candidate: Candidate, field_name: str) -> str:
    return validation_note(candidate, field_name) or ""


def ready_blocker_for_candidate(candidate: Candidate) -> ReadyBlocker | None:
    if lead_is_ready_eligible(candidate):
        return None

    reason = getattr(candidate, "primary_filter_reason", "") or ""
    reason_lower = reason.lower()
    if "conflict" in reason_lower or "contradict" in reason_lower:
        return "conflicting_evidence"

    if candidate.candidate_category == "organization_only":
        return "organization_only"

    if validation_status(candidate, "source") in {"failed", "missing"}:
        return "source_inaccessible"

    if isinstance(candidate, Lead):
        if validation_status(candidate, "title") in {"unsupported", "missing", "failed"}:
            return "title_unsupported"
        if (
            validation_status(candidate, "name") == "failed"
            or validation_status(candidate, "organization") == "failed"
            or "persona" in reason_lower
        ):
            return "persona_mismatch"
        if validation_status(candidate, "email") == "missing":
            return "no_contact_source"
        if validation_status(candidate, "email") == "unsupported":
            return "no_validated_domain_pattern"
        if validation_status(candidate, "email") == "failed":
            return "conflicting_evidence"

    if candidate.candidate_category == "not_found":
        return "no_contact_source"

    if candidate.candidate_category == "failed":
        notes = " ".join(
            _record_notes(candidate, field_name)
            for field_name in ("source", "name", "title", "organization", "email")
        ).lower()
        if "http_status=403" in notes or "http_status=404" in notes or "fetch_error" in notes:
            return "source_inaccessible"
        if "title" in reason_lower:
            return "title_unsupported"
        return "conflicting_evidence"

    return None


def candidate_identity(candidate: Candidate) -> dict[str, Any]:
    return {
        "candidate_category": candidate.candidate_category,
        "tier": getattr(candidate, "tier", None),
        "name": getattr(candidate, "name", None),
        "title": getattr(candidate, "title", None),
        "organization": getattr(candidate, "organization", None),
        "searched_target": getattr(candidate, "searched_target", None),
    }
