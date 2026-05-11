from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import httpx

from .benchmark_suite import (
    OperatorEvidenceFixturePack,
    OperatorFixtureCase,
    build_operator_evidence_fixture_pack,
    build_required_benchmark_suite,
    build_saved_benchmark_observations,
    evaluate_required_benchmark_suite,
)

RunnerMode = Literal["scout", "full"]

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_OUTPUT_ROOT = _REPO_ROOT / "audits" / "raw" / "reset-2026-05-10" / "rg1"


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


@dataclass(frozen=True, slots=True)
class LiveBenchmarkCaseResult:
    benchmark_id: str
    mode: RunnerMode
    status_code: int
    response_path: Path
    status_path: Path
    elapsed_seconds: float

    def to_payload(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "mode": self.mode,
            "status_code": self.status_code,
            "response_path": str(self.response_path),
            "status_path": str(self.status_path),
            "elapsed_seconds": self.elapsed_seconds,
        }


@dataclass(frozen=True, slots=True)
class LiveBenchmarkRunSummary:
    mode: RunnerMode
    api_base_url: str
    output_root: Path
    suite_report: dict[str, Any]
    case_results: tuple[LiveBenchmarkCaseResult, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "api_base_url": self.api_base_url,
            "output_root": str(self.output_root),
            "suite_report": self.suite_report,
            "case_results": [result.to_payload() for result in self.case_results],
        }


def _normalize_response_payload(case: OperatorFixtureCase, status_code: int, payload: Any, elapsed_seconds: float) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "benchmark_id": case.benchmark_id,
        "prompt_label": case.prompt_label,
        "query": case.query,
        "mode": "scout",
        "runner_elapsed_seconds": elapsed_seconds,
    }

    if status_code < 400 and isinstance(payload, dict):
        normalized.update(payload)
        return normalized

    detail = payload.get("detail") if isinstance(payload, dict) else None
    error_payload = detail if isinstance(detail, dict) else payload if isinstance(payload, dict) else {}

    normalized["leads"] = []
    if "query_guardrail" in error_payload:
        normalized["query_guardrail"] = error_payload.get("query_guardrail")
    if isinstance(error_payload.get("error"), str):
        normalized["error"] = error_payload["error"]
    elif isinstance(error_payload.get("message"), str):
        normalized["error"] = error_payload["message"]
    else:
        normalized["error"] = f"HTTP {status_code}"
    if isinstance(error_payload.get("error_code"), str):
        normalized["error_code"] = error_payload["error_code"]
    return normalized


async def _run_case(
    client: httpx.AsyncClient,
    *,
    case: OperatorFixtureCase,
    api_base_url: str,
    api_token: str,
    output_root: Path,
    mode: RunnerMode,
) -> LiveBenchmarkCaseResult:
    route = "/full" if mode == "full" else "/scout"
    request_body: dict[str, Any] = {"query": case.query}
    if mode == "full":
        request_body["recipe_name"] = f"reset-rg1-{case.benchmark_id}"

    output_root.mkdir(parents=True, exist_ok=True)
    response_path = output_root / f"{case.benchmark_id}.json"
    status_path = output_root / f"{case.benchmark_id}.http"

    start = time.perf_counter()
    try:
        response = await client.post(
            f"{api_base_url.rstrip('/')}{route}",
            headers={"x-white-rabbit-internal-token": api_token},
            json=request_body,
        )
        elapsed_seconds = round(time.perf_counter() - start, 3)
        try:
            payload = response.json()
        except ValueError:
            payload = {"error": response.text}
        status_code = response.status_code
        normalized_payload = _normalize_response_payload(case, status_code, payload, elapsed_seconds)
    except httpx.TimeoutException as exc:
        elapsed_seconds = round(time.perf_counter() - start, 3)
        status_code = 599
        normalized_payload = {
            "benchmark_id": case.benchmark_id,
            "prompt_label": case.prompt_label,
            "query": case.query,
            "mode": mode,
            "runner_elapsed_seconds": elapsed_seconds,
            "leads": [],
            "error": f"Runner timeout: {exc}",
            "error_code": "runner_timeout",
            "partial_artifact": True,
        }
    except httpx.RequestError as exc:
        elapsed_seconds = round(time.perf_counter() - start, 3)
        status_code = 599
        normalized_payload = {
            "benchmark_id": case.benchmark_id,
            "prompt_label": case.prompt_label,
            "query": case.query,
            "mode": mode,
            "runner_elapsed_seconds": elapsed_seconds,
            "leads": [],
            "error": f"Runner request error: {exc}",
            "error_code": "runner_request_error",
            "partial_artifact": True,
        }
    normalized_payload["mode"] = mode
    response_path.write_text(json.dumps(normalized_payload, indent=2, sort_keys=True), encoding="utf-8")
    status_path.write_text(f"{status_code}\n", encoding="utf-8")

    return LiveBenchmarkCaseResult(
        benchmark_id=case.benchmark_id,
        mode=mode,
        status_code=status_code,
        response_path=response_path,
        status_path=status_path,
        elapsed_seconds=elapsed_seconds,
    )


async def run_live_benchmark_suite(
    *,
    api_base_url: str,
    api_token: str,
    fixture_pack: OperatorEvidenceFixturePack | None = None,
    output_root: Path | None = None,
    mode: RunnerMode = "scout",
    reset_sandbox: bool = True,
    client: httpx.AsyncClient | None = None,
) -> LiveBenchmarkRunSummary:
    fixture_pack = fixture_pack or build_operator_evidence_fixture_pack()
    output_root = output_root or _DEFAULT_OUTPUT_ROOT

    owns_client = client is None
    if owns_client:
        client = httpx.AsyncClient(timeout=120.0, follow_redirects=True)

    try:
        if reset_sandbox:
            await client.post(
                f"{api_base_url.rstrip('/')}/sandbox/reset",
                headers={"x-white-rabbit-internal-token": api_token},
            )
        case_results = []
        for case in fixture_pack.cases:
            case_results.append(
                await _run_case(
                    client,
                    case=case,
                    api_base_url=api_base_url,
                    api_token=api_token,
                    output_root=output_root,
                    mode=mode,
                )
            )
    finally:
        if owns_client and client is not None:
            await client.aclose()

    observations = build_saved_benchmark_observations(output_root, fixture_pack=fixture_pack)
    suite = build_required_benchmark_suite(fixture_pack=fixture_pack)
    suite_report = evaluate_required_benchmark_suite(suite, observations)
    theme_summaries: dict[str, dict[str, Any]] = {}
    for case in fixture_pack.cases:
        observation = observations[case.benchmark_id]
        summary = theme_summaries.setdefault(
            case.theme,
            {
                "case_count": 0,
                "categorized_rows": 0,
                "person_rows": 0,
                "high_trust_usable_rows": 0,
                "contact_quality_passes": 0,
                "contact_evidence_candidates_searched": 0,
                "contact_evidence_contacts_acquired": 0,
                "contact_evidence_review_to_high_trust": 0,
            },
        )
        funnel_counts = observation.funnel_counts or {}
        summary["case_count"] += 1
        summary["categorized_rows"] += observation.categorized_row_count
        summary["person_rows"] += observation.person_lead_count
        summary["high_trust_usable_rows"] += observation.high_trust_usable_count
        summary["contact_quality_passes"] += int(funnel_counts.get("contact_quality_passes", 0) or 0)
        summary["contact_evidence_candidates_searched"] += int(
            funnel_counts.get("contact_evidence_candidates_searched", 0) or 0
        )
        summary["contact_evidence_contacts_acquired"] += int(
            funnel_counts.get("contact_evidence_contacts_acquired", 0) or 0
        )
        summary["contact_evidence_review_to_high_trust"] += int(
            funnel_counts.get("contact_evidence_review_to_high_trust", 0) or 0
        )
    for summary in theme_summaries.values():
        summary["contact_quality_rate"] = _rate(summary["contact_quality_passes"], summary["categorized_rows"])
        summary["high_trust_usable_yield"] = _rate(summary["high_trust_usable_rows"], summary["categorized_rows"])
        summary["contact_acquisition_success_rate"] = _rate(
            summary["contact_evidence_contacts_acquired"],
            summary["contact_evidence_candidates_searched"],
        )
        summary["review_to_high_trust_rate"] = _rate(
            summary["contact_evidence_review_to_high_trust"],
            summary["contact_evidence_candidates_searched"],
        )
    suite_payload = {
        "suite_id": suite_report.suite_id,
        "total_cases": suite_report.total_cases,
        "passed_cases": suite_report.passed_cases,
        "failed_cases": suite_report.failed_cases,
        "persona_pass_cases": suite_report.persona_pass_cases,
        "contact_pass_cases": suite_report.contact_pass_cases,
        "source_pass_cases": suite_report.source_pass_cases,
        "privacy_refusal_cases": suite_report.privacy_refusal_cases,
        "guardrail_mismatches": list(suite_report.guardrail_mismatches),
        "observation_mismatches": list(suite_report.observation_mismatches),
        "theme_summaries": theme_summaries,
        "case_summaries": {
            benchmark_id: {
                "http_status": observation.http_status,
                "guardrail_status": observation.guardrail_status,
                "categorized_row_count": observation.categorized_row_count,
                "person_lead_count": observation.person_lead_count,
                "high_trust_usable_count": observation.high_trust_usable_count,
                "review_count": observation.review_count,
                "organization_only_count": observation.organization_only_count,
                "not_found_count": observation.not_found_count,
                "failed_count": observation.failed_count,
                "expected_target_coverage_count": observation.expected_target_coverage_count,
                "expected_target_coverage_missing": list(observation.expected_target_coverage_missing),
                "minimum_escape_rows": observation.minimum_escape_rows,
                "target_categorized_rows": observation.target_categorized_rows,
                "escape_velocity_floor_met": observation.escape_velocity_floor_met,
                "target_volume_floor_met": observation.target_volume_floor_met,
                "high_volume_floor_met": observation.high_volume_floor_met,
                "volume_floor_status": observation.volume_floor_status,
                "privacy_refusal": observation.privacy_refusal,
                "funnel_counts": dict(observation.funnel_counts or {}),
                "error_code": observation.error_code,
                "quality_status": (
                    "expected_privacy_refusal" if observation.privacy_refusal else "evaluated"
                ),
                "ready_blocker_counts": (
                    {"privacy_refusal": 1}
                    if observation.privacy_refusal
                    else observation.quality_report.ready_blocker_counts
                    if observation.quality_report is not None
                    else {}
                ),
                "candidate_ready_blockers": (
                    []
                    if observation.privacy_refusal or observation.quality_report is None
                    else observation.quality_report.candidate_ready_blockers
                ),
                "quality_report": (
                    observation.quality_report.to_payload() if observation.quality_report is not None else None
                ),
            }
            for benchmark_id, observation in observations.items()
        },
    }
    (output_root / "quality-summary.json").write_text(
        json.dumps(suite_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return LiveBenchmarkRunSummary(
        mode=mode,
        api_base_url=api_base_url,
        output_root=output_root,
        suite_report=suite_payload,
        case_results=tuple(case_results),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the White Rabbit RG1 live benchmark suite.")
    parser.add_argument("--api-base-url", default=os.environ.get("WR_BENCHMARK_API_BASE_URL", "http://localhost:8000"))
    parser.add_argument(
        "--output-dir",
        default=str(_DEFAULT_OUTPUT_ROOT),
        help="Directory for per-benchmark JSON/HTTP artifacts and the quality summary.",
    )
    parser.add_argument("--mode", choices=("scout", "full"), default="scout")
    parser.add_argument(
        "--no-reset-sandbox",
        action="store_true",
        help="Skip the protected sandbox reset before running the suite.",
    )
    parser.add_argument(
        "--api-token",
        default=os.environ.get("WR_API_INTERNAL_TOKEN"),
        help="Internal API token. Defaults to WR_API_INTERNAL_TOKEN.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if not args.api_token:
        parser.error("missing API token: pass --api-token or set WR_API_INTERNAL_TOKEN")

    summary = asyncio.run(
        run_live_benchmark_suite(
            api_base_url=args.api_base_url,
            api_token=args.api_token,
            output_root=Path(args.output_dir),
            mode=args.mode,
            reset_sandbox=not args.no_reset_sandbox,
        )
    )
    print(json.dumps(summary.to_payload(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
