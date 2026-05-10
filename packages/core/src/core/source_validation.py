from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape
from typing import Any

import httpx

from .models import Candidate, CandidateValidation, ContactValidationRecord, FieldValidationRecord

SOURCE_VALIDATION_TIMEOUT_SECONDS = 10.0
_SUPPORTED_SOURCE_FIELD_STATUSES = {"supported", "verified_found"}

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _normalize_source_text(text: str) -> str:
    cleaned = _HTML_TAG_RE.sub(" ", unescape(text))
    return _WHITESPACE_RE.sub(" ", cleaned).strip()


def _phrase_pattern(value: str) -> re.Pattern[str]:
    parts = [re.escape(part) for part in value.strip().split() if part]
    if not parts:
        return re.compile(r"(?!x)x")
    return re.compile(r"\s+".join(parts), re.IGNORECASE)


def _find_evidence_snippet(source_text: str, field_value: str, window: int = 80) -> str | None:
    match = _phrase_pattern(field_value).search(source_text)
    if not match:
        return None

    start = max(0, match.start() - window)
    end = min(len(source_text), match.end() + window)
    snippet = source_text[start:end].strip()
    if start > 0:
        snippet = f"...{snippet}"
    if end < len(source_text):
        snippet = f"{snippet}..."
    return snippet


def _field_record_for_missing_source(
    field_name: str,
    field_value: Any,
    *,
    checked_at: str,
) -> FieldValidationRecord:
    if _has_text(field_value):
        return FieldValidationRecord(
            status="failed",
            source_url=None,
            checked_at=checked_at,
            notes=f"Could not validate {field_name} because source_url was not provided.",
        )

    return FieldValidationRecord(
        status="missing",
        source_url=None,
        checked_at=checked_at,
        notes=f"{field_name} is not present on the candidate.",
    )


def _contact_record_for_missing_source(
    field_name: str,
    field_value: Any,
    *,
    checked_at: str,
) -> ContactValidationRecord:
    if _has_text(field_value):
        return ContactValidationRecord(
            status="failed",
            source_url=None,
            checked_at=checked_at,
            notes=f"Could not validate {field_name} because source_url was not provided.",
        )

    return ContactValidationRecord(
        status="missing",
        source_url=None,
        checked_at=checked_at,
        notes=f"{field_name} is not present on the candidate.",
    )


def _field_record_for_access_failure(
    field_name: str,
    field_value: Any,
    *,
    source_url: str,
    checked_at: str,
    note: str,
) -> FieldValidationRecord:
    if _has_text(field_value):
        status = "failed"
        field_note = note
    else:
        status = "missing"
        field_note = f"{field_name} is not present on the candidate. {note}"

    return FieldValidationRecord(
        status=status,
        source_url=source_url,
        checked_at=checked_at,
        notes=field_note,
    )


def _contact_record_for_access_failure(
    field_name: str,
    field_value: Any,
    *,
    source_url: str,
    checked_at: str,
    note: str,
) -> ContactValidationRecord:
    if _has_text(field_value):
        status = "failed"
        field_note = note
    else:
        status = "missing"
        field_note = f"{field_name} is not present on the candidate. {note}"

    return ContactValidationRecord(
        status=status,
        source_url=source_url,
        checked_at=checked_at,
        notes=field_note,
    )


def _field_record_from_source_text(
    field_name: str,
    field_value: Any,
    *,
    source_url: str,
    checked_at: str,
    source_text: str,
) -> tuple[FieldValidationRecord, str | None]:
    if not _has_text(field_value):
        return (
            FieldValidationRecord(
                status="missing",
                source_url=source_url,
                checked_at=checked_at,
                notes=f"{field_name} is not present on the candidate.",
            ),
            None,
        )

    snippet = _find_evidence_snippet(source_text, field_value)
    if snippet:
        return (
            FieldValidationRecord(
                status="supported",
                source_url=source_url,
                evidence_snippet=snippet,
                checked_at=checked_at,
                notes=f"Direct text support found for {field_name}.",
            ),
            snippet,
        )

    return (
        FieldValidationRecord(
            status="unsupported",
            source_url=source_url,
            checked_at=checked_at,
            notes=f"No direct text support found for {field_name}.",
        ),
        None,
    )


def _contact_record_from_source_text(
    field_name: str,
    field_value: Any,
    *,
    source_url: str,
    checked_at: str,
    source_text: str,
) -> tuple[ContactValidationRecord, str | None]:
    if not _has_text(field_value):
        return (
            ContactValidationRecord(
                status="missing",
                source_url=source_url,
                checked_at=checked_at,
                notes=f"{field_name} is not present on the candidate.",
            ),
            None,
        )

    snippet = _find_evidence_snippet(source_text, field_value)
    if snippet:
        return (
            ContactValidationRecord(
                status="verified_found",
                source_url=source_url,
                evidence_snippet=snippet,
                checked_at=checked_at,
                notes=f"Direct text support found for {field_name}.",
            ),
            snippet,
        )

    return (
        ContactValidationRecord(
            status="unsupported",
            source_url=source_url,
            checked_at=checked_at,
            notes=f"No direct text support found for {field_name}.",
        ),
        None,
    )


def _candidate_field_values(candidate: Candidate) -> dict[str, Any]:
    return {
        "name": getattr(candidate, "name", None),
        "title": getattr(candidate, "title", None),
        "organization": getattr(candidate, "organization", None),
        "email": getattr(candidate, "email", None),
        "phone": getattr(candidate, "phone", None),
    }


def _build_missing_source_validation(candidate: Candidate, *, checked_at: str) -> CandidateValidation:
    field_values = _candidate_field_values(candidate)
    return CandidateValidation(
        name=_field_record_for_missing_source("name", field_values["name"], checked_at=checked_at),
        title=_field_record_for_missing_source("title", field_values["title"], checked_at=checked_at),
        organization=_field_record_for_missing_source(
            "organization", field_values["organization"], checked_at=checked_at
        ),
        email=_contact_record_for_missing_source("email", field_values["email"], checked_at=checked_at),
        phone=_contact_record_for_missing_source("phone", field_values["phone"], checked_at=checked_at),
        source=FieldValidationRecord(
            status="missing",
            source_url=None,
            checked_at=checked_at,
            notes="source_url was not provided.",
        ),
    )


def _build_access_failure_validation(
    candidate: Candidate,
    *,
    source_url: str,
    checked_at: str,
    note: str,
) -> CandidateValidation:
    field_values = _candidate_field_values(candidate)
    return CandidateValidation(
        name=_field_record_for_access_failure("name", field_values["name"], source_url=source_url, checked_at=checked_at, note=note),
        title=_field_record_for_access_failure(
            "title", field_values["title"], source_url=source_url, checked_at=checked_at, note=note
        ),
        organization=_field_record_for_access_failure(
            "organization", field_values["organization"], source_url=source_url, checked_at=checked_at, note=note
        ),
        email=_contact_record_for_access_failure("email", field_values["email"], source_url=source_url, checked_at=checked_at, note=note),
        phone=_contact_record_for_access_failure("phone", field_values["phone"], source_url=source_url, checked_at=checked_at, note=note),
        source=FieldValidationRecord(
            status="failed",
            source_url=source_url,
            checked_at=checked_at,
            notes=note,
        ),
    )


def _build_source_text_validation(
    candidate: Candidate,
    *,
    resolved_url: str,
    status_code: int,
    checked_at: str,
    source_text: str,
) -> CandidateValidation:
    field_values = _candidate_field_values(candidate)
    field_records: dict[str, FieldValidationRecord] = {}
    supported_fields: list[str] = []
    best_snippet: str | None = None

    for field_name in ("name", "title", "organization", "email", "phone"):
        if field_name in {"email", "phone"}:
            record, snippet = _contact_record_from_source_text(
                field_name,
                field_values[field_name],
                source_url=resolved_url,
                checked_at=checked_at,
                source_text=source_text,
            )
        else:
            record, snippet = _field_record_from_source_text(
                field_name,
                field_values[field_name],
                source_url=resolved_url,
                checked_at=checked_at,
                source_text=source_text,
            )
        field_records[field_name] = record
        if record.status in _SUPPORTED_SOURCE_FIELD_STATUSES:
            supported_fields.append(field_name)
            if best_snippet is None:
                best_snippet = snippet

    source_status = "supported" if supported_fields else "unsupported"
    matched_fields = ",".join(supported_fields) if supported_fields else "none"
    source_notes = f"http_status={status_code} resolved_url={resolved_url} matched_fields={matched_fields}"

    return CandidateValidation(
        name=field_records["name"],
        title=field_records["title"],
        organization=field_records["organization"],
        email=field_records["email"],
        phone=field_records["phone"],
        source=FieldValidationRecord(
            status=source_status,
            source_url=resolved_url,
            evidence_snippet=best_snippet,
            checked_at=checked_at,
            notes=source_notes,
        ),
    )


async def _validate_candidate_source_with_client(
    candidate: Candidate,
    *,
    client: Any,
    source_url: str,
    checked_at: str,
) -> CandidateValidation:
    try:
        response = await client.get(source_url, follow_redirects=True)
    except Exception as exc:
        return _build_access_failure_validation(
            candidate,
            source_url=source_url,
            checked_at=checked_at,
            note=f"fetch_error={exc.__class__.__name__}: {exc}",
        )

    status_code = getattr(response, "status_code", None)
    resolved_url = str(getattr(response, "url", source_url))

    if not isinstance(status_code, int):
        return _build_access_failure_validation(
            candidate,
            source_url=resolved_url,
            checked_at=checked_at,
            note=f"fetch_error=invalid_status_code:{status_code!r}",
        )

    if status_code < 200 or status_code >= 300:
        return _build_access_failure_validation(
            candidate,
            source_url=resolved_url,
            checked_at=checked_at,
            note=f"http_status={status_code} resolved_url={resolved_url}",
        )

    source_text = _normalize_source_text(getattr(response, "text", ""))
    return _build_source_text_validation(
        candidate,
        resolved_url=resolved_url,
        status_code=status_code,
        checked_at=checked_at,
        source_text=source_text,
    )


async def validate_candidate_source(candidate: Candidate, *, client: Any | None = None) -> CandidateValidation:
    checked_at = _utc_now_iso()
    source_url = getattr(candidate, "source_url", None)

    if not _has_text(source_url):
        return _build_missing_source_validation(candidate, checked_at=checked_at)

    try:
        if client is None:
            async with httpx.AsyncClient(timeout=SOURCE_VALIDATION_TIMEOUT_SECONDS, follow_redirects=True) as async_client:
                return await _validate_candidate_source_with_client(
                    candidate,
                    client=async_client,
                    source_url=source_url,
                    checked_at=checked_at,
                )
        return await _validate_candidate_source_with_client(
            candidate,
            client=client,
            source_url=source_url,
            checked_at=checked_at,
        )
    except Exception as exc:  # pragma: no cover - defensive guard for unexpected validator bugs
        return _build_access_failure_validation(
            candidate,
            source_url=source_url,
            checked_at=checked_at,
            note=f"validator_error={exc.__class__.__name__}: {exc}",
        )
