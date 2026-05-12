from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .k12_source_map import (
    GENERIC_SEARCH_FAMILIES,
    K12SourceMap,
    collect_k12_roster_sources,
    load_nm_k12_source_map,
)
from .manual_oracle import (
    CRM_READY_CONTACT_STATUSES,
    ManualOracleFixture,
    ManualOracleRow,
    evaluate_manual_oracle_replay,
    load_april_nm_manual_oracle_fixture,
)


_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_R09F_REPLAY_ARTIFACT_PATH = (
    _REPO_ROOT / "audits/raw/reset-2026-05-10/r09f/source-assisted-compiler-replay.json"
)

CANONICAL_TIERS = {
    "high_trust_usable",
    "manual_lookup",
    "review",
    "organization_only",
    "not_found",
    "failed",
}
CONTACT_STATUSES = {
    "verified_found",
    "deduced_with_pattern_evidence",
    "missing",
    "failed",
    "unsupported",
}
_TIER_PRIORITY = {
    "high_trust_usable": 50,
    "manual_lookup": 40,
    "review": 30,
    "organization_only": 20,
    "not_found": 10,
    "failed": 0,
}
_CONTACT_PRIORITY = {
    "verified_found": 5,
    "deduced_with_pattern_evidence": 4,
    "missing": 2,
    "unsupported": 1,
    "failed": 0,
}
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class SourceAssistedSourceRecord:
    source_id: str
    url: str
    source_family: str
    access_status: str
    source_reputation_signal: str
    input_method: str
    supports: tuple[str, ...]
    district_id: str = ""
    district_name: str = ""
    notes: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "url": self.url,
            "source_family": self.source_family,
            "access_status": self.access_status,
            "source_reputation_signal": self.source_reputation_signal,
            "input_method": self.input_method,
            "supports": list(self.supports),
            "district_id": self.district_id,
            "district_name": self.district_name,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class CompiledCandidateRow:
    candidate_id: str
    input_row_id: str
    candidate_category: str
    tier: str
    organization: str
    title: str
    lead_name: str
    email: str
    phone: str
    contact_status: str
    source_url: str
    source_id: str
    source_ids: tuple[str, ...]
    source_family: str
    source_reputation_signal: str
    input_method: str
    verification_note: str
    blocker_notes: str
    next_action: str
    primary_filter_reason: str
    field_evidence: Mapping[str, Mapping[str, Any]]

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "input_row_id": self.input_row_id,
            "candidate_category": self.candidate_category,
            "tier": self.tier,
            "expected_tier": self.tier,
            "organization": self.organization,
            "title": self.title,
            "lead_name": self.lead_name,
            "name": self.lead_name,
            "email": self.email,
            "phone": self.phone,
            "contact_status": self.contact_status,
            "email_status": self.contact_status,
            "source_url": self.source_url,
            "source_id": self.source_id,
            "source_ids": list(self.source_ids),
            "source_family": self.source_family,
            "source_reputation_signal": self.source_reputation_signal,
            "input_method": self.input_method,
            "verification_note": self.verification_note,
            "validation_notes": self.verification_note,
            "blocker_notes": self.blocker_notes,
            "next_action": self.next_action,
            "primary_filter_reason": self.primary_filter_reason,
            "field_evidence": {
                key: dict(value) for key, value in self.field_evidence.items()
            },
        }


@dataclass(frozen=True, slots=True)
class SourceAssistedCompileSummary:
    compiler_id: str
    candidate_rows: tuple[CompiledCandidateRow, ...]
    source_records: tuple[SourceAssistedSourceRecord, ...]
    duplicate_rows: tuple[str, ...]
    blocked_source_urls: tuple[str, ...]
    input_counts: Mapping[str, int]
    manual_oracle_replay: Mapping[str, Any] | None

    @property
    def tier_distribution(self) -> dict[str, int]:
        distribution = {tier: 0 for tier in CANONICAL_TIERS}
        for row in self.candidate_rows:
            distribution[row.tier] = distribution.get(row.tier, 0) + 1
        return dict(sorted(distribution.items()))

    @property
    def candidate_payloads(self) -> list[dict[str, Any]]:
        return [row.to_payload() for row in self.candidate_rows]

    def passes(self) -> bool:
        unsupported_ready = [
            row
            for row in self.candidate_rows
            if row.tier == "high_trust_usable"
            and row.contact_status not in CRM_READY_CONTACT_STATUSES
        ]
        if unsupported_ready:
            return False
        if self.manual_oracle_replay is not None:
            return bool(self.manual_oracle_replay.get("structure_reproduced"))
        return bool(self.candidate_rows)

    def to_payload(self) -> dict[str, Any]:
        return {
            "compiler_id": self.compiler_id,
            "input_counts": dict(self.input_counts),
            "source_count": len(self.source_records),
            "candidate_count": len(self.candidate_rows),
            "tier_distribution": self.tier_distribution,
            "duplicate_rows": list(self.duplicate_rows),
            "blocked_source_urls": list(self.blocked_source_urls),
            "manual_oracle_replay": dict(self.manual_oracle_replay)
            if self.manual_oracle_replay is not None
            else None,
            "source_records": [source.to_payload() for source in self.source_records],
            "candidate_rows": self.candidate_payloads,
            "passes": self.passes(),
        }


def compile_april_nm_source_assisted_replay(
    *,
    manual_oracle_fixture: ManualOracleFixture | None = None,
    source_map: K12SourceMap | None = None,
) -> SourceAssistedCompileSummary:
    return compile_source_assisted_leads(
        manual_oracle_fixture=manual_oracle_fixture or load_april_nm_manual_oracle_fixture(),
        source_map=source_map or load_nm_k12_source_map(),
    )


def compile_source_assisted_leads(
    *,
    source_map: K12SourceMap | None = None,
    manual_oracle_fixture: ManualOracleFixture | None = None,
    source_urls: Iterable[str] = (),
    source_packs: Iterable[Mapping[str, Any]] = (),
    seed_csv_rows: Iterable[Mapping[str, Any]] = (),
    pasted_text: str = "",
) -> SourceAssistedCompileSummary:
    sources: dict[str, SourceAssistedSourceRecord] = {}
    source_urls_tuple = tuple(source_urls)
    source_packs_tuple = tuple(source_packs)
    seed_csv_rows_tuple = tuple(seed_csv_rows)
    pasted_rows = tuple(parse_pasted_candidate_rows(pasted_text))
    source_map_row_sources: dict[str, SourceAssistedSourceRecord] = {}
    source_map_source_count = 0

    if source_map is not None:
        for record in _source_records_from_source_map(source_map):
            source_map_source_count += 1
            _add_source_record(sources, record)
            for row_id in _source_map_row_ids(source_map, record):
                source_map_row_sources[row_id] = record

    for url in source_urls_tuple:
        normalized_url = _clean(url)
        if not normalized_url:
            continue
        _add_source_record(
            sources,
            SourceAssistedSourceRecord(
                source_id=_stable_id("src", normalized_url),
                url=normalized_url,
                source_family="operator_source_url",
                access_status="operator_supplied",
                source_reputation_signal="operator_supplied_public_source",
                input_method="source_url",
                supports=("source evidence",),
            ),
        )

    for source_pack in source_packs_tuple:
        record = _source_record_from_mapping(source_pack, input_method="source_pack")
        if record is not None:
            _add_source_record(sources, record)

    compiled_rows: list[CompiledCandidateRow] = []
    if manual_oracle_fixture is not None:
        for row in manual_oracle_fixture.rows:
            compiled_rows.append(
                _candidate_from_manual_oracle_row(row, sources, source_map_row_sources)
            )

    for row in seed_csv_rows_tuple:
        candidate = _candidate_from_mapping(
            row,
            sources=sources,
            input_method="seed_csv_row",
            default_source_family="seed_csv",
        )
        if candidate is not None:
            compiled_rows.append(candidate)

    for source_pack in source_packs_tuple:
        pack_source = _source_record_from_mapping(source_pack, input_method="source_pack")
        for row in _source_pack_rows(source_pack):
            candidate = _candidate_from_mapping(
                row,
                sources=sources,
                input_method="source_pack",
                default_source=pack_source,
                default_source_family="source_pack",
            )
            if candidate is not None:
                compiled_rows.append(candidate)

    for row in pasted_rows:
        candidate = _candidate_from_mapping(
            row,
            sources=sources,
            input_method="pasted_text",
            default_source_family="pasted_search_or_chatbot_output",
        )
        if candidate is not None:
            compiled_rows.append(candidate)

    deduped_rows, duplicate_rows = _dedupe_rows(compiled_rows)
    manual_replay_payload = None
    if manual_oracle_fixture is not None:
        manual_replay_payload = evaluate_manual_oracle_replay(
            [row.to_payload() for row in deduped_rows],
            fixture=manual_oracle_fixture,
        ).to_payload()

    blocked_source_urls = tuple(
        record.url
        for record in sources.values()
        if record.source_family in GENERIC_SEARCH_FAMILIES
    )

    return SourceAssistedCompileSummary(
        compiler_id="r09f_source_assisted_lead_compiler",
        candidate_rows=tuple(deduped_rows),
        source_records=tuple(sorted(sources.values(), key=lambda item: item.source_id)),
        duplicate_rows=tuple(duplicate_rows),
        blocked_source_urls=blocked_source_urls,
        input_counts={
            "source_map_sources": source_map_source_count,
            "source_urls": len(source_urls_tuple),
            "source_packs": len(source_packs_tuple),
            "seed_csv_rows": len(seed_csv_rows_tuple),
            "pasted_rows": len(pasted_rows),
            "manual_oracle_rows": len(manual_oracle_fixture.rows)
            if manual_oracle_fixture is not None
            else 0,
        },
        manual_oracle_replay=manual_replay_payload,
    )


def parse_seed_csv_text(text: str) -> list[dict[str, str]]:
    if not text.strip():
        return []
    reader = csv.DictReader(io.StringIO(text))
    return [{str(key): str(value or "") for key, value in row.items()} for row in reader]


def parse_pasted_candidate_rows(text: str) -> list[dict[str, str]]:
    if not text.strip():
        return []
    if "," in text.splitlines()[0] and "organization" in text.splitlines()[0].lower():
        return parse_seed_csv_text(text)

    rows: list[dict[str, str]] = []
    for index, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 4:
            continue
        rows.append(
            {
                "row_id": f"pasted-{index:02d}",
                "organization": parts[0],
                "title": parts[1],
                "contact_status": parts[2],
                "source_url": parts[3],
                "verification_note": parts[4] if len(parts) > 4 else "",
                "next_action": parts[5] if len(parts) > 5 else "",
            }
        )
    return rows


def write_r09f_replay_artifact(
    path: Path | None = None,
    summary: SourceAssistedCompileSummary | None = None,
) -> Path:
    artifact_path = path or DEFAULT_R09F_REPLAY_ARTIFACT_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    replay = summary or compile_april_nm_source_assisted_replay()
    artifact_path.write_text(
        json.dumps(replay.to_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact_path


def _source_records_from_source_map(source_map: K12SourceMap) -> list[SourceAssistedSourceRecord]:
    records: list[SourceAssistedSourceRecord] = []
    for seed in collect_k12_roster_sources(source_map):
        records.append(
            SourceAssistedSourceRecord(
                source_id=seed.seed_id,
                url=seed.url,
                source_family=seed.source_family,
                access_status=seed.access_status,
                source_reputation_signal=seed.source_reputation_signal,
                input_method="k12_source_map",
                supports=seed.supports,
                district_id=seed.district_id,
                district_name=seed.district_name,
                notes="R09E roster-first source map seed.",
            )
        )
    return records


def _source_map_row_ids(
    source_map: K12SourceMap,
    record: SourceAssistedSourceRecord,
) -> tuple[str, ...]:
    for district in source_map.districts:
        if district.district_id == record.district_id:
            aliases: list[str] = []
            for row_id in district.manual_oracle_row_ids:
                aliases.extend(_manual_oracle_aliases(row_id))
            return tuple(aliases)
    return ()


def _candidate_from_manual_oracle_row(
    row: ManualOracleRow,
    sources: dict[str, SourceAssistedSourceRecord],
    source_map_row_sources: Mapping[str, SourceAssistedSourceRecord],
) -> CompiledCandidateRow:
    source = _manual_oracle_source_for_row(row, sources, source_map_row_sources)
    return _candidate_from_mapping(
        {
            "row_id": row.row_id,
            "organization": row.organization,
            "title": row.title,
            "lead_name": row.contact_label,
            "email": row.email_value,
            "phone": row.phone_value,
            "contact_status": row.contact_status,
            "source_url": row.source_url,
            "source_family": source.source_family,
            "source_reputation_signal": source.source_reputation_signal,
            "verification_note": row.verification_note,
            "expected_tier": row.expected_tier,
            "next_action": row.next_action,
            "checked_at": row.last_verified,
        },
        sources=sources,
        input_method="manual_oracle_row_replay",
        default_source=source,
        default_source_family=source.source_family,
    ) or _empty_failed_row(row, source)


def _candidate_from_mapping(
    row: Mapping[str, Any],
    *,
    sources: dict[str, SourceAssistedSourceRecord],
    input_method: str,
    default_source_family: str,
    default_source: SourceAssistedSourceRecord | None = None,
) -> CompiledCandidateRow | None:
    organization = _first_text(row, "organization", "org", "district", "district_name")
    title = _first_text(row, "title", "role")
    source_url = _first_text(row, "source_url", "url")
    if not organization and not source_url:
        return None

    source = default_source or _source_for_mapping(
        row,
        source_url=source_url,
        sources=sources,
        input_method=input_method,
        default_source_family=default_source_family,
    )
    if source is None:
        return None
    _add_source_record(sources, source)

    source_url = source_url or source.url
    contact_status = _normalize_contact_status(_first_text(row, "contact_status", "email_status"))
    tier = _normalize_tier(_first_text(row, "expected_tier", "tier"), contact_status, title, source_url)
    if tier == "high_trust_usable" and contact_status not in CRM_READY_CONTACT_STATUSES:
        tier = "manual_lookup"

    verification_note = _first_text(
        row,
        "verification_note",
        "validation_notes",
        "notes",
        "primary_filter_reason",
        "explanation",
    )
    next_action = _first_text(row, "next_action", "action")
    blocker_notes = _blocker_notes(tier, contact_status, verification_note, next_action)
    primary_filter_reason = _primary_filter_reason(tier, contact_status, blocker_notes)
    email = _safe_email(_first_text(row, "email", "email_value"))
    phone = _safe_contact_value(_first_text(row, "phone", "phone_value"))
    lead_name = _first_text(row, "lead_name", "name", "contact_label")
    input_row_id = _first_text(row, "row_id", "id") or _stable_id(
        "input",
        organization,
        title,
        source_url,
    )

    return CompiledCandidateRow(
        candidate_id=_stable_id("r09frow", organization, title, lead_name, source_url),
        input_row_id=input_row_id,
        candidate_category=_candidate_category(tier, title),
        tier=tier,
        organization=organization,
        title=title,
        lead_name=lead_name,
        email=email,
        phone=phone,
        contact_status=contact_status,
        source_url=source_url,
        source_id=source.source_id,
        source_ids=(source.source_id,),
        source_family=source.source_family,
        source_reputation_signal=source.source_reputation_signal,
        input_method=input_method,
        verification_note=verification_note or primary_filter_reason,
        blocker_notes=blocker_notes,
        next_action=next_action,
        primary_filter_reason=primary_filter_reason,
        field_evidence=_field_evidence(
            lead_name=lead_name,
            title=title,
            organization=organization,
            contact_status=contact_status,
            source=source,
            source_url=source_url,
            verification_note=verification_note,
            checked_at=_first_text(row, "checked_at", "last_verified"),
        ),
    )


def _manual_oracle_source_for_row(
    row: ManualOracleRow,
    sources: dict[str, SourceAssistedSourceRecord],
    source_map_row_sources: Mapping[str, SourceAssistedSourceRecord],
) -> SourceAssistedSourceRecord:
    mapped = sources.get(_source_key(row.source_url))
    if mapped is not None:
        return mapped

    for alias in _manual_oracle_aliases(row.row_id):
        source = source_map_row_sources.get(alias)
        if source is not None:
            return source

    source_family = "manual_oracle_seed"
    if row.source_csv_shape == "public_emails":
        source_family = "manual_oracle_public_email_source"
    return SourceAssistedSourceRecord(
        source_id=_stable_id("src", row.source_url, row.row_id),
        url=row.source_url,
        source_family=source_family,
        access_status="manual_oracle_replay_source",
        source_reputation_signal="official_public_document",
        input_method="manual_oracle_row_replay",
        supports=("organization", "title", "contact_status", "source_url", "blocker_note"),
        district_name=row.organization,
        notes=row.source_url_type or "R09D sanitized source row.",
    )


def _source_record_from_mapping(
    payload: Mapping[str, Any],
    *,
    input_method: str,
) -> SourceAssistedSourceRecord | None:
    url = _first_text(payload, "source_url", "url")
    if not url:
        return None
    return SourceAssistedSourceRecord(
        source_id=_first_text(payload, "source_id", "id") or _stable_id("src", url),
        url=url,
        source_family=_first_text(payload, "source_family") or input_method,
        access_status=_first_text(payload, "access_status") or "operator_supplied",
        source_reputation_signal=_first_text(payload, "source_reputation_signal")
        or "operator_supplied_public_source",
        input_method=input_method,
        supports=_supports_from_payload(payload),
        district_id=_first_text(payload, "district_id"),
        district_name=_first_text(payload, "district_name", "organization"),
        notes=_first_text(payload, "notes"),
    )


def _source_for_mapping(
    row: Mapping[str, Any],
    *,
    source_url: str,
    sources: Mapping[str, SourceAssistedSourceRecord],
    input_method: str,
    default_source_family: str,
) -> SourceAssistedSourceRecord | None:
    if source_url and _source_key(source_url) in sources:
        return sources[_source_key(source_url)]
    if not source_url:
        return None
    return SourceAssistedSourceRecord(
        source_id=_first_text(row, "source_id") or _stable_id("src", source_url),
        url=source_url,
        source_family=_first_text(row, "source_family") or default_source_family,
        access_status=_first_text(row, "access_status") or "operator_supplied",
        source_reputation_signal=_first_text(row, "source_reputation_signal")
        or "operator_supplied_public_source",
        input_method=input_method,
        supports=("organization", "title", "contact_status", "source_url"),
        district_name=_first_text(row, "organization", "district_name"),
        notes=_first_text(row, "notes"),
    )


def _source_pack_rows(source_pack: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    rows = source_pack.get("rows", ())
    if not isinstance(rows, Iterable) or isinstance(rows, (str, bytes)):
        return ()
    return tuple(row for row in rows if isinstance(row, Mapping))


def _dedupe_rows(rows: Iterable[CompiledCandidateRow]) -> tuple[list[CompiledCandidateRow], list[str]]:
    kept: dict[tuple[str, str], CompiledCandidateRow] = {}
    duplicate_rows: list[str] = []
    for row in rows:
        key = (row.organization.strip().lower(), row.title.strip().lower())
        if key not in kept:
            kept[key] = row
            continue
        if _row_priority(row) > _row_priority(kept[key]):
            duplicate_rows.append(kept[key].input_row_id)
            kept[key] = row
        else:
            duplicate_rows.append(row.input_row_id)
    return list(kept.values()), duplicate_rows


def _supports_from_payload(payload: Mapping[str, Any]) -> tuple[str, ...]:
    supports = payload.get("supports", ("source evidence",))
    if isinstance(supports, str):
        return (supports,)
    if isinstance(supports, Iterable):
        return tuple(str(item) for item in supports)
    return ("source evidence",)


def _row_priority(row: CompiledCandidateRow) -> tuple[int, int, int]:
    return (
        _TIER_PRIORITY.get(row.tier, -1),
        _CONTACT_PRIORITY.get(row.contact_status, -1),
        1 if row.source_url else 0,
    )


def _field_evidence(
    *,
    lead_name: str,
    title: str,
    organization: str,
    contact_status: str,
    source: SourceAssistedSourceRecord,
    source_url: str,
    verification_note: str,
    checked_at: str,
) -> dict[str, dict[str, Any]]:
    return {
        "name": _evidence_record(
            "supported" if lead_name else "missing",
            source,
            source_url,
            "Named public contact retained as a sanitized label." if lead_name else "No person name in input.",
            checked_at,
        ),
        "title": _evidence_record(
            "supported" if title else "missing",
            source,
            source_url,
            title,
            checked_at,
        ),
        "organization": _evidence_record(
            "supported" if organization else "missing",
            source,
            source_url,
            organization,
            checked_at,
        ),
        "email": _evidence_record(
            contact_status,
            source,
            source_url,
            verification_note,
            checked_at,
        ),
        "source": _evidence_record(
            "supported" if source_url else "missing",
            source,
            source_url,
            source.notes,
            checked_at,
        ),
    }


def _evidence_record(
    status: str,
    source: SourceAssistedSourceRecord,
    source_url: str,
    evidence_snippet: str,
    checked_at: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "source_id": source.source_id,
        "source_url": source_url,
        "evidence_snippet": evidence_snippet,
        "checked_at": checked_at,
        "source_family": source.source_family,
    }


def _candidate_category(tier: str, title: str) -> str:
    if tier == "organization_only":
        return "organization_only"
    if tier == "not_found":
        return "not_found"
    if tier == "failed":
        return "failed"
    return "person_lead" if title else "organization_only"


def _primary_filter_reason(tier: str, contact_status: str, blocker_notes: str) -> str:
    if tier == "high_trust_usable":
        return "READY: source-assisted row has field support and usable contact evidence."
    if tier == "manual_lookup":
        return f"REVIEW: {blocker_notes or 'manual lookup required before CRM import.'}"
    if tier == "review":
        return f"REVIEW: {blocker_notes or 'source-supported row needs human review.'}"
    if tier == "organization_only":
        return "ORG-ONLY: source identified an organization but no validated person row."
    if tier == "not_found":
        return "NOT FOUND: source-assisted input did not yield an acceptable contact."
    return f"FAILED: {blocker_notes or contact_status or 'source evidence did not support the row.'}"


def _blocker_notes(tier: str, contact_status: str, verification_note: str, next_action: str) -> str:
    if tier == "high_trust_usable":
        return ""
    if contact_status in {"missing", "unsupported"}:
        return next_action or verification_note or "Direct contact is missing or unsupported."
    if contact_status == "failed":
        return verification_note or "Contact evidence failed validation."
    return verification_note or next_action


def _normalize_tier(explicit_tier: str, contact_status: str, title: str, source_url: str) -> str:
    tier = explicit_tier.strip()
    if tier == "READY":
        tier = "high_trust_usable"
    elif tier == "REVIEW":
        tier = "review"
    if tier in CANONICAL_TIERS:
        return tier
    if contact_status in CRM_READY_CONTACT_STATUSES and title and source_url:
        return "high_trust_usable"
    if contact_status in {"missing", "unsupported"} and title and source_url:
        return "manual_lookup"
    return "review"


def _normalize_contact_status(value: str) -> str:
    normalized = value.strip()
    legacy = {
        "Found": "verified_found",
        "Deduced": "deduced_with_pattern_evidence",
        "Missing": "missing",
    }
    normalized = legacy.get(normalized, normalized)
    return normalized if normalized in CONTACT_STATUSES else "unsupported"


def _safe_email(value: str) -> str:
    email = value.strip()
    if "redacted" in email.lower():
        return ""
    return email if _EMAIL_RE.match(email) else ""


def _safe_contact_value(value: str) -> str:
    contact_value = value.strip()
    if "redacted" in contact_value.lower():
        return ""
    return contact_value


def _empty_failed_row(row: ManualOracleRow, source: SourceAssistedSourceRecord) -> CompiledCandidateRow:
    return CompiledCandidateRow(
        candidate_id=_stable_id("r09frow", row.row_id),
        input_row_id=row.row_id,
        candidate_category="failed",
        tier="failed",
        organization=row.organization,
        title=row.title,
        lead_name="",
        email="",
        phone="",
        contact_status="failed",
        source_url=row.source_url,
        source_id=source.source_id,
        source_ids=(source.source_id,),
        source_family=source.source_family,
        source_reputation_signal=source.source_reputation_signal,
        input_method="manual_oracle_row_replay",
        verification_note=row.verification_note,
        blocker_notes="Compiler could not build a canonical row from the manual-oracle input.",
        next_action=row.next_action,
        primary_filter_reason="FAILED: Compiler could not build a canonical row from the manual-oracle input.",
        field_evidence={},
    )


def _source_key(url: str) -> str:
    return url.strip().lower().rstrip("/")


def _add_source_record(
    sources: dict[str, SourceAssistedSourceRecord],
    record: SourceAssistedSourceRecord,
) -> None:
    key = _source_key(record.url)
    existing = sources.get(key)
    if existing is None or _source_record_priority(record) > _source_record_priority(existing):
        sources[key] = record


def _source_record_priority(record: SourceAssistedSourceRecord) -> tuple[int, int]:
    return (
        0 if record.source_family in GENERIC_SEARCH_FAMILIES else 1,
        1 if record.source_reputation_signal.startswith("official") else 0,
    )


def _manual_oracle_aliases(row_id: str) -> tuple[str, ...]:
    clean = row_id.replace("april-nm-", "").replace("-", "_")
    aliases = {row_id, clean}
    if clean.startswith("verified_"):
        aliases.add(clean.replace("verified_", "april-nm-verified-"))
    if clean.startswith("manual_lookup_"):
        aliases.add(clean.replace("manual_lookup_", "april-nm-manual-lookup-"))
    return tuple(aliases)


def _first_text(payload: Mapping[str, Any], *field_names: str) -> str:
    for field_name in field_names:
        value = payload.get(field_name)
        cleaned = _clean(value)
        if cleaned:
            return cleaned
    return ""


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _stable_id(prefix: str, *parts: str) -> str:
    identity = "|".join(part.strip().lower() for part in parts if part.strip())
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"
