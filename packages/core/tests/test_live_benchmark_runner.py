from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx

from core.benchmark_suite import build_operator_evidence_fixture_pack, build_saved_benchmark_observations
from core.live_benchmark_runner import run_live_benchmark_suite, wait_for_api_startup
from core.models import CandidateValidation, ContactValidationRecord, FieldValidationRecord, Lead


def _field(status: str = "supported") -> FieldValidationRecord:
    return FieldValidationRecord(
        status=status,
        source_url="https://example.com/source",
        evidence_snippet=f"evidence {status}",
        checked_at="2026-05-10T12:00:00Z",
        notes=f"notes {status}",
    )


def _contact(status: str = "verified_found") -> ContactValidationRecord:
    return ContactValidationRecord(
        status=status,
        source_url="https://example.com/contact",
        evidence_snippet=f"contact {status}",
        checked_at="2026-05-10T12:00:00Z",
        notes=f"contact {status}",
    )


def _lead_payload() -> dict:
    lead = Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Mesa Public Schools",
        email="jane.smith@mesa.example",
        email_status="verified_found",
        source_url="https://example.com/mesa",
        confidence=0.95,
        why_target="Matches the district technology leadership target.",
        icebreaker="Your district technology leadership role aligns with this outreach.",
        fit_score=0.95,
        evidence_score=0.9,
        contact_score=0.9,
        gate_passed=True,
        explanation="Strong fit with supported source evidence.",
        validation=CandidateValidation(
            name=_field(),
            title=_field(),
            organization=_field(),
            email=_contact(),
            phone=_contact("missing"),
            source=_field(),
        ),
    )
    return lead.model_dump(mode="json")


def test_build_saved_benchmark_observations_reads_saved_runner_artifacts(tmp_path: Path):
    fixture_pack = build_operator_evidence_fixture_pack()
    cases = tuple(case for case in fixture_pack.cases if case.benchmark_id in {"thomas-arizona-k12", "privacy-reject-homeowner-phones"})
    trimmed_pack = type(fixture_pack)(pack_id=fixture_pack.pack_id, source=fixture_pack.source, cases=cases)

    (tmp_path / "thomas-arizona-k12.json").write_text(
        json.dumps(
            {
                "benchmark_id": "thomas-arizona-k12",
                "query": cases[0].query,
                "leads": [_lead_payload()],
                "metrics": {"estimated_cost_usd": 0.12, "elapsed_seconds": 1.5},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "thomas-arizona-k12.http").write_text("200\n", encoding="utf-8")
    (tmp_path / "privacy-reject-homeowner-phones.json").write_text(
        json.dumps(
            {
                "benchmark_id": "privacy-reject-homeowner-phones",
                "query": cases[1].query,
                "error": "Blocked by privacy guardrail.",
                "query_guardrail": {"status": "blocked", "message": "Blocked by privacy guardrail."},
                "leads": [],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "privacy-reject-homeowner-phones.http").write_text("422\n", encoding="utf-8")

    observations = build_saved_benchmark_observations(tmp_path, fixture_pack=trimmed_pack)

    assert observations["thomas-arizona-k12"].http_status == 200
    assert observations["thomas-arizona-k12"].categorized_row_count == 1
    assert observations["thomas-arizona-k12"].funnel_counts["categorized_rows"] == 1
    assert observations["privacy-reject-homeowner-phones"].http_status == 422
    assert observations["privacy-reject-homeowner-phones"].guardrail_status == "blocked"
    assert observations["privacy-reject-homeowner-phones"].privacy_refusal is True
    assert observations["privacy-reject-homeowner-phones"].quality_report is None


def test_run_live_benchmark_suite_saves_raw_outputs_and_quality_summary(tmp_path: Path):
    fixture_pack = build_operator_evidence_fixture_pack()
    cases = tuple(case for case in fixture_pack.cases if case.benchmark_id in {"thomas-arizona-k12", "privacy-reject-homeowner-phones"})
    trimmed_pack = type(fixture_pack)(pack_id=fixture_pack.pack_id, source=fixture_pack.source, cases=cases)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok", "service": "white-rabbit-api"})
        if request.url.path == "/readiness":
            return httpx.Response(
                200,
                json={
                    "status": "degraded",
                    "checked_at": "2026-05-11T00:00:00Z",
                    "checks": [
                        {
                            "name": "tavily",
                            "status": "degraded",
                            "required": True,
                            "message": "Config-only readiness.",
                            "details": {"api_key_present": True},
                        }
                    ],
                },
            )
        if request.url.path == "/sandbox/reset":
            return httpx.Response(200, json={"sandbox_usage": {"total_queries": 0, "total_rows": 0}})
        query = json.loads(request.content.decode("utf-8"))["query"]
        if query == cases[0].query:
            return httpx.Response(
                200,
                json={
                    "leads": [_lead_payload()],
                    "metrics": {
                        "input_tokens": 100,
                        "output_tokens": 50,
                        "tavily_searches": 1,
                        "openai_web_searches": 0,
                        "elapsed_seconds": 1.23,
                        "estimated_cost_usd": 0.015,
                        "funnel_counts": {
                            "raw_vendor_hits": 24,
                            "deduped_sources": 18,
                            "source_snapshots": 18,
                            "extracted_candidates": 4,
                            "categorized_rows": 1,
                            "person_rows": 1,
                            "high_trust_usable_rows": 1,
                            "contact_quality_passes": 1,
                        },
                    },
                    "query_guardrail": {"status": "needs_more_detail", "message": "Needs account detail."},
                },
            )
        return httpx.Response(
            422,
            json={
                "detail": {
                    "error": "Blocked by privacy guardrail.",
                    "query_guardrail": {"status": "blocked", "message": "Blocked by privacy guardrail."},
                }
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        summary = asyncio.run(
            run_live_benchmark_suite(
                api_base_url="http://white-rabbit.test",
                api_token="test-token",
                fixture_pack=trimmed_pack,
                output_root=tmp_path,
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert summary.output_root == tmp_path
    assert summary.startup_probe is not None
    assert summary.startup_probe.health_ok is True
    assert (tmp_path / "thomas-arizona-k12.json").exists()
    assert (tmp_path / "startup" / "health.json").exists()
    assert (tmp_path / "startup" / "readiness.json").exists()
    assert (tmp_path / "thomas-arizona-k12.http").read_text(encoding="utf-8").strip() == "200"
    assert (tmp_path / "privacy-reject-homeowner-phones.http").read_text(encoding="utf-8").strip() == "422"

    saved_payload = json.loads((tmp_path / "thomas-arizona-k12.json").read_text(encoding="utf-8"))
    assert saved_payload["mode"] == "scout"
    assert saved_payload["metrics"]["estimated_cost_usd"] == 0.015
    assert "runner_elapsed_seconds" in saved_payload

    quality_summary = json.loads((tmp_path / "quality-summary.json").read_text(encoding="utf-8"))
    assert quality_summary["startup_probe"]["health_ok"] is True
    assert quality_summary["total_cases"] == 2
    assert quality_summary["case_summaries"]["thomas-arizona-k12"]["http_status"] == 200
    assert quality_summary["case_summaries"]["thomas-arizona-k12"]["funnel_counts"] == {
        "raw_vendor_hits": 24,
        "deduped_sources": 18,
        "source_snapshots": 18,
        "extracted_candidates": 4,
        "categorized_rows": 1,
        "person_rows": 1,
        "persona_supported_rows": 0,
        "source_supported_rows": 0,
        "high_trust_usable_rows": 1,
        "contact_quality_passes": 1,
        "contact_evidence_candidates_searched": 0,
        "contact_evidence_searches": 0,
        "contact_evidence_contacts_acquired": 0,
        "contact_evidence_field_corroborations": 0,
        "contact_evidence_conflicting_signals": 0,
        "contact_evidence_review_to_high_trust": 0,
    }
    assert quality_summary["theme_summaries"]["named_account"]["contact_quality_passes"] == 1
    assert quality_summary["theme_summaries"]["named_account"]["high_trust_usable_yield"] == 1.0
    assert quality_summary["case_summaries"]["thomas-arizona-k12"]["minimum_escape_rows"] == 8
    assert quality_summary["case_summaries"]["thomas-arizona-k12"]["target_categorized_rows"] == 8
    assert quality_summary["case_summaries"]["privacy-reject-homeowner-phones"]["http_status"] == 422
    assert quality_summary["case_summaries"]["privacy-reject-homeowner-phones"]["guardrail_status"] == "blocked"
    assert quality_summary["case_summaries"]["privacy-reject-homeowner-phones"]["quality_status"] == "expected_privacy_refusal"
    assert quality_summary["case_summaries"]["privacy-reject-homeowner-phones"]["ready_blocker_counts"] == {
        "privacy_refusal": 1
    }
    assert quality_summary["case_summaries"]["privacy-reject-homeowner-phones"]["quality_report"] is None
    assert quality_summary["case_summaries"]["privacy-reject-homeowner-phones"]["volume_floor_status"] == "expected_privacy_refusal"


def test_run_live_benchmark_suite_records_manufacturing_503_as_valid_artifact(tmp_path: Path):
    fixture_pack = build_operator_evidence_fixture_pack()
    cases = tuple(case for case in fixture_pack.cases if case.benchmark_id == "manufacturing-ops-detroit")
    trimmed_pack = type(fixture_pack)(pack_id=fixture_pack.pack_id, source=fixture_pack.source, cases=cases)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok", "service": "white-rabbit-api"})
        if request.url.path == "/readiness":
            return httpx.Response(200, json={"status": "ready"})
        if request.url.path == "/sandbox/reset":
            return httpx.Response(200, json={"sandbox_usage": {"total_queries": 0, "total_rows": 0}})
        return httpx.Response(
            503,
            json={
                "detail": {
                    "error": "OpenAI response could not be parsed: role-as-name validation failed.",
                    "error_code": "openai_parse_failed",
                }
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        asyncio.run(
            run_live_benchmark_suite(
                api_base_url="http://white-rabbit.test",
                api_token="test-token",
                fixture_pack=trimmed_pack,
                output_root=tmp_path,
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    saved_payload = json.loads((tmp_path / "manufacturing-ops-detroit.json").read_text(encoding="utf-8"))
    assert (tmp_path / "manufacturing-ops-detroit.http").read_text(encoding="utf-8").strip() == "503"
    assert saved_payload["benchmark_id"] == "manufacturing-ops-detroit"
    assert saved_payload["leads"] == []
    assert saved_payload["error_code"] == "openai_parse_failed"

    quality_summary = json.loads((tmp_path / "quality-summary.json").read_text(encoding="utf-8"))
    case_summary = quality_summary["case_summaries"]["manufacturing-ops-detroit"]
    assert case_summary["http_status"] == 503
    assert case_summary["error_code"] == "openai_parse_failed"
    assert case_summary["quality_status"] == "partial_artifact"
    assert case_summary["quality_report"]["total_candidates"] == 0


def test_run_live_benchmark_suite_writes_partial_artifacts_on_timeout(tmp_path: Path):
    fixture_pack = build_operator_evidence_fixture_pack()
    cases = tuple(case for case in fixture_pack.cases if case.benchmark_id == "healthcare-it-phoenix")
    trimmed_pack = type(fixture_pack)(pack_id=fixture_pack.pack_id, source=fixture_pack.source, cases=cases)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok", "service": "white-rabbit-api"})
        if request.url.path == "/readiness":
            return httpx.Response(200, json={"status": "ready", "checked_at": "2026-05-11T00:00:00Z", "checks": []})
        if request.url.path == "/sandbox/reset":
            return httpx.Response(200, json={"sandbox_usage": {"total_queries": 0, "total_rows": 0}})
        raise httpx.TimeoutException("case timed out", request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        summary = asyncio.run(
            run_live_benchmark_suite(
                api_base_url="http://white-rabbit.test",
                api_token="test-token",
                fixture_pack=trimmed_pack,
                output_root=tmp_path,
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert summary.case_results[0].status_code == 599
    assert (tmp_path / "healthcare-it-phoenix.http").read_text(encoding="utf-8").strip() == "599"
    saved_payload = json.loads((tmp_path / "healthcare-it-phoenix.json").read_text(encoding="utf-8"))
    assert saved_payload["error_code"] == "product_request_timeout"
    assert saved_payload["partial_artifact"] is True
    assert saved_payload["leads"] == []
    assert saved_payload["post_timeout_health_probe"]["health_ok"] is True
    assert (tmp_path / "timeouts" / "product-request" / "healthcare-it-phoenix" / "health.json").exists()
    assert (tmp_path / "timeouts" / "product-request" / "healthcare-it-phoenix" / "health.http").read_text(encoding="utf-8").strip() == "200"

    quality_summary = json.loads((tmp_path / "quality-summary.json").read_text(encoding="utf-8"))
    case_summary = quality_summary["case_summaries"]["healthcare-it-phoenix"]
    assert case_summary["http_status"] == 599
    assert case_summary["error_code"] == "product_request_timeout"
    assert case_summary["quality_status"] == "partial_artifact"
    assert case_summary["quality_report"]["total_candidates"] == 0
    assert case_summary["post_timeout_health_probe"]["health_ok"] is True


def test_run_live_benchmark_suite_writes_case_artifacts_when_readiness_times_out(tmp_path: Path):
    fixture_pack = build_operator_evidence_fixture_pack()
    cases = tuple(case for case in fixture_pack.cases if case.benchmark_id == "healthcare-it-phoenix")
    trimmed_pack = type(fixture_pack)(pack_id=fixture_pack.pack_id, source=fixture_pack.source, cases=cases)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok", "service": "white-rabbit-api"})
        if request.url.path == "/readiness":
            raise httpx.ReadTimeout("readiness timed out", request=request)
        raise AssertionError(f"Unexpected call to {request.url.path}")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        summary = asyncio.run(
            run_live_benchmark_suite(
                api_base_url="http://white-rabbit.test",
                api_token="test-token",
                fixture_pack=trimmed_pack,
                output_root=tmp_path,
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert summary.startup_probe is not None
    assert summary.startup_probe.health_ok is True
    assert summary.startup_probe.readiness_status == "readiness_timeout"
    assert summary.startup_probe.readiness_error_code == "readiness_timeout"
    saved_payload = json.loads((tmp_path / "healthcare-it-phoenix.json").read_text(encoding="utf-8"))
    assert saved_payload["error_code"] == "readiness_timeout"
    assert saved_payload["partial_artifact"] is True
    assert saved_payload["startup_probe"]["readiness_error_code"] == "readiness_timeout"
    quality_summary = json.loads((tmp_path / "quality-summary.json").read_text(encoding="utf-8"))
    assert quality_summary["suite_failure"]["stage"] == "readiness"
    assert quality_summary["suite_failure"]["error_code"] == "readiness_timeout"
    case_summary = quality_summary["case_summaries"]["healthcare-it-phoenix"]
    assert case_summary["quality_status"] == "partial_artifact"
    assert case_summary["error_code"] == "readiness_timeout"


def test_run_live_benchmark_suite_writes_case_artifacts_when_sandbox_reset_times_out(tmp_path: Path):
    fixture_pack = build_operator_evidence_fixture_pack()
    cases = tuple(case for case in fixture_pack.cases if case.benchmark_id == "healthcare-it-phoenix")
    trimmed_pack = type(fixture_pack)(pack_id=fixture_pack.pack_id, source=fixture_pack.source, cases=cases)
    health_calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            health_calls["count"] += 1
            return httpx.Response(200, json={"status": "ok", "service": "white-rabbit-api"})
        if request.url.path == "/readiness":
            return httpx.Response(
                200,
                json={
                    "status": "ready",
                    "checked_at": "2026-05-11T00:00:00Z",
                    "checks": [],
                },
            )
        if request.url.path == "/sandbox/reset":
            raise httpx.ReadTimeout("sandbox reset timed out", request=request)
        raise AssertionError(f"Unexpected call to {request.url.path}")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        summary = asyncio.run(
            run_live_benchmark_suite(
                api_base_url="http://white-rabbit.test",
                api_token="test-token",
                fixture_pack=trimmed_pack,
                output_root=tmp_path,
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert summary.startup_probe is not None
    assert summary.startup_probe.health_ok is True
    assert summary.suite_report["suite_failure"]["stage"] == "sandbox_reset"
    assert summary.suite_report["suite_failure"]["error_code"] == "sandbox_reset_timeout"
    saved_payload = json.loads((tmp_path / "healthcare-it-phoenix.json").read_text(encoding="utf-8"))
    assert saved_payload["error_code"] == "sandbox_reset_timeout"
    assert saved_payload["partial_artifact"] is True
    assert saved_payload["sandbox_reset_probe"]["error_code"] == "sandbox_reset_timeout"
    assert saved_payload["post_timeout_health_probe"]["health_ok"] is True
    assert health_calls["count"] >= 2
    quality_summary = json.loads((tmp_path / "quality-summary.json").read_text(encoding="utf-8"))
    case_summary = quality_summary["case_summaries"]["healthcare-it-phoenix"]
    assert case_summary["quality_status"] == "partial_artifact"
    assert case_summary["error_code"] == "sandbox_reset_timeout"
    assert quality_summary["sandbox_reset_probe"]["error_code"] == "sandbox_reset_timeout"


def test_run_live_benchmark_suite_records_runner_timeout_on_post_timeout_health_probe_failure(tmp_path: Path):
    fixture_pack = build_operator_evidence_fixture_pack()
    cases = tuple(case for case in fixture_pack.cases if case.benchmark_id == "healthcare-it-phoenix")
    trimmed_pack = type(fixture_pack)(pack_id=fixture_pack.pack_id, source=fixture_pack.source, cases=cases)
    health_calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            health_calls["count"] += 1
            if health_calls["count"] == 1:
                return httpx.Response(200, json={"status": "ok", "service": "white-rabbit-api"})
            raise httpx.ReadTimeout("post-timeout health probe timed out", request=request)
        if request.url.path == "/readiness":
            return httpx.Response(
                200,
                json={
                    "status": "ready",
                    "checked_at": "2026-05-11T00:00:00Z",
                    "checks": [],
                },
            )
        if request.url.path == "/sandbox/reset":
            return httpx.Response(200, json={"sandbox_usage": {"total_queries": 0, "total_rows": 0}})
        raise httpx.ReadTimeout("product request timed out", request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        summary = asyncio.run(
            run_live_benchmark_suite(
                api_base_url="http://white-rabbit.test",
                api_token="test-token",
                fixture_pack=trimmed_pack,
                output_root=tmp_path,
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert summary.case_results[0].status_code == 599
    saved_payload = json.loads((tmp_path / "healthcare-it-phoenix.json").read_text(encoding="utf-8"))
    assert saved_payload["error_code"] == "product_request_timeout"
    assert saved_payload["post_timeout_health_probe"]["error_code"] == "runner_timeout"
    quality_summary = json.loads((tmp_path / "quality-summary.json").read_text(encoding="utf-8"))
    assert quality_summary["case_summaries"]["healthcare-it-phoenix"]["quality_status"] == "partial_artifact"
    assert quality_summary["case_summaries"]["healthcare-it-phoenix"]["post_timeout_health_probe"]["error_code"] == "runner_timeout"


def test_wait_for_api_startup_writes_failure_artifacts(tmp_path: Path):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        probe = asyncio.run(
            wait_for_api_startup(
                api_base_url="http://127.0.0.1:8999",
                output_root=tmp_path,
                client=client,
                timeout_seconds=0.01,
                poll_interval_seconds=0.01,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert probe.health_ok is False
    assert probe.failure_path is not None
    assert (tmp_path / "startup" / "health.http").read_text(encoding="utf-8").strip() == "000"
    failure = json.loads((tmp_path / "startup" / "startup-failure.json").read_text(encoding="utf-8"))
    assert failure["error_code"] == "api_startup_failed"
    assert failure["api_base"]["port"] == 8999
    assert failure["env_presence"]["WR_API_INTERNAL_TOKEN"] in ({"present": False}, {"present": True})


def test_run_live_benchmark_suite_writes_case_artifacts_when_startup_fails(tmp_path: Path):
    fixture_pack = build_operator_evidence_fixture_pack()
    cases = tuple(case for case in fixture_pack.cases if case.benchmark_id == "healthcare-it-phoenix")
    trimmed_pack = type(fixture_pack)(pack_id=fixture_pack.pack_id, source=fixture_pack.source, cases=cases)

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        summary = asyncio.run(
            run_live_benchmark_suite(
                api_base_url="http://127.0.0.1:8999",
                api_token="test-token",
                fixture_pack=trimmed_pack,
                output_root=tmp_path,
                client=client,
                startup_timeout_seconds=0.01,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert summary.startup_probe is not None
    assert summary.startup_probe.health_ok is False
    assert summary.case_results[0].status_code == 599
    saved_payload = json.loads((tmp_path / "healthcare-it-phoenix.json").read_text(encoding="utf-8"))
    assert saved_payload["error_code"] == "api_startup_failed"
    assert saved_payload["partial_artifact"] is True
    quality_summary = json.loads((tmp_path / "quality-summary.json").read_text(encoding="utf-8"))
    assert quality_summary["startup_probe"]["health_ok"] is False
    assert quality_summary["case_summaries"]["healthcare-it-phoenix"]["error_code"] == "api_startup_failed"
