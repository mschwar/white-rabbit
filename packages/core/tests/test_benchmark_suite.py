from __future__ import annotations

import json
from pathlib import Path

from core.benchmark_suite import (
    BenchmarkObservation,
    build_required_benchmark_suite,
    evaluate_required_benchmark_suite,
    validate_required_benchmark_suite,
)
from core.query_guardrails import evaluate_query_guardrails


FIXTURE_PATH = Path(__file__).with_name("fixtures") / "benchmark_suite.json"


def _load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


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


def test_required_benchmark_suite_fixture_matches_canonical_definition():
    suite = build_required_benchmark_suite()
    assert _load_fixture() == suite.to_payload()


def test_required_benchmark_suite_covers_required_audit_queries_and_guardrails():
    suite = build_required_benchmark_suite()
    queries = {case.query for case in suite.cases}
    themes = {case.theme for case in suite.cases}

    assert {
        "contractors in Illinois",
        "food and beverage operations leaders in Texas",
        "healthcare IT directors in Phoenix",
        "finance CISOs at financial services firms in New York",
        "manufacturing operations leaders in Detroit",
        "K-12 IT directors in Albuquerque",
        "personal phone numbers for homeowners in Texas",
    } == queries
    assert {"simple_b2b", "guardrail_accept", "privacy_rejection"} == themes

    for case in suite.cases:
        result = evaluate_query_guardrails(case.query)
        assert result.status == case.expected_guardrail_status

    assert validate_required_benchmark_suite(suite) == ()


def test_required_benchmark_suite_reports_pass_fail_dimensions_offline():
    suite, observations = _build_observations()
    report = evaluate_required_benchmark_suite(suite, observations)

    assert report.suite_id == "required_lead_quality_suite"
    assert report.total_cases == 7
    assert report.passed_cases == 7
    assert report.failed_cases == 0
    assert report.persona_pass_cases == 6
    assert report.contact_pass_cases == 6
    assert report.source_pass_cases == 6
    assert report.privacy_refusal_cases == 1
    assert report.guardrail_mismatches == ()
    assert report.observation_mismatches == ()
