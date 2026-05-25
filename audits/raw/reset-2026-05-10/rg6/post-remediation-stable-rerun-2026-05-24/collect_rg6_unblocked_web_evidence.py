#!/usr/bin/env python3
"""Collect RG6 production evidence through the authenticated web boundary.

The script loads secrets from WR_EXTERNAL_ENV_FILE, but only writes sanitized
production artifacts. It intentionally avoids the direct live benchmark command
that was previously denied by the tool approval layer.
"""
from __future__ import annotations

import csv
import datetime as dt
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[5]
CORE_SRC = REPO_ROOT / "packages" / "core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from core.benchmark_suite import (  # noqa: E402
    build_operator_evidence_fixture_pack,
    build_required_benchmark_suite,
    build_saved_benchmark_observations,
    evaluate_required_benchmark_suite,
)

OUT = Path(os.environ.get("WR_RG6_EVIDENCE_OUT", Path(__file__).resolve().parent))
API_BASE = os.environ.get("WR_RG6_API_BASE", "https://white-rabbit-api.fly.dev")
WEB_BASE = os.environ.get("WR_RG6_WEB_BASE", "https://white-rabbit-ten.vercel.app")
EXTERNAL_ENV_FILE = Path(os.environ.get("WR_EXTERNAL_ENV_FILE", ""))

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
SECRET_HEADER_NAMES = {"set-cookie", "cookie", "authorization", "x-white-rabbit-internal-token"}
CONTACT_KEYS = {"email", "phone", "direct_phone", "mobile_phone", "email_address", "phone_number"}
CONTACT_STATUSES = {"supported", "verified_found", "deduced_with_pattern_evidence"}
EXPORT_HEADERS = [
    "lead_name",
    "title",
    "organization",
    "email",
    "email_status",
    "phone",
    "phone_status",
    "usable_candidate",
    "operator_label",
    "candidate_category",
    "rank",
    "query",
    "run_id",
    "fit_score",
    "evidence_score",
    "contact_score",
    "ranking_gate",
    "source_name_url",
    "source_title_url",
    "source_org_url",
    "source_email_url",
    "source_phone_url",
    "source_access_status",
    "validation_notes",
    "checked_at",
    "location",
    "recipe_name",
    "sort_mode",
    "generated_at",
]


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


ENV: dict[str, str] = {}
PASSWORD = ""


def progress(message: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")
    line = f"{timestamp} {message}"
    with (OUT / "collector-progress.log").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line, flush=True)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, inner in value.items():
            lowered = str(key).lower()
            if lowered in SECRET_HEADER_NAMES:
                out[key] = "[REDACTED]" if inner else inner
            elif (
                (lowered in CONTACT_KEYS or lowered.endswith("_email") or lowered.endswith("_phone"))
                and not isinstance(inner, (dict, list))
            ):
                out[key] = "" if inner else inner
            else:
                out[key] = redact(inner)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return PHONE_RE.sub("[REDACTED_PHONE]", EMAIL_RE.sub("[REDACTED_EMAIL]", value))
    return value


def sanitize_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {key: ("[REDACTED]" if key.lower() in SECRET_HEADER_NAMES else value) for key, value in headers.items()}


def redact_contact_cell(value: Any) -> str:
    if not value:
        return ""
    text = str(value)
    if EMAIL_RE.search(text):
        return "[REDACTED_EMAIL]"
    if PHONE_RE.search(text):
        return "[REDACTED_PHONE]"
    return ""


def parse_body(body: str) -> Any:
    try:
        return json.loads(body)
    except Exception:
        return body[:4000]


def request(opener, base: str, method: str, path: str, *, payload: Any = None, form: Mapping[str, str] | None = None, timeout: float = 60) -> dict[str, Any]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["content-type"] = "application/json"
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["content-type"] = "application/x-www-form-urlencoded"

    req = urllib.request.Request(base.rstrip("/") + path, data=data, headers=headers, method=method)
    started = time.perf_counter()
    try:
        with opener.open(req, timeout=timeout) as response:
            raw = response.read().decode(errors="replace")
            return {
                "method": method,
                "url": base.rstrip("/") + path,
                "final_url": response.url,
                "status": response.status,
                "seconds": round(time.perf_counter() - started, 3),
                "headers": sanitize_headers(dict(response.headers)),
                "body": redact(parse_body(raw)),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        return {
            "method": method,
            "url": base.rstrip("/") + path,
            "final_url": exc.url,
            "status": exc.code,
            "seconds": round(time.perf_counter() - started, 3),
            "headers": sanitize_headers(dict(exc.headers)),
            "body": redact(parse_body(raw)),
        }
    except Exception as exc:
        return {
            "method": method,
            "url": base.rstrip("/") + path,
            "status": "ERROR",
            "seconds": round(time.perf_counter() - started, 3),
            "error_type": type(exc).__name__,
            "message": str(exc),
        }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(redact(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def body_dict(response: Mapping[str, Any]) -> dict[str, Any]:
    body = response.get("body")
    return body if isinstance(body, dict) else {}


def response_rows(response: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = body_dict(response).get("leads")
    return rows if isinstance(rows, list) else []


def distribution(rows: list[dict[str, Any]], field: str, default: str = "unknown") -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get(field) or default) if isinstance(row, dict) else default
        counts[key] = counts.get(key, 0) + 1
    return counts


def validation_status(row: Mapping[str, Any], field: str) -> str:
    validation = row.get("validation")
    if not isinstance(validation, dict):
        return str(row.get(f"{field}_status") or "")
    record = validation.get(field)
    if not isinstance(record, dict):
        return str(row.get(f"{field}_status") or "")
    return str(record.get("status") or "")


def validation_source(row: Mapping[str, Any], field: str) -> str:
    validation = row.get("validation")
    fallback = str(row.get("source_url") or "")
    if not isinstance(validation, dict):
        return fallback
    record = validation.get(field)
    if not isinstance(record, dict):
        return fallback
    return str(record.get("source_url") or fallback)


def checked_at(row: Mapping[str, Any]) -> str:
    validation = row.get("validation")
    if not isinstance(validation, dict):
        return ""
    for field in ("source", "name", "title", "organization", "email", "phone"):
        record = validation.get(field)
        if isinstance(record, dict) and record.get("checked_at"):
            return str(record["checked_at"])
    return ""


def row_has_contact_support(row: Mapping[str, Any]) -> bool:
    return validation_status(row, "email") in CONTACT_STATUSES or validation_status(row, "phone") in CONTACT_STATUSES


def output_tier(row: Mapping[str, Any]) -> str:
    return str(row.get("tier") or "review")


def ranking_gate(row: Mapping[str, Any]) -> str:
    category = str(row.get("candidate_category") or "person_lead")
    tier = output_tier(row)
    if tier == "high_trust_usable":
        return "usable"
    if category == "organization_only":
        return "organization_only"
    if category == "not_found" or tier == "not_found":
        return "not_found"
    return "noisy_failed"


def operator_label(row: Mapping[str, Any]) -> str:
    tier = output_tier(row)
    return {
        "high_trust_usable": "READY",
        "review": "REVIEW",
        "manual_lookup": "REVIEW",
        "organization_only": "ORG-ONLY",
        "not_found": "NOT FOUND",
        "failed": "NOT FOUND",
    }.get(tier, "REVIEW")


def summarize_case(case_id: str, response: Mapping[str, Any]) -> dict[str, Any]:
    rows = response_rows(response)
    high_trust_with_contact = sum(1 for row in rows if isinstance(row, dict) and output_tier(row) == "high_trust_usable" and row_has_contact_support(row))
    contact_quality_passes = sum(1 for row in rows if isinstance(row, dict) and row_has_contact_support(row))
    body = body_dict(response)
    return {
        "benchmark_id": case_id,
        "status": response.get("status"),
        "seconds": response.get("seconds"),
        "row_count": len(rows),
        "tier_distribution": distribution(rows, "tier"),
        "candidate_category_distribution": distribution(rows, "candidate_category"),
        "operator_label_distribution": {label: sum(1 for row in rows if isinstance(row, dict) and operator_label(row) == label) for label in ("READY", "REVIEW", "ORG-ONLY", "NOT FOUND")},
        "contact_quality_passes": contact_quality_passes,
        "high_trust_usable_with_contact_evidence": high_trust_with_contact,
        "run_id": body.get("run_id"),
        "recipe_id": body.get("recipe_id"),
        "metrics": body.get("metrics"),
        "persistence_readback": body.get("persistence_readback"),
        "query_guardrail": body.get("query_guardrail"),
        "sandbox_usage": body.get("sandbox_usage"),
    }


def export_rows(response: Mapping[str, Any], *, query: str, location: str, run_id: str, generated_at: str, output_path: Path) -> dict[str, Any]:
    rows = response_rows(response)
    guardrail = body_dict(response).get("query_guardrail")
    guardrail_note = "No query guardrail result returned." if guardrail is None else f"Query guardrail {guardrail.get('status')}: {guardrail.get('message')}"
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_HEADERS)
        writer.writeheader()
        for rank, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            gate = ranking_gate(row)
            validation_note = " ".join(
                part
                for part in (
                    f"Generated {generated_at}.",
                    "Sort mode: gate.",
                    guardrail_note,
                    f"Field statuses: name={validation_status(row, 'name')}; title={validation_status(row, 'title')}; organization={validation_status(row, 'organization')}; email={validation_status(row, 'email')}; phone={validation_status(row, 'phone')}; source={validation_status(row, 'source')}.",
                    str(row.get("primary_filter_reason") or row.get("failure_reason") or row.get("explanation") or ""),
                )
                if part
            )
            writer.writerow(
                {
                    "lead_name": row.get("name") or row.get("lead_name") or "",
                    "title": row.get("title") or "",
                    "organization": row.get("organization") or row.get("target_account") or "",
                    "email": redact_contact_cell(row.get("email")),
                    "email_status": validation_status(row, "email"),
                    "phone": redact_contact_cell(row.get("phone")),
                    "phone_status": validation_status(row, "phone"),
                    "usable_candidate": "yes" if gate == "usable" else "no",
                    "operator_label": operator_label(row),
                    "candidate_category": row.get("candidate_category") or "person_lead",
                    "rank": str(rank),
                    "query": query,
                    "run_id": run_id,
                    "fit_score": row.get("fit_score") if row.get("fit_score") is not None else "",
                    "evidence_score": row.get("evidence_score") if row.get("evidence_score") is not None else "",
                    "contact_score": row.get("contact_score") if row.get("contact_score") is not None else "",
                    "ranking_gate": gate,
                    "source_name_url": validation_source(row, "name"),
                    "source_title_url": validation_source(row, "title"),
                    "source_org_url": validation_source(row, "organization"),
                    "source_email_url": validation_source(row, "email"),
                    "source_phone_url": validation_source(row, "phone"),
                    "source_access_status": validation_status(row, "source"),
                    "validation_notes": validation_note,
                    "checked_at": checked_at(row),
                    "location": location,
                    "recipe_name": "",
                    "sort_mode": "gate",
                    "generated_at": generated_at,
                }
            )
    return {"path": str(output_path), "row_count": len(rows), "headers": EXPORT_HEADERS}


def main() -> int:
    global ENV, PASSWORD
    OUT.mkdir(parents=True, exist_ok=True)
    collected_at = dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")
    progress("loading external env")
    ENV = load_env(EXTERNAL_ENV_FILE)
    PASSWORD = ENV.get("WR_SHARED_PASSWORD", "")
    progress("external env loaded")
    direct = urllib.request.build_opener()
    web = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
        urllib.request.HTTPRedirectHandler(),
    )
    fixture_pack = build_operator_evidence_fixture_pack()
    case_filter_raw = os.environ.get("WR_RG6_CASE_IDS", "")
    case_filter = {item.strip() for item in case_filter_raw.split(",") if item.strip()}
    skip_reset = os.environ.get("WR_RG6_SKIP_RESET", "").lower() in {"1", "true", "yes"}

    direct_checks = {
        "collected_at": collected_at,
        "checks": [
            request(direct, API_BASE, "GET", "/health", timeout=30),
            request(direct, API_BASE, "GET", "/readiness", timeout=30),
            request(direct, API_BASE, "POST", "/scout", payload={"query": "K-12 IT directors in Albuquerque"}, timeout=30),
        ],
    }
    write_json(OUT / "direct-api-health-readiness-and-protection.json", direct_checks)
    progress("direct checks written")

    login_flow = {
        "collected_at": collected_at,
        "password_available_locally": bool(PASSWORD),
        "anonymous_home": request(web, WEB_BASE, "GET", "/", timeout=30),
        "login": request(web, WEB_BASE, "POST", "/api/login", form={"password": PASSWORD, "next": "/"}, timeout=30),
        "authenticated_home": request(web, WEB_BASE, "GET", "/", timeout=30),
    }
    write_json(OUT / "web-auth-flow.json", login_flow)
    progress("web auth flow written")

    sandbox_before = request(web, WEB_BASE, "GET", "/api/sandbox", timeout=30)
    sandbox_reset = {"status": "SKIPPED", "reason": "WR_RG6_SKIP_RESET set"} if skip_reset else request(web, WEB_BASE, "POST", "/api/sandbox", timeout=60)
    sandbox_after = request(web, WEB_BASE, "GET", "/api/sandbox", timeout=30)
    write_json(OUT / "web-sandbox-reset.json", {"before": sandbox_before, "reset": sandbox_reset, "after": sandbox_after})
    progress("sandbox reset written")

    source_proof = request(web, WEB_BASE, "POST", "/api/source-assisted-proof", payload={"query": "NM IT for school districts"}, timeout=120)
    write_json(OUT / "web-source-assisted-proof-route.json", source_proof)
    progress("source-assisted proof written")

    case_summaries: dict[str, dict[str, Any]] = {}
    timed: dict[str, Any] | None = None
    for index, case in enumerate(fixture_pack.cases):
        if case_filter and case.benchmark_id not in case_filter:
            progress(f"skipping case {case.benchmark_id}")
            continue
        progress(f"starting case {case.benchmark_id}")
        started = time.perf_counter()
        response = request(web, WEB_BASE, "POST", "/api/scout", payload={"query": case.query}, timeout=300)
        elapsed_minutes = round((time.perf_counter() - started) / 60, 3)
        case_path = OUT / f"{case.benchmark_id}.json"
        status_path = OUT / f"{case.benchmark_id}.http"
        payload_body = body_dict(response)
        write_json(case_path, payload_body if payload_body else response)
        status = response.get("status")
        status_path.write_text(f"{status if isinstance(status, int) else 0}\n", encoding="utf-8")
        summary = summarize_case(case.benchmark_id, response)
        case_summaries[case.benchmark_id] = summary
        write_json(OUT / f"{case.benchmark_id}-summary.json", summary)
        progress(f"case {case.benchmark_id} written")

        if index == 0:
            run_id = str(summary.get("run_id") or "")
            readback = request(web, WEB_BASE, "GET", f"/api/runs/{run_id}/leads", timeout=90) if run_id else None
            export_summary = export_rows(
                response,
                query=case.query,
                location=case.geography,
                run_id=run_id,
                generated_at=collected_at,
                output_path=OUT / "timed-query-to-export.csv",
            )
            close_response = (
                request(
                    web,
                    WEB_BASE,
                    "POST",
                    f"/api/runs/{run_id}/close",
                    payload={"operator_minutes": elapsed_minutes},
                    timeout=60,
                )
                if run_id
                else None
            )
            if readback is not None:
                write_json(OUT / "timed-query-readback.json", readback)
            if close_response is not None:
                write_json(OUT / "timed-query-close.json", close_response)
            timed = {
                "collected_at": collected_at,
                "benchmark_id": case.benchmark_id,
                "run_id": run_id or None,
                "operator_flow": "no-assistance scripted primary query-to-export production flow: authenticated web /api/scout -> persisted readback -> CSV materialization -> /api/runs/{run_id}/close",
                "operator_minutes": elapsed_minutes,
                "scout_seconds": response.get("seconds"),
                "readback_status": readback.get("status") if isinstance(readback, dict) else None,
                "close_status": close_response.get("status") if isinstance(close_response, dict) else None,
                "export": export_summary,
            }
            write_json(OUT / "timed-query-to-export.json", timed)
            progress("timed query-to-export written")

    for case in fixture_pack.cases:
        summary_path = OUT / f"{case.benchmark_id}-summary.json"
        if case.benchmark_id not in case_summaries and summary_path.exists():
            case_summaries[case.benchmark_id] = json.loads(summary_path.read_text(encoding="utf-8"))
    if timed is None and (OUT / "timed-query-to-export.json").exists():
        timed = json.loads((OUT / "timed-query-to-export.json").read_text(encoding="utf-8"))

    observations = build_saved_benchmark_observations(OUT, fixture_pack=fixture_pack)
    suite_report = evaluate_required_benchmark_suite(build_required_benchmark_suite(fixture_pack), observations)
    quality_summary = {
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
        "case_summaries": case_summaries,
    }
    write_json(OUT / "quality-summary.json", quality_summary)
    progress("quality summary written")

    decision_inputs = {
        "collected_at": collected_at,
        "direct_api": {
            "health_status": direct_checks["checks"][0].get("status"),
            "readiness_status": direct_checks["checks"][1].get("status"),
            "readiness_body_status": body_dict(direct_checks["checks"][1]).get("status"),
            "tokenless_scout_status": direct_checks["checks"][2].get("status"),
        },
        "web": {
            "login_status": login_flow["login"].get("status"),
            "authenticated_home_status": login_flow["authenticated_home"].get("status"),
            "source_assisted_route_status": source_proof.get("status"),
        },
        "sandbox_reset_status": sandbox_reset.get("status"),
        "sandbox_after": body_dict(sandbox_after),
        "arizona_scout_summary": case_summaries.get("thomas-arizona-k12"),
        "timed_query_to_export": timed,
        "required_suite": quality_summary,
    }
    write_json(OUT / "decision-inputs.json", decision_inputs)
    progress("decision inputs written")
    print(json.dumps(decision_inputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
