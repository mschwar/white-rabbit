from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Sequence

from .models import Candidate, Lead

QualityArtifactKind = Literal["run", "benchmark"]

_PERSONAL_FIELD_STATUSES = ("supported", "unsupported", "missing", "failed")
_CONTACT_STATUSES = (
    "verified_found",
    "deduced_with_pattern_evidence",
    "missing",
    "failed",
    "unsupported",
)
_CANDIDATE_CATEGORIES = ("person_lead", "organization_only", "not_found", "failed")
_USABLE_CONTACT_STATUSES = {"verified_found", "deduced_with_pattern_evidence"}
_DEFAULT_QUALITY_GATE_THRESHOLDS = {
    "minimum_usable_count": 1,
    "minimum_precision_rate": 0.5,
    "minimum_persona_match_rate": 0.5,
    "minimum_contact_quality_rate": 0.5,
    "minimum_source_support_rate": 0.5,
    "maximum_fake_email_count": 0,
    "maximum_unsupported_email_count": 0,
    "maximum_high_noise_rate": 0.4,
}


def _seeded_counter(keys: Sequence[str]) -> Counter[str]:
    return Counter({key: 0 for key in keys})


def _nested_status_counters() -> dict[str, Counter[str]]:
    return {
        "name": _seeded_counter(_PERSONAL_FIELD_STATUSES),
        "title": _seeded_counter(_PERSONAL_FIELD_STATUSES),
        "organization": _seeded_counter(_PERSONAL_FIELD_STATUSES),
        "source": _seeded_counter(_PERSONAL_FIELD_STATUSES),
        "email": _seeded_counter(_CONTACT_STATUSES),
        "phone": _seeded_counter(_CONTACT_STATUSES),
    }


def _rate(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(count / total, 3)


@dataclass(frozen=True, slots=True)
class QualityReport:
    artifact_kind: QualityArtifactKind
    artifact_id: str | None = None
    query: str | None = None
    total_candidates: int = 0
    usable_count: int = 0
    precision_rate: float = 0.0
    person_lead_count: int = 0
    organization_only_count: int = 0
    not_found_count: int = 0
    failed_count: int = 0
    persona_match_count: int = 0
    persona_match_rate: float = 0.0
    contact_quality_count: int = 0
    contact_quality_rate: float = 0.0
    source_support_count: int = 0
    source_support_rate: float = 0.0
    fake_email_count: int = 0
    unsupported_email_count: int = 0
    high_noise_count: int = 0
    high_noise_rate: float = 0.0
    quality_gate_passed: bool = False
    quality_gate_failures: tuple[str, ...] = ()
    quality_gate_thresholds: dict[str, int | float] = field(default_factory=dict)
    candidate_category_counts: dict[str, int] = field(default_factory=dict)
    validation_status_counts: dict[str, dict[str, int]] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "artifact_kind": self.artifact_kind,
            "artifact_id": self.artifact_id,
            "query": self.query,
            "total_candidates": self.total_candidates,
            "usable_count": self.usable_count,
            "precision_rate": self.precision_rate,
            "person_lead_count": self.person_lead_count,
            "organization_only_count": self.organization_only_count,
            "not_found_count": self.not_found_count,
            "failed_count": self.failed_count,
            "persona_match_count": self.persona_match_count,
            "persona_match_rate": self.persona_match_rate,
            "contact_quality_count": self.contact_quality_count,
            "contact_quality_rate": self.contact_quality_rate,
            "source_support_count": self.source_support_count,
            "source_support_rate": self.source_support_rate,
            "fake_email_count": self.fake_email_count,
            "unsupported_email_count": self.unsupported_email_count,
            "high_noise_count": self.high_noise_count,
            "high_noise_rate": self.high_noise_rate,
            "quality_gate_passed": self.quality_gate_passed,
            "quality_gate_failures": list(self.quality_gate_failures),
            "quality_gate_thresholds": dict(self.quality_gate_thresholds),
            "candidate_category_counts": dict(self.candidate_category_counts),
            "validation_status_counts": {
                field_name: dict(counts) for field_name, counts in self.validation_status_counts.items()
            },
        }


def _evaluate_quality_gate(
    *,
    total_candidates: int,
    usable_count: int,
    precision_rate: float,
    persona_match_rate: float,
    contact_quality_rate: float,
    source_support_rate: float,
    fake_email_count: int,
    unsupported_email_count: int,
    high_noise_rate: float,
    thresholds: Mapping[str, int | float],
) -> tuple[bool, tuple[str, ...]]:
    failures: list[str] = []

    if total_candidates == 0:
        failures.append("no_candidates")
    if usable_count < thresholds["minimum_usable_count"]:
        failures.append("zero_usable_candidates")
    if precision_rate < thresholds["minimum_precision_rate"]:
        failures.append("low_precision_rate")
    if persona_match_rate < thresholds["minimum_persona_match_rate"]:
        failures.append("low_persona_match_rate")
    if contact_quality_rate < thresholds["minimum_contact_quality_rate"]:
        failures.append("low_contact_quality_rate")
    if source_support_rate < thresholds["minimum_source_support_rate"]:
        failures.append("low_source_support_rate")
    if fake_email_count > thresholds["maximum_fake_email_count"]:
        failures.append("fake_emails_present")
    if unsupported_email_count > thresholds["maximum_unsupported_email_count"]:
        failures.append("unsupported_emails_present")
    if high_noise_rate > thresholds["maximum_high_noise_rate"]:
        failures.append("high_noise_rate")

    return not failures, tuple(failures)


def build_quality_report(
    candidates: Sequence[Candidate],
    *,
    artifact_kind: QualityArtifactKind = "run",
    artifact_id: str | None = None,
    query: str | None = None,
    quality_gate_thresholds: Mapping[str, int | float] | None = None,
) -> QualityReport:
    category_counts = _seeded_counter(_CANDIDATE_CATEGORIES)
    validation_status_counts = _nested_status_counters()

    usable_count = 0
    person_lead_count = 0
    organization_only_count = 0
    not_found_count = 0
    failed_count = 0
    persona_match_count = 0
    contact_quality_count = 0
    source_support_count = 0
    fake_email_count = 0
    unsupported_email_count = 0
    high_noise_count = 0

    for candidate in candidates:
        category = candidate.candidate_category
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1

        validation = candidate.validation
        for field_name in ("name", "title", "organization", "source", "email", "phone"):
            status = getattr(getattr(validation, field_name), "status", "unsupported")
            validation_status_counts[field_name][status] += 1

        if category == "person_lead":
            person_lead_count += 1
            if isinstance(candidate, Lead) and candidate.gate_passed:
                usable_count += 1

            if all(
                getattr(validation, field_name).status == "supported"
                for field_name in ("name", "title", "organization")
            ):
                persona_match_count += 1

        elif category == "organization_only":
            organization_only_count += 1
        elif category == "not_found":
            not_found_count += 1
        elif category == "failed":
            failed_count += 1

        if validation.email.status in _USABLE_CONTACT_STATUSES:
            contact_quality_count += 1
        elif validation.email.status == "failed":
            fake_email_count += 1
        elif validation.email.status == "unsupported":
            unsupported_email_count += 1

        if validation.source.status == "supported":
            source_support_count += 1
        if category in {"organization_only", "failed"} or validation.email.status in {"failed", "unsupported"}:
            high_noise_count += 1

    total_candidates = len(candidates)
    high_noise_rate = _rate(high_noise_count, total_candidates)
    precision_rate = _rate(usable_count, total_candidates)
    persona_match_rate = _rate(persona_match_count, total_candidates)
    contact_quality_rate = _rate(contact_quality_count, total_candidates)
    source_support_rate = _rate(source_support_count, total_candidates)
    thresholds = dict(_DEFAULT_QUALITY_GATE_THRESHOLDS)
    if quality_gate_thresholds:
        thresholds.update(quality_gate_thresholds)
    quality_gate_passed, quality_gate_failures = _evaluate_quality_gate(
        total_candidates=total_candidates,
        usable_count=usable_count,
        precision_rate=precision_rate,
        persona_match_rate=persona_match_rate,
        contact_quality_rate=contact_quality_rate,
        source_support_rate=source_support_rate,
        fake_email_count=fake_email_count,
        unsupported_email_count=unsupported_email_count,
        high_noise_rate=high_noise_rate,
        thresholds=thresholds,
    )

    return QualityReport(
        artifact_kind=artifact_kind,
        artifact_id=artifact_id,
        query=query,
        total_candidates=total_candidates,
        usable_count=usable_count,
        precision_rate=precision_rate,
        person_lead_count=person_lead_count,
        organization_only_count=organization_only_count,
        not_found_count=not_found_count,
        failed_count=failed_count,
        persona_match_count=persona_match_count,
        persona_match_rate=persona_match_rate,
        contact_quality_count=contact_quality_count,
        contact_quality_rate=contact_quality_rate,
        source_support_count=source_support_count,
        source_support_rate=source_support_rate,
        fake_email_count=fake_email_count,
        unsupported_email_count=unsupported_email_count,
        high_noise_count=high_noise_count,
        high_noise_rate=high_noise_rate,
        quality_gate_passed=quality_gate_passed,
        quality_gate_failures=quality_gate_failures,
        quality_gate_thresholds=thresholds,
        candidate_category_counts=dict(category_counts),
        validation_status_counts={
            field_name: dict(counts) for field_name, counts in validation_status_counts.items()
        },
    )
