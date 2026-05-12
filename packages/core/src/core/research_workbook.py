from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Mapping

from .manual_oracle import CRM_READY_CONTACT_STATUSES
from .source_assisted_compiler import (
    SourceAssistedCompileSummary,
    compile_april_nm_source_assisted_replay,
)


_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_R09G_REPLAY_ARTIFACT_PATH = (
    _REPO_ROOT / "audits/raw/reset-2026-05-10/r09g/research-workbook-replay.json"
)

WORKBOOK_TIERS = (
    "READY_WITH_CONTACT",
    "REVIEW",
    "MANUAL_LOOKUP",
    "ORG_ONLY",
    "NOT_FOUND",
    "FAILED",
)
WORKBOOK_TIER_ORDER = {tier: index for index, tier in enumerate(WORKBOOK_TIERS)}
DEFAULT_R09G_QUERY = "NM IT for school districts"
DEFAULT_R09G_RUN_ID = "r09g-april-nm-source-assisted-workbook"


@dataclass(frozen=True, slots=True)
class ResearchWorkbookRow:
    rank: int
    query: str
    run_id: str
    candidate_id: str
    input_row_id: str
    workbook_tier: str
    operator_label: str
    candidate_category: str
    crm_ready: bool
    lead_name: str
    title: str
    organization: str
    email: str
    email_status: str
    phone: str
    phone_status: str
    fit_score: str
    evidence_score: str
    contact_score: str
    ranking_gate: str
    source_name_url: str
    source_title_url: str
    source_org_url: str
    source_email_url: str
    source_phone_url: str
    source_access_status: str
    source_id: str
    source_ids: tuple[str, ...]
    source_family: str
    source_reputation_signal: str
    input_method: str
    validation_notes: str
    blocker_notes: str
    next_action: str
    checked_at: str

    def to_export_row(self) -> dict[str, str]:
        return {
            "query": self.query,
            "run_id": self.run_id,
            "rank": str(self.rank),
            "workbook_tier": self.workbook_tier,
            "operator_label": self.operator_label,
            "candidate_category": self.candidate_category,
            "crm_ready": "yes" if self.crm_ready else "no",
            "lead_name": self.lead_name,
            "title": self.title,
            "organization": self.organization,
            "email": self.email,
            "email_status": self.email_status,
            "phone": self.phone,
            "phone_status": self.phone_status,
            "fit_score": self.fit_score,
            "evidence_score": self.evidence_score,
            "contact_score": self.contact_score,
            "ranking_gate": self.ranking_gate,
            "source_name_url": self.source_name_url,
            "source_title_url": self.source_title_url,
            "source_org_url": self.source_org_url,
            "source_email_url": self.source_email_url,
            "source_phone_url": self.source_phone_url,
            "source_access_status": self.source_access_status,
            "source_id": self.source_id,
            "source_ids": ";".join(self.source_ids),
            "source_family": self.source_family,
            "source_reputation_signal": self.source_reputation_signal,
            "input_method": self.input_method,
            "validation_notes": self.validation_notes,
            "blocker_notes": self.blocker_notes,
            "next_action": self.next_action,
            "checked_at": self.checked_at,
        }

    def to_payload(self) -> dict[str, Any]:
        payload = self.to_export_row()
        payload["rank"] = self.rank
        payload["crm_ready"] = self.crm_ready
        payload["source_ids"] = list(self.source_ids)
        return payload


@dataclass(frozen=True, slots=True)
class ResearchWorkbookSummary:
    workbook_id: str
    source_compiler_id: str
    query: str
    run_id: str
    rows: tuple[ResearchWorkbookRow, ...]
    source_count: int
    downgraded_ready_rows: tuple[str, ...]

    @property
    def tier_distribution(self) -> dict[str, int]:
        distribution = {tier: 0 for tier in WORKBOOK_TIERS}
        for row in self.rows:
            distribution[row.workbook_tier] += 1
        return distribution

    @property
    def export_rows(self) -> list[dict[str, str]]:
        return [row.to_export_row() for row in self.rows]

    def passes(self) -> bool:
        unsupported_ready = [
            row
            for row in self.rows
            if row.workbook_tier == "READY_WITH_CONTACT"
            and row.email_status not in CRM_READY_CONTACT_STATUSES
        ]
        missing_source = [row for row in self.rows if not _best_source_url(row)]
        return bool(self.rows) and not unsupported_ready and not missing_source

    def to_payload(self) -> dict[str, Any]:
        return {
            "workbook_id": self.workbook_id,
            "source_compiler_id": self.source_compiler_id,
            "query": self.query,
            "run_id": self.run_id,
            "source_count": self.source_count,
            "row_count": len(self.rows),
            "tier_distribution": self.tier_distribution,
            "export_headers": list(RESEARCH_WORKBOOK_EXPORT_HEADERS),
            "downgraded_ready_rows": list(self.downgraded_ready_rows),
            "rows": [row.to_payload() for row in self.rows],
            "passes": self.passes(),
        }


RESEARCH_WORKBOOK_EXPORT_HEADERS = (
    "query",
    "run_id",
    "rank",
    "workbook_tier",
    "operator_label",
    "candidate_category",
    "crm_ready",
    "lead_name",
    "title",
    "organization",
    "email",
    "email_status",
    "phone",
    "phone_status",
    "fit_score",
    "evidence_score",
    "contact_score",
    "ranking_gate",
    "source_name_url",
    "source_title_url",
    "source_org_url",
    "source_email_url",
    "source_phone_url",
    "source_access_status",
    "source_id",
    "source_ids",
    "source_family",
    "source_reputation_signal",
    "input_method",
    "validation_notes",
    "blocker_notes",
    "next_action",
    "checked_at",
)


def build_april_nm_research_workbook_replay(
    *,
    query: str = DEFAULT_R09G_QUERY,
    run_id: str = DEFAULT_R09G_RUN_ID,
    compile_summary: SourceAssistedCompileSummary | None = None,
) -> ResearchWorkbookSummary:
    source_summary = compile_summary or compile_april_nm_source_assisted_replay()
    return build_research_workbook_from_compile_summary(
        source_summary,
        query=query,
        run_id=run_id,
        workbook_id="r09g_research_workbook_tiering_export_semantics",
    )


def build_research_workbook_from_compile_summary(
    summary: SourceAssistedCompileSummary,
    *,
    query: str,
    run_id: str,
    workbook_id: str = "research_workbook",
) -> ResearchWorkbookSummary:
    return build_research_workbook(
        summary.candidate_payloads,
        source_records=(source.to_payload() for source in summary.source_records),
        query=query,
        run_id=run_id,
        workbook_id=workbook_id,
        source_compiler_id=summary.compiler_id,
    )


def build_research_workbook(
    candidates: Iterable[Mapping[str, Any]],
    *,
    query: str,
    run_id: str,
    workbook_id: str = "research_workbook",
    source_compiler_id: str = "",
    source_records: Iterable[Mapping[str, Any]] = (),
) -> ResearchWorkbookSummary:
    candidate_payloads = tuple(dict(candidate) for candidate in candidates)
    source_lookup = _source_records_by_id(source_records)
    rows_with_order: list[tuple[int, int, ResearchWorkbookRow]] = []
    downgraded_ready_rows: list[str] = []

    for index, candidate in enumerate(candidate_payloads):
        workbook_tier = resolve_workbook_tier(candidate)
        if _is_claimed_ready(candidate) and workbook_tier != "READY_WITH_CONTACT":
            downgraded_ready_rows.append(_row_identity(candidate))
        rows_with_order.append(
            (
                WORKBOOK_TIER_ORDER[workbook_tier],
                index,
                _build_workbook_row(
                    candidate,
                    source_lookup=source_lookup,
                    query=query,
                    run_id=run_id,
                    workbook_tier=workbook_tier,
                ),
            )
        )

    ranked_rows = tuple(
        replace(row, rank=rank)
        for rank, (_, _, row) in enumerate(sorted(rows_with_order), start=1)
    )

    return ResearchWorkbookSummary(
        workbook_id=workbook_id,
        source_compiler_id=source_compiler_id,
        query=query,
        run_id=run_id,
        rows=ranked_rows,
        source_count=len(source_lookup),
        downgraded_ready_rows=tuple(downgraded_ready_rows),
    )


def resolve_workbook_tier(candidate: Mapping[str, Any]) -> str:
    tier = _text(candidate.get("tier")) or _text(candidate.get("expected_tier"))
    category = _text(candidate.get("candidate_category"))
    contact_status = _contact_status(candidate)

    if category == "organization_only" or tier == "organization_only":
        return "ORG_ONLY"
    if category == "not_found" or tier == "not_found":
        return "NOT_FOUND"
    if category == "failed" or tier == "failed":
        return "FAILED"
    if tier == "manual_lookup":
        return "MANUAL_LOOKUP"
    if tier == "high_trust_usable":
        if contact_status in CRM_READY_CONTACT_STATUSES and _has_ready_field_support(candidate):
            return "READY_WITH_CONTACT"
        if contact_status in {"missing", "unsupported"}:
            return "MANUAL_LOOKUP"
        return "REVIEW"
    if tier == "review":
        return "REVIEW"
    if contact_status in CRM_READY_CONTACT_STATUSES and _has_ready_field_support(candidate):
        return "READY_WITH_CONTACT"
    if contact_status in {"missing", "unsupported"}:
        return "MANUAL_LOOKUP"
    return "REVIEW"


def build_research_workbook_csv(rows: Iterable[ResearchWorkbookRow | Mapping[str, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(RESEARCH_WORKBOOK_EXPORT_HEADERS), extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        export_row = row.to_export_row() if isinstance(row, ResearchWorkbookRow) else dict(row)
        writer.writerow({header: export_row.get(header, "") for header in RESEARCH_WORKBOOK_EXPORT_HEADERS})
    return buffer.getvalue().strip("\r\n")


def write_r09g_replay_artifact(
    path: Path | None = None,
    summary: ResearchWorkbookSummary | None = None,
) -> Path:
    artifact_path = path or DEFAULT_R09G_REPLAY_ARTIFACT_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    replay = summary or build_april_nm_research_workbook_replay()
    artifact_path.write_text(
        json.dumps(replay.to_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact_path


def _build_workbook_row(
    candidate: Mapping[str, Any],
    *,
    source_lookup: Mapping[str, Mapping[str, Any]],
    query: str,
    run_id: str,
    workbook_tier: str,
) -> ResearchWorkbookRow:
    source_id = _text(candidate.get("source_id"))
    source = source_lookup.get(source_id, {})
    source_ids = _string_tuple(candidate.get("source_ids")) or ((source_id,) if source_id else ())
    field_evidence = _field_evidence(candidate)
    source_url = _text(candidate.get("source_url")) or _text(source.get("url"))
    source_family = _text(candidate.get("source_family")) or _text(source.get("source_family"))
    source_reputation_signal = _text(candidate.get("source_reputation_signal")) or _text(
        source.get("source_reputation_signal")
    )
    input_method = _text(candidate.get("input_method")) or _text(source.get("input_method"))
    source_access_status = _text(source.get("access_status")) or _evidence_status(field_evidence, "source")
    email_status = _contact_status(candidate)
    phone = _text(candidate.get("phone"))
    phone_status = "verified_found" if phone else _evidence_status(field_evidence, "phone") or "missing"
    blocker_notes = _text(candidate.get("blocker_notes"))
    next_action = _text(candidate.get("next_action"))

    return ResearchWorkbookRow(
        rank=0,
        query=query,
        run_id=run_id,
        candidate_id=_text(candidate.get("candidate_id")) or _text(candidate.get("id")),
        input_row_id=_text(candidate.get("input_row_id")),
        workbook_tier=workbook_tier,
        operator_label=_operator_label(workbook_tier),
        candidate_category=_text(candidate.get("candidate_category")) or "person_lead",
        crm_ready=workbook_tier == "READY_WITH_CONTACT",
        lead_name=_text(candidate.get("lead_name")) or _text(candidate.get("name")),
        title=_text(candidate.get("title")),
        organization=_text(candidate.get("organization")) or _text(candidate.get("searched_target")),
        email=_safe_ready_contact_value(_text(candidate.get("email")), email_status, workbook_tier),
        email_status=email_status,
        phone=_safe_ready_contact_value(phone, phone_status, workbook_tier),
        phone_status=phone_status,
        fit_score=_score(candidate, "fit_score"),
        evidence_score=_score(candidate, "evidence_score"),
        contact_score=_score(candidate, "contact_score"),
        ranking_gate=workbook_tier,
        source_name_url=_evidence_url(field_evidence, "name", source_url),
        source_title_url=_evidence_url(field_evidence, "title", source_url),
        source_org_url=_evidence_url(field_evidence, "organization", source_url),
        source_email_url=_evidence_url(field_evidence, "email", source_url),
        source_phone_url=_evidence_url(field_evidence, "phone", ""),
        source_access_status=source_access_status,
        source_id=source_id,
        source_ids=source_ids,
        source_family=source_family,
        source_reputation_signal=source_reputation_signal,
        input_method=input_method,
        validation_notes=_validation_notes(
            candidate,
            workbook_tier=workbook_tier,
            email_status=email_status,
            phone_status=phone_status,
            blocker_notes=blocker_notes,
            next_action=next_action,
        ),
        blocker_notes=blocker_notes,
        next_action=next_action,
        checked_at=_checked_at(field_evidence),
    )


def _source_records_by_id(records: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for record in records:
        payload = dict(record)
        source_id = _text(payload.get("source_id"))
        if source_id:
            indexed[source_id] = payload
    return indexed


def _field_evidence(candidate: Mapping[str, Any]) -> Mapping[str, Mapping[str, Any]]:
    raw = candidate.get("field_evidence") or candidate.get("validation") or {}
    if not isinstance(raw, Mapping):
        return {}
    evidence: dict[str, Mapping[str, Any]] = {}
    for field_name, record in raw.items():
        if isinstance(record, Mapping):
            evidence[str(field_name)] = record
    return evidence


def _has_ready_field_support(candidate: Mapping[str, Any]) -> bool:
    if (_text(candidate.get("candidate_category")) or "person_lead") != "person_lead":
        return False
    if not (
        _text(candidate.get("source_url"))
        and _text(candidate.get("organization"))
        and _text(candidate.get("title"))
        and (_text(candidate.get("lead_name")) or _text(candidate.get("name")))
    ):
        return False
    evidence = _field_evidence(candidate)
    for field_name in ("name", "title", "organization", "email", "source"):
        status = _evidence_status(evidence, field_name)
        if status and field_name in {"name", "title", "organization", "source"} and status != "supported":
            return False
        if field_name == "email" and status and status not in CRM_READY_CONTACT_STATUSES:
            return False
    return True


def _is_claimed_ready(candidate: Mapping[str, Any]) -> bool:
    tier = _text(candidate.get("tier")) or _text(candidate.get("expected_tier"))
    return tier == "high_trust_usable"


def _row_identity(candidate: Mapping[str, Any]) -> str:
    return (
        _text(candidate.get("candidate_id"))
        or _text(candidate.get("input_row_id"))
        or _text(candidate.get("organization"))
        or "unknown-row"
    )


def _operator_label(workbook_tier: str) -> str:
    labels = {
        "READY_WITH_CONTACT": "READY",
        "REVIEW": "REVIEW",
        "MANUAL_LOOKUP": "MANUAL LOOKUP",
        "ORG_ONLY": "ORG-ONLY",
        "NOT_FOUND": "NOT FOUND",
        "FAILED": "FAILED",
    }
    return labels[workbook_tier]


def _safe_ready_contact_value(value: str, status: str, workbook_tier: str) -> str:
    if workbook_tier != "READY_WITH_CONTACT":
        return ""
    return value if status in CRM_READY_CONTACT_STATUSES else ""


def _validation_notes(
    candidate: Mapping[str, Any],
    *,
    workbook_tier: str,
    email_status: str,
    phone_status: str,
    blocker_notes: str,
    next_action: str,
) -> str:
    parts = [
        f"Workbook tier: {workbook_tier}.",
        f"Candidate category: {_text(candidate.get('candidate_category')) or 'person_lead'}.",
        f"Email status: {email_status}.",
        f"Phone status: {phone_status}.",
    ]
    primary_reason = _text(candidate.get("primary_filter_reason"))
    verification_note = _text(candidate.get("verification_note")) or _text(candidate.get("validation_notes"))
    if primary_reason:
        parts.append(f"Reason: {primary_reason}.")
    if verification_note and verification_note != primary_reason:
        parts.append(f"Verification: {verification_note}.")
    if blocker_notes:
        parts.append(f"Blocker: {blocker_notes}.")
    if next_action:
        parts.append(f"Next action: {next_action}.")
    if workbook_tier != "READY_WITH_CONTACT":
        parts.append("CRM import blocked until the row has supported contact evidence.")
    return " ".join(parts)


def _best_source_url(row: ResearchWorkbookRow) -> str:
    return (
        row.source_name_url
        or row.source_title_url
        or row.source_org_url
        or row.source_email_url
        or row.source_phone_url
    )


def _evidence_url(evidence: Mapping[str, Mapping[str, Any]], field_name: str, fallback: str) -> str:
    record = evidence.get(field_name, {})
    return _text(record.get("source_url")) or fallback


def _evidence_status(evidence: Mapping[str, Mapping[str, Any]], field_name: str) -> str:
    return _text(evidence.get(field_name, {}).get("status"))


def _checked_at(evidence: Mapping[str, Mapping[str, Any]]) -> str:
    for field_name in ("source", "email", "name", "title", "organization", "phone"):
        checked_at = _text(evidence.get(field_name, {}).get("checked_at"))
        if checked_at:
            return checked_at
    return ""


def _contact_status(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("contact_status")) or _text(candidate.get("email_status")) or "unsupported"


def _score(candidate: Mapping[str, Any], key: str) -> str:
    value = candidate.get(key)
    if isinstance(value, int | float):
        return f"{float(value):.2f}"
    return _text(value)


def _string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value if str(item))
    return ()


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
