from __future__ import annotations

import json
from pathlib import Path

from core.benchmark_suite import (
    BenchmarkObservation,
    build_operator_evidence_fixture_pack,
    build_required_benchmark_suite,
    evaluate_required_benchmark_suite,
    validate_required_benchmark_suite,
)
from core.query_guardrails import evaluate_query_guardrails


FIXTURE_PATH = Path(__file__).with_name("fixtures") / "benchmark_suite.json"
OPERATOR_FIXTURE_PATH = Path(__file__).with_name("fixtures") / "operator_evidence_fixture_pack.json"


def _load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _load_operator_fixture() -> dict[str, object]:
    return json.loads(OPERATOR_FIXTURE_PATH.read_text(encoding="utf-8"))


def _build_observations():
    suite = build_required_benchmark_suite()
    observations: dict[str, BenchmarkObservation] = {}

    for case in suite.cases:
        observations[case.benchmark_id] = BenchmarkObservation(
            benchmark_id=case.benchmark_id,
            guardrail_status=evaluate_query_guardrails(case.query).status,
            persona_pass=case.expected_persona_pass,
            contact_pass=case.expected_contact_pass,
            source_pass=case.expected_source_pass,
            privacy_refusal=case.expected_privacy_refusal,
        )

    return suite, observations


def test_operator_evidence_fixture_pack_matches_canonical_definition():
    fixture_pack = build_operator_evidence_fixture_pack()

    assert _load_operator_fixture() == fixture_pack.to_payload()


def test_operator_evidence_fixture_pack_preserves_real_reset_prompts_and_private_source_ids():
    fixture_pack = build_operator_evidence_fixture_pack()
    case_ids = {case.benchmark_id for case in fixture_pack.cases}

    assert case_ids == {
        "thomas-arizona-k12",
        "lee-commodity-buyers",
        "healthcare-it-phoenix",
        "finance-cisos-new-york",
        "manufacturing-ops-detroit",
        "privacy-reject-homeowner-phones",
    }

    arizona_case = next(case for case in fixture_pack.cases if case.benchmark_id == "thomas-arizona-k12")
    lee_case = next(case for case in fixture_pack.cases if case.benchmark_id == "lee-commodity-buyers")
    privacy_case = next(case for case in fixture_pack.cases if case.benchmark_id == "privacy-reject-homeowner-phones")

    assert arizona_case.query_source_kind == "verbatim_operator_source"
    assert arizona_case.expected_min_categorized_rows == 8
    assert arizona_case.target_categorized_rows == 8
    assert {reference.source_id for reference in arizona_case.evidence_references} == {
        "GMAIL-THOMAS-01",
        "GMAIL-THOMAS-02",
        "GMAIL-THOMAS-03",
        "WB-AZ-01",
    }
    assert "packages/core/tests/fixtures/arizona_k12_voip.json" in {
        artifact.path for artifact in arizona_case.replay_artifacts
    }
    assert lee_case.query_source_kind == "reconstructed_from_audit"
    assert {reference.source_id for reference in lee_case.evidence_references} == {
        "GMAIL-LEE-01",
        "GMAIL-LEE-02",
    }
    assert lee_case.target_categorized_rows == 50
    assert privacy_case.expected_guardrail_status == "blocked"
    assert privacy_case.expected_output_tiers == ()
    assert arizona_case.expected_guardrail_status == "needs_more_detail"
    assert lee_case.expected_guardrail_status == "needs_more_detail"


def test_required_benchmark_suite_fixture_matches_canonical_definition():
    suite = build_required_benchmark_suite()
    assert _load_fixture() == suite.to_payload()


def test_required_benchmark_suite_covers_required_audit_queries_and_guardrails():
    suite = build_required_benchmark_suite()
    fixture_pack = build_operator_evidence_fixture_pack()
    queries = {case.query for case in suite.cases}
    themes = {case.theme for case in suite.cases}

    assert {
        "name and email and phone number for these District Approx Size Tech Decision Maker Type Mesa Public Schools 60k+ students CIO / Director of Technology; Chandler Unified School District 40k+ CTO / IT Director; Peoria Unified School District 35k+ Technology Services; Gilbert Public Schools 30k+ CTO; Deer Valley Unified School District 30k+ IT leadership; Paradise Valley Unified School District 25k+ CIO/Technology; Dysart Unified School District 24k+ Director of Technology; Maricopa Unified School District 9k+ Director of Technology",
        "commodity buyers at retail lumber yards in Washington",
        "healthcare IT directors in Phoenix",
        "finance CISOs at financial services firms in New York",
        "manufacturing operations leaders in Detroit",
        "personal phone numbers for homeowners in Texas",
    } == queries
    assert {"named_account", "broad_b2b", "privacy_rejection"} == themes
    assert {case.benchmark_id for case in suite.cases} == {
        case.benchmark_id for case in fixture_pack.cases
    }

    for case in suite.cases:
        result = evaluate_query_guardrails(case.query)
        assert result.status == case.expected_guardrail_status

    assert validate_required_benchmark_suite(suite) == ()


def test_required_benchmark_suite_reports_pass_fail_dimensions_offline():
    suite, observations = _build_observations()
    report = evaluate_required_benchmark_suite(suite, observations)

    assert report.suite_id == "required_lead_quality_suite"
    assert report.total_cases == 6
    assert report.passed_cases == 6
    assert report.failed_cases == 0
    assert report.persona_pass_cases == 3
    assert report.contact_pass_cases == 3
    assert report.source_pass_cases == 3
    assert report.privacy_refusal_cases == 1
    assert report.guardrail_mismatches == ()
    assert report.observation_mismatches == ()
