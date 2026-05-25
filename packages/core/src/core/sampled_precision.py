from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .benchmark_suite import build_operator_evidence_fixture_pack
from .lead_quality_policy import (
    candidate_identity,
    lead_has_contact_support,
    lead_has_persona_support,
    lead_has_source_support,
    validation_status,
)
from .models import Candidate, Lead, LeadList


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


@dataclass(frozen=True, slots=True)
class SampledPrecisionRow:
    benchmark_id: str
    row_index: int
    candidate_category: str
    tier: str | None
    name: str | None
    title: str | None
    organization: str | None
    right_persona: bool
    right_organization: bool
    source_supported: bool
    contact_supported: bool
    unsupported_email: bool
    fake_email: bool
    review_notes: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "row_index": self.row_index,
            "candidate_category": self.candidate_category,
            "tier": self.tier,
            "name": self.name,
            "title": self.title,
            "organization": self.organization,
            "right_persona": self.right_persona,
            "right_organization": self.right_organization,
            "source_supported": self.source_supported,
            "contact_supported": self.contact_supported,
            "unsupported_email": self.unsupported_email,
            "fake_email": self.fake_email,
            "review_notes": self.review_notes,
        }


@dataclass(frozen=True, slots=True)
class SampledPrecisionPacket:
    packet_id: str
    sampled_row_count: int
    persona_precision: float
    organization_precision: float
    source_support_precision: float
    contact_support_precision: float
    unsupported_email_count: int
    fake_email_count: int
    green_precision_floor_met: bool
    rows: tuple[SampledPrecisionRow, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "sampled_row_count": self.sampled_row_count,
            "persona_precision": self.persona_precision,
            "organization_precision": self.organization_precision,
            "source_support_precision": self.source_support_precision,
            "contact_support_precision": self.contact_support_precision,
            "unsupported_email_count": self.unsupported_email_count,
            "fake_email_count": self.fake_email_count,
            "green_precision_floor_met": self.green_precision_floor_met,
            "rows": [row.to_payload() for row in self.rows],
        }


def _review_notes(candidate: Candidate) -> str:
    statuses = [
        f"name={validation_status(candidate, 'name')}",
        f"title={validation_status(candidate, 'title')}",
        f"organization={validation_status(candidate, 'organization')}",
        f"source={validation_status(candidate, 'source')}",
        f"email={validation_status(candidate, 'email')}",
    ]
    reason = getattr(candidate, "primary_filter_reason", "") or getattr(candidate, "explanation", "")
    return "; ".join([*statuses, f"reason={reason}"]).strip()


def _row_from_candidate(benchmark_id: str, row_index: int, candidate: Candidate) -> SampledPrecisionRow:
    identity = candidate_identity(candidate)
    right_persona = lead_has_persona_support(candidate)
    right_organization = validation_status(candidate, "organization") == "supported"
    source_supported = lead_has_source_support(candidate) or validation_status(candidate, "source") == "supported"
    contact_supported = lead_has_contact_support(candidate)
    email_status = validation_status(candidate, "email")
    email_value = candidate.email.strip() if isinstance(candidate, Lead) else ""
    unsupported_email = bool(email_value) and email_status == "unsupported"
    fake_email = bool(email_value) and email_status == "failed"
    return SampledPrecisionRow(
        benchmark_id=benchmark_id,
        row_index=row_index,
        candidate_category=str(identity["candidate_category"]),
        tier=identity["tier"],
        name=identity["name"],
        title=identity["title"],
        organization=identity["organization"],
        right_persona=right_persona,
        right_organization=right_organization,
        source_supported=source_supported,
        contact_supported=contact_supported,
        unsupported_email=unsupported_email,
        fake_email=fake_email,
        review_notes=_review_notes(candidate),
    )


def _deterministic_sample(candidates: Sequence[Candidate], sample_size: int) -> list[tuple[int, Candidate]]:
    if sample_size <= 0:
        return []
    indexed = list(enumerate(candidates))
    person_rows = [(index, candidate) for index, candidate in indexed if isinstance(candidate, Lead)]
    nonperson_rows = [(index, candidate) for index, candidate in indexed if not isinstance(candidate, Lead)]
    return [*person_rows, *nonperson_rows][:sample_size]


def build_sampled_precision_packet(
    rows_by_benchmark: Mapping[str, Sequence[Candidate]],
    *,
    sample_size_per_case: int = 10,
    packet_id: str = "required_suite_sampled_precision",
) -> SampledPrecisionPacket:
    rows: list[SampledPrecisionRow] = []
    for benchmark_id in sorted(rows_by_benchmark):
        for row_index, candidate in _deterministic_sample(rows_by_benchmark[benchmark_id], sample_size_per_case):
            rows.append(_row_from_candidate(benchmark_id, row_index, candidate))

    sampled_count = len(rows)
    persona_count = sum(row.right_persona for row in rows)
    organization_count = sum(row.right_organization for row in rows)
    source_count = sum(row.source_supported for row in rows)
    contact_count = sum(row.contact_supported for row in rows)
    unsupported_email_count = sum(row.unsupported_email for row in rows)
    fake_email_count = sum(row.fake_email for row in rows)
    persona_precision = _rate(persona_count, sampled_count)
    organization_precision = _rate(organization_count, sampled_count)
    source_support_precision = _rate(source_count, sampled_count)
    contact_support_precision = _rate(contact_count, sampled_count)
    green_precision_floor_met = (
        persona_precision >= 0.7
        and organization_precision >= 0.7
        and source_support_precision >= 0.7
        and unsupported_email_count == 0
        and fake_email_count == 0
    )
    return SampledPrecisionPacket(
        packet_id=packet_id,
        sampled_row_count=sampled_count,
        persona_precision=persona_precision,
        organization_precision=organization_precision,
        source_support_precision=source_support_precision,
        contact_support_precision=contact_support_precision,
        unsupported_email_count=unsupported_email_count,
        fake_email_count=fake_email_count,
        green_precision_floor_met=green_precision_floor_met,
        rows=tuple(rows),
    )


def _load_candidates(path: Path) -> list[Candidate]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    leads = payload.get("leads") if isinstance(payload, dict) else None
    if not isinstance(leads, list):
        return []
    return list(LeadList.model_validate({"leads": leads}).leads)


def build_sampled_precision_packet_from_output_root(
    output_root: Path,
    *,
    sample_size_per_case: int = 10,
) -> SampledPrecisionPacket:
    fixture_pack = build_operator_evidence_fixture_pack()
    rows_by_benchmark: dict[str, list[Candidate]] = {}
    for case in fixture_pack.cases:
        payload_path = output_root / f"{case.benchmark_id}.json"
        rows_by_benchmark[case.benchmark_id] = _load_candidates(payload_path) if payload_path.exists() else []
    return build_sampled_precision_packet(rows_by_benchmark, sample_size_per_case=sample_size_per_case)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build deterministic sampled precision packet for benchmark outputs.")
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--sample-size-per-case", type=int, default=10)
    parser.add_argument("--write-json", type=Path, default=None)
    args = parser.parse_args(argv)

    packet = build_sampled_precision_packet_from_output_root(
        args.output_root,
        sample_size_per_case=args.sample_size_per_case,
    )
    payload = packet.to_payload()
    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
