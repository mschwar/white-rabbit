from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Mapping

from core.models import Lead, LeadList
from core.query_guardrails import QueryGuardrailStatus, evaluate_query_guardrails
from core.quality_report import QualityReport, build_quality_report

BenchmarkTheme = Literal["named_account", "broad_b2b", "privacy_rejection"]
BenchmarkDimension = Literal["persona", "contact", "source", "privacy_refusal"]
QuerySourceKind = Literal["verbatim_operator_source", "reconstructed_from_audit", "public_guardrail_fixture"]


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    source_id: str
    location: str
    summary: str

    def to_payload(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "location": self.location,
            "summary": self.summary,
        }


@dataclass(frozen=True, slots=True)
class ReplayArtifact:
    path: str
    kind: Literal["live_json", "http_status", "worksheet_readback", "guardrail_response"]
    notes: str = ""

    def to_payload(self) -> dict[str, str]:
        return {
            "path": self.path,
            "kind": self.kind,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class OperatorFixtureCase:
    benchmark_id: str
    prompt_label: str
    query: str
    query_source_kind: QuerySourceKind
    theme: BenchmarkTheme
    persona: str
    geography: str
    expected_guardrail_status: QueryGuardrailStatus
    expected_output_tiers: tuple[str, ...]
    expected_target_coverage: tuple[str, ...] = ()
    expected_min_categorized_rows: int = 0
    target_categorized_rows: int = 0
    privacy_safe_summary: str = ""
    evidence_references: tuple[EvidenceReference, ...] = ()
    replay_artifacts: tuple[ReplayArtifact, ...] = ()
    notes: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "prompt_label": self.prompt_label,
            "query": self.query,
            "query_source_kind": self.query_source_kind,
            "theme": self.theme,
            "persona": self.persona,
            "geography": self.geography,
            "expected_guardrail_status": self.expected_guardrail_status,
            "expected_output_tiers": list(self.expected_output_tiers),
            "expected_target_coverage": list(self.expected_target_coverage),
            "expected_min_categorized_rows": self.expected_min_categorized_rows,
            "target_categorized_rows": self.target_categorized_rows,
            "privacy_safe_summary": self.privacy_safe_summary,
            "evidence_references": [reference.to_payload() for reference in self.evidence_references],
            "replay_artifacts": [artifact.to_payload() for artifact in self.replay_artifacts],
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class OperatorEvidenceFixturePack:
    pack_id: str
    source: str
    cases: tuple[OperatorFixtureCase, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "pack_id": self.pack_id,
            "source": self.source,
            "cases": [case.to_payload() for case in self.cases],
        }


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    benchmark_id: str
    theme: BenchmarkTheme
    query: str
    persona: str
    expected_guardrail_status: QueryGuardrailStatus
    expected_persona_pass: bool
    expected_contact_pass: bool
    expected_source_pass: bool
    expected_privacy_refusal: bool
    notes: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "theme": self.theme,
            "query": self.query,
            "persona": self.persona,
            "expected_guardrail_status": self.expected_guardrail_status,
            "expected_persona_pass": self.expected_persona_pass,
            "expected_contact_pass": self.expected_contact_pass,
            "expected_source_pass": self.expected_source_pass,
            "expected_privacy_refusal": self.expected_privacy_refusal,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkSuite:
    suite_id: str
    source: str
    cases: tuple[BenchmarkCase, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "suite_id": self.suite_id,
            "source": self.source,
            "cases": [case.to_payload() for case in self.cases],
        }


@dataclass(frozen=True, slots=True)
class BenchmarkObservation:
    benchmark_id: str
    guardrail_status: QueryGuardrailStatus
    persona_pass: bool
    contact_pass: bool
    source_pass: bool
    privacy_refusal: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "guardrail_status": self.guardrail_status,
            "persona_pass": self.persona_pass,
            "contact_pass": self.contact_pass,
            "source_pass": self.source_pass,
            "privacy_refusal": self.privacy_refusal,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkSuiteReport:
    suite_id: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    persona_pass_cases: int
    contact_pass_cases: int
    source_pass_cases: int
    privacy_refusal_cases: int
    guardrail_mismatches: tuple[str, ...] = ()
    observation_mismatches: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReplayBenchmarkObservation:
    benchmark_id: str
    guardrail_status: QueryGuardrailStatus
    persona_pass: bool
    contact_pass: bool
    source_pass: bool
    privacy_refusal: bool
    categorized_row_count: int
    person_lead_count: int
    high_trust_usable_count: int
    review_count: int
    organization_only_count: int
    not_found_count: int
    failed_count: int
    expected_target_coverage_count: int = 0
    expected_target_coverage_missing: tuple[str, ...] = ()
    minimum_escape_rows: int = 0
    target_categorized_rows: int = 0
    escape_velocity_floor_met: bool = False
    target_volume_floor_met: bool = False
    high_volume_floor_met: bool = False
    volume_floor_status: str = "not_evaluated"
    funnel_counts: dict[str, int] | None = None
    http_status: int | None = None
    error_code: str | None = None
    quality_report: QualityReport | None = None


_REPO_ROOT = Path(__file__).resolve().parents[4]


def _resolve_repo_path(path: str, *, repo_root: Path | None = None) -> Path:
    return (repo_root or _REPO_ROOT) / path


def _artifact_payload(case: OperatorFixtureCase, *, repo_root: Path | None = None) -> dict[str, Any]:
    for artifact in case.replay_artifacts:
        if artifact.kind in {"live_json", "guardrail_response"}:
            payload_path = _resolve_repo_path(artifact.path, repo_root=repo_root)
            return json.loads(payload_path.read_text(encoding="utf-8"))
    return {}


def _artifact_http_status(case: OperatorFixtureCase, *, repo_root: Path | None = None) -> int | None:
    for artifact in case.replay_artifacts:
        if artifact.kind == "http_status":
            status_path = _resolve_repo_path(artifact.path, repo_root=repo_root)
            raw = status_path.read_text(encoding="utf-8").strip()
            if raw:
                return int(raw)
    return None


def _payload_guardrail_status(payload: Mapping[str, Any], query: str) -> QueryGuardrailStatus:
    query_guardrail = payload.get("query_guardrail")
    if isinstance(query_guardrail, Mapping) and isinstance(query_guardrail.get("status"), str):
        return str(query_guardrail.get("status"))
    return evaluate_query_guardrails(query).status


def _row_supports_target(candidate: Any, target: str) -> bool:
    lowered_target = target.lower()
    haystacks = (
        getattr(candidate, "organization", None),
        getattr(candidate, "name", None),
        getattr(candidate, "searched_target", None),
        getattr(candidate, "failure_reason", None),
    )
    return any(isinstance(value, str) and lowered_target in value.lower() for value in haystacks)


def _parse_replay_candidates(payload: Mapping[str, Any]) -> list[Any]:
    leads = payload.get("leads")
    if not isinstance(leads, list):
        return []
    return LeadList.model_validate({"leads": leads}).leads


def _empty_quality_counts() -> dict[str, int]:
    return {
        "total_candidates": 0,
        "person_lead_count": 0,
        "persona_match_count": 0,
        "usable_count": 0,
        "contact_quality_count": 0,
        "source_support_count": 0,
    }


def _empty_funnel_counts() -> dict[str, int]:
    return {
        "raw_vendor_hits": 0,
        "deduped_sources": 0,
        "source_snapshots": 0,
        "extracted_candidates": 0,
        "categorized_rows": 0,
        "person_rows": 0,
        "persona_supported_rows": 0,
        "source_supported_rows": 0,
        "high_trust_usable_rows": 0,
        "contact_quality_passes": 0,
        "contact_evidence_candidates_searched": 0,
        "contact_evidence_searches": 0,
        "contact_evidence_contacts_acquired": 0,
        "contact_evidence_field_corroborations": 0,
        "contact_evidence_conflicting_signals": 0,
        "contact_evidence_review_to_high_trust": 0,
    }


def _payload_funnel_counts(
    payload: Mapping[str, Any],
    *,
    quality_counts: Mapping[str, int],
) -> dict[str, int]:
    metrics = payload.get("metrics")
    if isinstance(metrics, Mapping) and isinstance(metrics.get("funnel_counts"), Mapping):
        return {
            key: int(metrics["funnel_counts"].get(key, 0) or 0)
            for key in _empty_funnel_counts()
        }

    counts = _empty_funnel_counts()
    counts.update({
        "raw_vendor_hits": 0,
        "deduped_sources": 0,
        "source_snapshots": 0,
        "extracted_candidates": quality_counts["total_candidates"],
        "categorized_rows": quality_counts["total_candidates"],
        "person_rows": quality_counts["person_lead_count"],
        "persona_supported_rows": quality_counts["persona_match_count"],
        "source_supported_rows": quality_counts["source_support_count"],
        "high_trust_usable_rows": quality_counts["usable_count"],
        "contact_quality_passes": quality_counts["contact_quality_count"],
    })
    return counts


def _volume_floor_status(
    *,
    case: OperatorFixtureCase,
    privacy_refusal: bool,
    categorized_row_count: int,
) -> tuple[bool, bool, bool, str]:
    if privacy_refusal:
        return True, True, True, "expected_privacy_refusal"

    escape_velocity_floor_met = categorized_row_count >= case.expected_min_categorized_rows
    target_volume_floor_met = categorized_row_count >= case.target_categorized_rows
    if case.theme == "broad_b2b":
        high_volume_floor_met = target_volume_floor_met
        status = "target_met" if target_volume_floor_met else "below_active_50_plus_target"
    else:
        high_volume_floor_met = escape_velocity_floor_met
        status = "minimum_met" if escape_velocity_floor_met else "below_minimum_escape_floor"

    return escape_velocity_floor_met, target_volume_floor_met, high_volume_floor_met, status


def _build_observation_from_payload(
    case: OperatorFixtureCase,
    payload: Mapping[str, Any],
    *,
    http_status: int | None = None,
) -> ReplayBenchmarkObservation:
    candidates = _parse_replay_candidates(payload)
    guardrail_status = _payload_guardrail_status(payload, case.query)
    privacy_refusal = (
        case.theme == "privacy_rejection"
        and guardrail_status == "blocked"
        and not candidates
        and isinstance(payload.get("error"), str)
    )
    quality_report = None
    if not privacy_refusal:
        quality_report = build_quality_report(
            candidates,
            artifact_kind="benchmark",
            artifact_id=case.benchmark_id,
            query=case.query,
        )
        quality_counts = {
            "total_candidates": quality_report.total_candidates,
            "person_lead_count": quality_report.person_lead_count,
            "persona_match_count": quality_report.persona_match_count,
            "usable_count": quality_report.usable_count,
            "contact_quality_count": quality_report.contact_quality_count,
            "source_support_count": quality_report.source_support_count,
        }
        thresholds = quality_report.quality_gate_thresholds
        persona_pass = quality_report.persona_match_rate >= thresholds["minimum_persona_match_rate"]
        contact_pass = (
            quality_report.contact_quality_rate >= thresholds["minimum_contact_quality_rate"]
            and quality_report.fake_email_count <= thresholds["maximum_fake_email_count"]
            and quality_report.unsupported_email_count <= thresholds["maximum_unsupported_email_count"]
            and quality_report.total_candidates > 0
        )
        source_pass = (
            quality_report.source_support_rate >= thresholds["minimum_source_support_rate"]
            and quality_report.total_candidates > 0
        )
    else:
        quality_counts = _empty_quality_counts()
        persona_pass = False
        contact_pass = False
        source_pass = False

    (
        escape_velocity_floor_met,
        target_volume_floor_met,
        high_volume_floor_met,
        volume_floor_status,
    ) = _volume_floor_status(
        case=case,
        privacy_refusal=privacy_refusal,
        categorized_row_count=quality_counts["total_candidates"],
    )
    funnel_counts = _payload_funnel_counts(payload, quality_counts=quality_counts)

    return ReplayBenchmarkObservation(
        benchmark_id=case.benchmark_id,
        guardrail_status=guardrail_status,
        persona_pass=persona_pass,
        contact_pass=contact_pass,
        source_pass=source_pass,
        privacy_refusal=privacy_refusal,
        categorized_row_count=quality_counts["total_candidates"],
        person_lead_count=quality_counts["person_lead_count"],
        high_trust_usable_count=quality_counts["usable_count"],
        review_count=quality_counts["person_lead_count"] - quality_counts["usable_count"],
        organization_only_count=quality_report.organization_only_count if quality_report else 0,
        not_found_count=quality_report.not_found_count if quality_report else 0,
        failed_count=quality_report.failed_count if quality_report else 0,
        expected_target_coverage_count=sum(
            1 for target in case.expected_target_coverage if any(_row_supports_target(candidate, target) for candidate in candidates)
        ),
        expected_target_coverage_missing=tuple(
            target
            for target in case.expected_target_coverage
            if not any(_row_supports_target(candidate, target) for candidate in candidates)
        ),
        minimum_escape_rows=case.expected_min_categorized_rows,
        target_categorized_rows=case.target_categorized_rows,
        escape_velocity_floor_met=escape_velocity_floor_met,
        target_volume_floor_met=target_volume_floor_met,
        high_volume_floor_met=high_volume_floor_met,
        volume_floor_status=volume_floor_status,
        funnel_counts=funnel_counts,
        http_status=http_status,
        error_code=payload.get("error_code") if isinstance(payload.get("error_code"), str) else None,
        quality_report=quality_report,
    )


def build_replay_benchmark_observations(
    fixture_pack: OperatorEvidenceFixturePack | None = None,
    *,
    repo_root: Path | None = None,
) -> dict[str, BenchmarkObservation]:
    fixture_pack = fixture_pack or build_operator_evidence_fixture_pack()
    observations: dict[str, BenchmarkObservation] = {}

    for case in fixture_pack.cases:
        payload = _artifact_payload(case, repo_root=repo_root)
        observations[case.benchmark_id] = _build_observation_from_payload(
            case,
            payload,
            http_status=_artifact_http_status(case, repo_root=repo_root),
        )

    return observations


def build_saved_benchmark_observations(
    output_root: Path,
    fixture_pack: OperatorEvidenceFixturePack | None = None,
) -> dict[str, ReplayBenchmarkObservation]:
    fixture_pack = fixture_pack or build_operator_evidence_fixture_pack()
    observations: dict[str, ReplayBenchmarkObservation] = {}

    for case in fixture_pack.cases:
        payload_path = output_root / f"{case.benchmark_id}.json"
        status_path = output_root / f"{case.benchmark_id}.http"
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        http_status = int(status_path.read_text(encoding="utf-8").strip()) if status_path.exists() else None
        observations[case.benchmark_id] = _build_observation_from_payload(case, payload, http_status=http_status)

    return observations


def build_operator_evidence_fixture_pack() -> OperatorEvidenceFixturePack:
    shared_b2b_tiers = (
        "high_trust_usable",
        "review",
        "organization_only",
        "not_found",
        "failed",
    )
    return OperatorEvidenceFixturePack(
        pack_id="operator_evidence_fixture_pack",
        source=(
            "Canonical reset prompts and replay artifacts for RG1. Private evidence is preserved as source IDs and "
            "privacy-safe summaries, not quoted thread dumps."
        ),
        cases=(
            OperatorFixtureCase(
                benchmark_id="thomas-arizona-k12",
                prompt_label="Thomas Arizona K-12 exact prompt",
                query=(
                    "name and email and phone number for these District Approx Size Tech Decision Maker Type Mesa Public "
                    "Schools 60k+ students CIO / Director of Technology; Chandler Unified School District 40k+ CTO / IT "
                    "Director; Peoria Unified School District 35k+ Technology Services; Gilbert Public Schools 30k+ CTO; "
                    "Deer Valley Unified School District 30k+ IT leadership; Paradise Valley Unified School District 25k+ "
                    "CIO/Technology; Dysart Unified School District 24k+ Director of Technology; Maricopa Unified School "
                    "District 9k+ Director of Technology"
                ),
                query_source_kind="verbatim_operator_source",
                theme="named_account",
                persona="district technology decision makers",
                geography="Arizona",
                expected_guardrail_status="needs_more_detail",
                expected_output_tiers=shared_b2b_tiers,
                expected_target_coverage=(
                    "Mesa Public Schools",
                    "Chandler Unified School District",
                    "Peoria Unified School District",
                    "Gilbert Public Schools",
                    "Deer Valley Unified School District",
                    "Paradise Valley Unified School District",
                    "Dysart Unified School District",
                    "Maricopa Unified School District",
                ),
                expected_min_categorized_rows=8,
                target_categorized_rows=8,
                privacy_safe_summary=(
                    "Thomas asked for a district-by-district contact comparison against workbook/PDF artifacts. This "
                    "fixture preserves the target list and workbook semantics without copying private email content."
                ),
                evidence_references=(
                    EvidenceReference(
                        source_id="GMAIL-THOMAS-01",
                        location="Gmail message ID 19e08ef2c7c42bf6",
                        summary="Initial benchmark request and exact Arizona K-12 prompt source.",
                    ),
                    EvidenceReference(
                        source_id="GMAIL-THOMAS-02",
                        location="Gmail message ID 19e08fb5a55a240d",
                        summary="Follow-up notes plus Arizona comparison PDF attachment reference.",
                    ),
                    EvidenceReference(
                        source_id="GMAIL-THOMAS-03",
                        location="Gmail message ID 19e092b5ad3e10a1",
                        summary="Workbook-quality follow-up with AZ_K12_VoIP_Targets.xlsx attachment reference.",
                    ),
                    EvidenceReference(
                        source_id="WB-AZ-01",
                        location="/Users/mschwar/Downloads/district_it_contacts_by_state_20260424_172807.xlsx",
                        summary="Corroborating workbook artifact used for district names and annotations.",
                    ),
                ),
                replay_artifacts=(
                    ReplayArtifact(
                        path="packages/core/tests/fixtures/arizona_k12_voip.json",
                        kind="worksheet_readback",
                        notes="Golden district coverage fixture with workbook annotations.",
                    ),
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/thomas-arizona-k12.json",
                        kind="live_json",
                        notes="Saved May 10 live response for replay comparison.",
                    ),
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/thomas-arizona-k12.http",
                        kind="http_status",
                        notes="Saved HTTP status for the live run.",
                    ),
                ),
                notes="Named-account benchmark: every district must resolve to a categorized output row.",
            ),
            OperatorFixtureCase(
                benchmark_id="lee-commodity-buyers",
                prompt_label="Lee commodity buyers prompt",
                query="commodity buyers at retail lumber yards in Washington",
                query_source_kind="reconstructed_from_audit",
                theme="broad_b2b",
                persona="commodity buyers",
                geography="Washington",
                expected_guardrail_status="needs_more_detail",
                expected_output_tiers=shared_b2b_tiers,
                expected_min_categorized_rows=10,
                target_categorized_rows=50,
                privacy_safe_summary=(
                    "Lee's operator signal prioritized direct person contacts over company-only rows. The exact replay "
                    "string is reconstructed from the saved live artifact because the private Gmail body is not copied "
                    "into the repo."
                ),
                evidence_references=(
                    EvidenceReference(
                        source_id="GMAIL-LEE-01",
                        location="Gmail message ID 19e0e8dcf8ad1322",
                        summary="Commodity-buyer prompt source and direct-person-contact requirement.",
                    ),
                    EvidenceReference(
                        source_id="GMAIL-LEE-02",
                        location="Gmail message ID 19e0eb0b801090da",
                        summary="CSV/export ordering and privacy caution for broad operator runs.",
                    ),
                ),
                replay_artifacts=(
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/lee-commodity-buyers.json",
                        kind="live_json",
                        notes="Saved May 10 live response for replay comparison.",
                    ),
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/lee-commodity-buyers.http",
                        kind="http_status",
                        notes="Saved HTTP status for the live run.",
                    ),
                ),
                notes="Broad-query benchmark: low single-digit rows are an explicit product failure.",
            ),
            OperatorFixtureCase(
                benchmark_id="healthcare-it-phoenix",
                prompt_label="Healthcare IT directors in Phoenix",
                query="healthcare IT directors in Phoenix",
                query_source_kind="public_guardrail_fixture",
                theme="broad_b2b",
                persona="healthcare IT directors",
                geography="Phoenix",
                expected_guardrail_status="clear",
                expected_output_tiers=shared_b2b_tiers,
                expected_min_categorized_rows=10,
                target_categorized_rows=50,
                privacy_safe_summary="Audit replay prompt used to test broad B2B healthcare coverage and export value.",
                replay_artifacts=(
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/healthcare-it-phoenix.json",
                        kind="live_json",
                        notes="Saved May 10 live response for replay comparison.",
                    ),
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/healthcare-it-phoenix.http",
                        kind="http_status",
                        notes="Saved HTTP status for the live run.",
                    ),
                ),
                notes="Broad-query benchmark: current export path works mechanically but still returns non-usable rows.",
            ),
            OperatorFixtureCase(
                benchmark_id="finance-cisos-new-york",
                prompt_label="Finance CISOs in New York",
                query="finance CISOs at financial services firms in New York",
                query_source_kind="public_guardrail_fixture",
                theme="broad_b2b",
                persona="finance CISOs",
                geography="New York",
                expected_guardrail_status="clear",
                expected_output_tiers=shared_b2b_tiers,
                expected_min_categorized_rows=10,
                target_categorized_rows=50,
                privacy_safe_summary="Audit replay prompt used to test finance persona matching and duplicate/conflict handling.",
                replay_artifacts=(
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/finance-cisos-ny.json",
                        kind="live_json",
                        notes="Saved May 10 live response for replay comparison.",
                    ),
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/finance-cisos-ny.http",
                        kind="http_status",
                        notes="Saved HTTP status for the live run.",
                    ),
                ),
                notes="Broad-query benchmark: duplicate/conflicting rows must degrade cleanly instead of looking strong.",
            ),
            OperatorFixtureCase(
                benchmark_id="manufacturing-ops-detroit",
                prompt_label="Manufacturing operations leaders in Detroit",
                query="manufacturing operations leaders in Detroit",
                query_source_kind="public_guardrail_fixture",
                theme="broad_b2b",
                persona="manufacturing operations leaders",
                geography="Detroit",
                expected_guardrail_status="clear",
                expected_output_tiers=shared_b2b_tiers,
                expected_min_categorized_rows=10,
                target_categorized_rows=50,
                privacy_safe_summary=(
                    "Audit replay prompt used to preserve the current parse-crash failure. The fixture exists so R02 and "
                    "R03 can prove the query degrades into explicit rows instead of a 503."
                ),
                replay_artifacts=(
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/manufacturing-ops-detroit.json",
                        kind="live_json",
                        notes="Saved May 10 failure payload with parse-validation details.",
                    ),
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/manufacturing-ops-detroit.http",
                        kind="http_status",
                        notes="Saved HTTP status for the live run.",
                    ),
                ),
                notes="Broad-query benchmark: role-as-name parse failure must become a recoverable case in later gates.",
            ),
            OperatorFixtureCase(
                benchmark_id="privacy-reject-homeowner-phones",
                prompt_label="B2C/private phone guardrail",
                query="personal phone numbers for homeowners in Texas",
                query_source_kind="public_guardrail_fixture",
                theme="privacy_rejection",
                persona="privacy-sensitive personal contact request",
                geography="Texas",
                expected_guardrail_status="blocked",
                expected_output_tiers=(),
                expected_min_categorized_rows=0,
                target_categorized_rows=0,
                privacy_safe_summary=(
                    "Guardrail fixture based on the May 10 privacy audit and Lee's caution that the product must refuse "
                    "consumer/private-person targeting before search."
                ),
                evidence_references=(
                    EvidenceReference(
                        source_id="GMAIL-LEE-02",
                        location="Gmail message ID 19e0eb0b801090da",
                        summary="Lee highlighted privacy caution and CRM-safe export expectations.",
                    ),
                ),
                replay_artifacts=(
                    ReplayArtifact(
                        path="audits/raw/zero-trust-2026-05-10/live/b2c-privacy-guardrail.json",
                        kind="guardrail_response",
                        notes="Saved blocked response for replay comparison.",
                    ),
                ),
                notes="Privacy fixture: must block before discovery, extraction, or validation spend.",
            ),
        ),
    )


def build_required_benchmark_suite(
    fixture_pack: OperatorEvidenceFixturePack | None = None,
) -> BenchmarkSuite:
    fixture_pack = fixture_pack or build_operator_evidence_fixture_pack()
    return BenchmarkSuite(
        suite_id="required_lead_quality_suite",
        source="Operator evidence fixture pack plus privacy guardrail fixture; private evidence stays as IDs and summaries.",
        cases=tuple(
            BenchmarkCase(
                benchmark_id=case.benchmark_id,
                theme=case.theme,
                query=case.query,
                persona=case.persona,
                expected_guardrail_status=case.expected_guardrail_status,
                expected_persona_pass=case.expected_guardrail_status == "clear",
                expected_contact_pass=case.expected_guardrail_status == "clear",
                expected_source_pass=case.expected_guardrail_status == "clear",
                expected_privacy_refusal=case.expected_guardrail_status == "blocked",
                notes=case.notes,
            )
            for case in fixture_pack.cases
        ),
    )


def validate_required_benchmark_suite(suite: BenchmarkSuite | None = None) -> tuple[str, ...]:
    suite = suite or build_required_benchmark_suite()
    mismatches: list[str] = []

    for case in suite.cases:
        guardrail_result = evaluate_query_guardrails(case.query)
        if guardrail_result.status != case.expected_guardrail_status:
            mismatches.append(
                f"{case.benchmark_id}: expected guardrail {case.expected_guardrail_status}, "
                f"got {guardrail_result.status}"
            )

    return tuple(mismatches)


def evaluate_required_benchmark_suite(
    suite: BenchmarkSuite,
    observations: Mapping[str, BenchmarkObservation],
) -> BenchmarkSuiteReport:
    passed_cases = 0
    guardrail_mismatches: list[str] = []
    observation_mismatches: list[str] = []

    persona_pass_cases = 0
    contact_pass_cases = 0
    source_pass_cases = 0
    privacy_refusal_cases = 0

    for case in suite.cases:
        observation = observations.get(case.benchmark_id)
        if observation is None:
            observation_mismatches.append(f"{case.benchmark_id}: missing observation")
            continue

        case_mismatches: list[str] = []

        if observation.guardrail_status != case.expected_guardrail_status:
            guardrail_mismatches.append(
                f"{case.benchmark_id}: expected guardrail {case.expected_guardrail_status}, got {observation.guardrail_status}"
            )
            case_mismatches.append("guardrail")

        if observation.persona_pass != case.expected_persona_pass:
            case_mismatches.append("persona")
        if observation.contact_pass != case.expected_contact_pass:
            case_mismatches.append("contact")
        if observation.source_pass != case.expected_source_pass:
            case_mismatches.append("source")
        if observation.privacy_refusal != case.expected_privacy_refusal:
            case_mismatches.append("privacy_refusal")
        if getattr(observation, "expected_target_coverage_missing", ()):
            case_mismatches.append("coverage")
        if getattr(observation, "high_volume_floor_met", True) is False:
            case_mismatches.append("volume")

        persona_pass_cases += int(observation.persona_pass)
        contact_pass_cases += int(observation.contact_pass)
        source_pass_cases += int(observation.source_pass)
        privacy_refusal_cases += int(observation.privacy_refusal)

        if case_mismatches:
            observation_mismatches.append(f"{case.benchmark_id}: {', '.join(case_mismatches)}")
            continue

        passed_cases += 1

    total_cases = len(suite.cases)
    failed_cases = total_cases - passed_cases

    return BenchmarkSuiteReport(
        suite_id=suite.suite_id,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        persona_pass_cases=persona_pass_cases,
        contact_pass_cases=contact_pass_cases,
        source_pass_cases=source_pass_cases,
        privacy_refusal_cases=privacy_refusal_cases,
        guardrail_mismatches=tuple(guardrail_mismatches),
        observation_mismatches=tuple(observation_mismatches),
    )
