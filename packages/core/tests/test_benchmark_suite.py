from __future__ import annotations

import json
from pathlib import Path

from core.benchmark_suite import (
    BenchmarkObservation,
    OperatorEvidenceFixturePack,
    build_replay_benchmark_observations,
    build_operator_evidence_fixture_pack,
    build_required_benchmark_suite,
    build_saved_benchmark_observations,
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


def test_replay_benchmark_observations_preserve_saved_reset_failures():
    observations = build_replay_benchmark_observations()

    arizona = observations["thomas-arizona-k12"]
    lee = observations["lee-commodity-buyers"]
    healthcare = observations["healthcare-it-phoenix"]
    finance = observations["finance-cisos-new-york"]
    manufacturing = observations["manufacturing-ops-detroit"]
    privacy = observations["privacy-reject-homeowner-phones"]

    assert arizona.guardrail_status == "needs_more_detail"
    assert arizona.categorized_row_count == 3
    assert arizona.review_count == 3
    assert arizona.expected_target_coverage_count == 3
    assert arizona.expected_target_coverage_missing == (
        "Gilbert Public Schools",
        "Deer Valley Unified School District",
        "Paradise Valley Unified School District",
        "Dysart Unified School District",
        "Maricopa Unified School District",
    )
    assert arizona.high_volume_floor_met is False
    assert arizona.contact_pass is False

    assert lee.http_status == 200
    assert lee.categorized_row_count == 4
    assert lee.review_count == 4
    assert lee.minimum_escape_rows == 10
    assert lee.target_categorized_rows == 50
    assert lee.escape_velocity_floor_met is False
    assert lee.target_volume_floor_met is False
    assert lee.volume_floor_status == "below_active_50_plus_target"
    assert lee.high_volume_floor_met is False

    assert healthcare.categorized_row_count == 2
    assert healthcare.persona_pass is True
    assert healthcare.contact_pass is False
    assert healthcare.source_pass is True
    assert healthcare.high_volume_floor_met is False

    assert finance.categorized_row_count == 4
    assert finance.guardrail_status == "needs_more_detail"
    assert finance.persona_pass is True
    assert finance.contact_pass is False
    assert finance.source_pass is True

    assert manufacturing.http_status == 503
    assert manufacturing.error_code == "openai_failed"
    assert manufacturing.categorized_row_count == 0
    assert manufacturing.high_volume_floor_met is False
    assert manufacturing.persona_pass is False

    assert privacy.http_status is None
    assert privacy.guardrail_status == "blocked"
    assert privacy.categorized_row_count == 0
    assert privacy.privacy_refusal is True
    assert privacy.volume_floor_status == "expected_privacy_refusal"
    assert privacy.high_volume_floor_met is True
    assert privacy.quality_report is None


def test_replay_benchmark_suite_fails_current_bad_outputs_offline():
    suite = build_required_benchmark_suite()
    observations = build_replay_benchmark_observations()
    report = evaluate_required_benchmark_suite(suite, observations)

    assert report.total_cases == 6
    assert report.passed_cases == 1
    assert report.failed_cases == 5
    assert report.persona_pass_cases == 2
    assert report.contact_pass_cases == 0
    assert report.source_pass_cases == 3
    assert report.privacy_refusal_cases == 1
    assert report.guardrail_mismatches == (
        "finance-cisos-new-york: expected guardrail clear, got needs_more_detail",
    )
    assert set(report.observation_mismatches) == {
        "thomas-arizona-k12: coverage, volume",
        "lee-commodity-buyers: source, volume",
        "healthcare-it-phoenix: contact, volume",
        "finance-cisos-new-york: guardrail, contact, volume",
        "manufacturing-ops-detroit: persona, contact, source, volume",
    }


def test_saved_benchmark_observations_tolerate_non_http_collector_status(tmp_path: Path):
    case = build_operator_evidence_fixture_pack().cases[0]
    fixture_pack = OperatorEvidenceFixturePack(
        pack_id="test-pack",
        source="unit-test",
        cases=(case,),
    )
    (tmp_path / f"{case.benchmark_id}.json").write_text(
        json.dumps(
            {
                "query_guardrail": {"status": case.expected_guardrail_status},
                "leads": [],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / f"{case.benchmark_id}.http").write_text("ERROR\n", encoding="utf-8")

    observations = build_saved_benchmark_observations(tmp_path, fixture_pack=fixture_pack)

    assert observations[case.benchmark_id].http_status is None
