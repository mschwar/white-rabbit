from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping
from urllib.parse import urlparse

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
_STARTUP_ENV_KEYS = (
    "WR_API_INTERNAL_TOKEN",
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "TAVILY_API_KEY",
)


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
class ApiStartupProbeResult:
    api_base_url: str
    health_ok: bool
    readiness_status: str | None
    attempts: tuple[dict[str, Any], ...]
    health_path: Path
    health_status_path: Path
    readiness_path: Path | None
    readiness_status_path: Path | None
    failure_path: Path | None
    elapsed_seconds: float

    def to_payload(self) -> dict[str, Any]:
        return {
            "api_base_url": self.api_base_url,
            "health_ok": self.health_ok,
            "readiness_status": self.readiness_status,
            "attempts": list(self.attempts),
            "health_path": str(self.health_path),
            "health_status_path": str(self.health_status_path),
            "readiness_path": str(self.readiness_path) if self.readiness_path else None,
            "readiness_status_path": str(self.readiness_status_path) if self.readiness_status_path else None,
            "failure_path": str(self.failure_path) if self.failure_path else None,
            "elapsed_seconds": self.elapsed_seconds,
        }


@dataclass(frozen=True, slots=True)
class LiveBenchmarkRunSummary:
    mode: RunnerMode
    api_base_url: str
    output_root: Path
    suite_report: dict[str, Any]
    case_results: tuple[LiveBenchmarkCaseResult, ...]
    startup_probe: ApiStartupProbeResult | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "api_base_url": self.api_base_url,
            "output_root": str(self.output_root),
            "suite_report": self.suite_report,
            "case_results": [result.to_payload() for result in self.case_results],
            "startup_probe": self.startup_probe.to_payload() if self.startup_probe else None,
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


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _env_presence() -> dict[str, dict[str, bool]]:
    return {name: {"present": bool(os.environ.get(name))} for name in _STARTUP_ENV_KEYS}


def _api_base_details(api_base_url: str) -> dict[str, Any]:
    parsed = urlparse(api_base_url)
    return {
        "scheme": parsed.scheme,
        "host": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path or "",
    }


async def wait_for_api_startup(
    *,
    api_base_url: str,
    output_root: Path,
    client: httpx.AsyncClient,
    timeout_seconds: float = 30.0,
    poll_interval_seconds: float = 1.0,
) -> ApiStartupProbeResult:
    """Wait for process health, then capture readiness diagnostics."""
    startup_root = output_root / "startup"
    startup_root.mkdir(parents=True, exist_ok=True)
    health_path = startup_root / "health.json"
    health_status_path = startup_root / "health.http"
    readiness_path = startup_root / "readiness.json"
    readiness_status_path = startup_root / "readiness.http"
    failure_path = startup_root / "startup-failure.json"
    diagnostics_path = startup_root / "startup-diagnostics.json"

    started = time.perf_counter()
    attempts: list[dict[str, Any]] = []
    deadline = started + timeout_seconds
    last_health_payload: dict[str, Any] = {
        "error": "API health was not checked.",
        "api_base_url": api_base_url,
        "env_presence": _env_presence(),
    }
    last_health_status = 0

    while True:
        attempt_started = time.perf_counter()
        request_timeout = max(0.1, min(5.0, timeout_seconds, deadline - time.perf_counter()))
        try:
            response = await asyncio.wait_for(
                client.get(f"{api_base_url.rstrip('/')}/health", timeout=request_timeout),
                timeout=request_timeout,
            )
            elapsed = round(time.perf_counter() - attempt_started, 3)
            last_health_status = response.status_code
            try:
                payload: Any = response.json()
            except ValueError:
                payload = {"body": response.text}
            last_health_payload = payload if isinstance(payload, dict) else {"body": payload}
            attempt = {
                "status_code": response.status_code,
                "elapsed_seconds": elapsed,
                "ok": response.status_code == 200 and last_health_payload.get("status") == "ok",
            }
        except (asyncio.TimeoutError, httpx.RequestError) as exc:
            elapsed = round(time.perf_counter() - attempt_started, 3)
            last_health_status = 0
            last_health_payload = {
                "error": f"{exc.__class__.__name__}: {exc}",
                "error_code": "health_request_error",
                "api_base_url": api_base_url,
            }
            attempt = {
                "status_code": 0,
                "elapsed_seconds": elapsed,
                "ok": False,
                "error": last_health_payload["error"],
            }

        attempts.append(attempt)
        if attempt["ok"]:
            _write_json(health_path, last_health_payload)
            health_status_path.write_text(f"{last_health_status}\n", encoding="utf-8")
            try:
                readiness_timeout = max(0.1, min(5.0, timeout_seconds))
                readiness_response = await asyncio.wait_for(
                    client.get(
                        f"{api_base_url.rstrip('/')}/readiness",
                        timeout=readiness_timeout,
                    ),
                    timeout=readiness_timeout,
                )
                try:
                    readiness_payload: Any = readiness_response.json()
                except ValueError:
                    readiness_payload = {"body": readiness_response.text}
                readiness_payload = readiness_payload if isinstance(readiness_payload, dict) else {"body": readiness_payload}
                _write_json(readiness_path, readiness_payload)
                readiness_status_path.write_text(f"{readiness_response.status_code}\n", encoding="utf-8")
                readiness_status = (
                    str(readiness_payload.get("status"))
                    if isinstance(readiness_payload.get("status"), str)
                    else f"http_{readiness_response.status_code}"
                )
            except (asyncio.TimeoutError, httpx.RequestError) as exc:
                readiness_payload = {
                    "status": "unavailable",
                    "error": f"{exc.__class__.__name__}: {exc}",
                    "error_code": "readiness_request_error",
                }
                _write_json(readiness_path, readiness_payload)
                readiness_status_path.write_text("000\n", encoding="utf-8")
                readiness_status = "unavailable"

            result = ApiStartupProbeResult(
                api_base_url=api_base_url,
                health_ok=True,
                readiness_status=readiness_status,
                attempts=tuple(attempts),
                health_path=health_path,
                health_status_path=health_status_path,
                readiness_path=readiness_path,
                readiness_status_path=readiness_status_path,
                failure_path=None,
                elapsed_seconds=round(time.perf_counter() - started, 3),
            )
            _write_json(diagnostics_path, result.to_payload())
            return result

        if time.perf_counter() >= deadline:
            break
        await asyncio.sleep(max(0.0, min(poll_interval_seconds, deadline - time.perf_counter())))

    failure_payload = {
        "error_code": "api_startup_failed",
        "message": f"API did not answer /health before {timeout_seconds} second timeout.",
        "api_base_url": api_base_url,
        "api_base": _api_base_details(api_base_url),
        "env_presence": _env_presence(),
        "timeout_seconds": timeout_seconds,
        "attempts": attempts,
        "last_health_status": last_health_status,
        "last_health_payload": last_health_payload,
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    _write_json(health_path, last_health_payload)
    health_status_path.write_text(f"{last_health_status or '000'}\n", encoding="utf-8")
    _write_json(failure_path, failure_payload)

    result = ApiStartupProbeResult(
        api_base_url=api_base_url,
        health_ok=False,
        readiness_status=None,
        attempts=tuple(attempts),
        health_path=health_path,
        health_status_path=health_status_path,
        readiness_path=None,
        readiness_status_path=None,
        failure_path=failure_path,
        elapsed_seconds=round(time.perf_counter() - started, 3),
    )
    _write_json(diagnostics_path, result.to_payload())
    return result


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
    wait_for_startup: bool = True,
    startup_timeout_seconds: float = 30.0,
) -> LiveBenchmarkRunSummary:
    fixture_pack = fixture_pack or build_operator_evidence_fixture_pack()
    output_root = output_root or _DEFAULT_OUTPUT_ROOT

    owns_client = client is None
    if owns_client:
        client = httpx.AsyncClient(timeout=120.0, follow_redirects=True)

    startup_probe: ApiStartupProbeResult | None = None
    try:
        if wait_for_startup:
            startup_probe = await wait_for_api_startup(
                api_base_url=api_base_url,
                output_root=output_root,
                client=client,
                timeout_seconds=startup_timeout_seconds,
            )
            if not startup_probe.health_ok:
                case_results = []
                for case in fixture_pack.cases:
                    response_path = output_root / f"{case.benchmark_id}.json"
                    status_path = output_root / f"{case.benchmark_id}.http"
                    elapsed_seconds = startup_probe.elapsed_seconds
                    payload = {
                        "benchmark_id": case.benchmark_id,
                        "prompt_label": case.prompt_label,
                        "query": case.query,
                        "mode": mode,
                        "runner_elapsed_seconds": elapsed_seconds,
                        "leads": [],
                        "error": "API startup failed before live benchmark case execution.",
                        "error_code": "api_startup_failed",
                        "partial_artifact": True,
                        "startup_probe": startup_probe.to_payload(),
                    }
                    _write_json(response_path, payload)
                    status_path.write_text("599\n", encoding="utf-8")
                    case_results.append(
                        LiveBenchmarkCaseResult(
                            benchmark_id=case.benchmark_id,
                            mode=mode,
                            status_code=599,
                            response_path=response_path,
                            status_path=status_path,
                            elapsed_seconds=elapsed_seconds,
                        )
                    )
                observations = build_saved_benchmark_observations(output_root, fixture_pack=fixture_pack)
                suite = build_required_benchmark_suite(fixture_pack=fixture_pack)
                suite_report = evaluate_required_benchmark_suite(suite, observations)
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
                    "startup_probe": startup_probe.to_payload(),
                    "case_summaries": {
                        benchmark_id: {
                            "http_status": observation.http_status,
                            "error_code": observation.error_code,
                            "categorized_row_count": observation.categorized_row_count,
                            "person_lead_count": observation.person_lead_count,
                            "high_trust_usable_count": observation.high_trust_usable_count,
                            "privacy_refusal": observation.privacy_refusal,
                            "quality_report": (
                                observation.quality_report.to_payload()
                                if observation.quality_report is not None
                                else None
                            ),
                        }
                        for benchmark_id, observation in observations.items()
                    },
                }
                _write_json(output_root / "quality-summary.json", suite_payload)
                return LiveBenchmarkRunSummary(
                    mode=mode,
                    api_base_url=api_base_url,
                    output_root=output_root,
                    suite_report=suite_payload,
                    case_results=tuple(case_results),
                    startup_probe=startup_probe,
                )

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
        "startup_probe": startup_probe.to_payload() if startup_probe else None,
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
        startup_probe=startup_probe,
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
    parser.add_argument(
        "--startup-timeout-seconds",
        type=float,
        default=30.0,
        help="Seconds to wait for /health before writing startup-failure artifacts.",
    )
    parser.add_argument(
        "--skip-startup-check",
        action="store_true",
        help="Skip /health and /readiness startup diagnostics before running cases.",
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
            wait_for_startup=not args.skip_startup_check,
            startup_timeout_seconds=args.startup_timeout_seconds,
        )
    )
    print(json.dumps(summary.to_payload(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
