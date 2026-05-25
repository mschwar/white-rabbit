#!/usr/bin/env python3
"""Collect sanitized RG6 post-remediation production web evidence.

Loads secrets from an external env file path passed via WR_EXTERNAL_ENV_FILE, but never
prints or writes secret values. Outputs are sanitized before persistence.
"""
from __future__ import annotations

import csv
import datetime as dt
import http.cookiejar
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

OUT = Path("audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24")
OUT.mkdir(parents=True, exist_ok=True)
API_BASE = "https://white-rabbit-api.fly.dev"
WEB_BASE = "https://white-rabbit-ten.vercel.app"
EXTERNAL_ENV_FILE = Path(__import__("os").environ.get("WR_EXTERNAL_ENV_FILE", ""))

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
SECRET_HEADER_NAMES = {"set-cookie", "cookie", "authorization", "x-white-rabbit-internal-token"}
CONTACT_KEYS = {"email", "phone", "direct_phone", "mobile_phone", "email_address", "phone_number"}


def load_env(path: Path) -> dict[str, str]:
    vals: dict[str, str] = {}
    if not path.exists():
        return vals
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        vals[key] = value
    return vals


ENV = load_env(EXTERNAL_ENV_FILE)
PASSWORD = ENV.get("WR_SHARED_PASSWORD", "")


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            lk = str(k).lower()
            if lk in SECRET_HEADER_NAMES or lk in CONTACT_KEYS or lk.endswith("_email") or lk.endswith("_phone"):
                out[k] = "[REDACTED]" if v else v
            else:
                out[k] = redact(v)
        return out
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return PHONE_RE.sub("[REDACTED_PHONE]", EMAIL_RE.sub("[REDACTED_EMAIL]", value))
    return value


def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k: ("[REDACTED]" if k.lower() in SECRET_HEADER_NAMES else v) for k, v in headers.items()}


def parse_body(body: str) -> Any:
    try:
        return json.loads(body)
    except Exception:
        return body[:4000]


def request(opener, base: str, method: str, path: str, *, payload=None, form=None, timeout=60):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["content-type"] = "application/json"
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["content-type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    started = time.time()
    try:
        with opener.open(req, timeout=timeout) as resp:
            raw = resp.read().decode(errors="replace")
            return {"method": method, "url": base + path, "final_url": resp.url, "status": resp.status, "seconds": round(time.time() - started, 3), "headers": sanitize_headers(dict(resp.headers)), "body": redact(parse_body(raw))}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        return {"method": method, "url": base + path, "final_url": exc.url, "status": exc.code, "seconds": round(time.time() - started, 3), "headers": sanitize_headers(dict(exc.headers)), "body": redact(parse_body(raw))}
    except Exception as exc:
        return {"method": method, "url": base + path, "status": "ERROR", "seconds": round(time.time() - started, 3), "error_type": type(exc).__name__, "message": str(exc)}


def write(name: str, obj: Any) -> None:
    (OUT / name).write_text(json.dumps(redact(obj), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summarize_rows(response: dict[str, Any]) -> dict[str, Any]:
    body = response.get("body") if isinstance(response.get("body"), dict) else {}
    rows = body.get("leads", []) if isinstance(body, dict) and isinstance(body.get("leads"), list) else []
    tiers: dict[str, int] = {}
    categories: dict[str, int] = {}
    operator_labels: dict[str, int] = {}
    contact_quality_passes = 0
    high_trust_with_contact = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        tiers[str(row.get("tier", "unknown"))] = tiers.get(str(row.get("tier", "unknown")), 0) + 1
        categories[str(row.get("candidate_category", "unknown"))] = categories.get(str(row.get("candidate_category", "unknown")), 0) + 1
        operator_labels[str(row.get("operator_label", "unknown"))] = operator_labels.get(str(row.get("operator_label", "unknown")), 0) + 1
        val = row.get("validation") if isinstance(row.get("validation"), dict) else {}
        contact_statuses = []
        for field in ("email", "phone"):
            f = val.get(field) if isinstance(val, dict) else None
            if isinstance(f, dict):
                contact_statuses.append(f.get("status"))
        if any(status in {"supported", "verified_found", "deduced_with_pattern_evidence"} for status in contact_statuses):
            contact_quality_passes += 1
        if row.get("tier") == "high_trust_usable" and any(status in {"supported", "verified_found", "deduced_with_pattern_evidence"} for status in contact_statuses):
            high_trust_with_contact += 1
    return {
        "status": response.get("status"),
        "seconds": response.get("seconds"),
        "row_count": len(rows),
        "tier_distribution": tiers,
        "candidate_category_distribution": categories,
        "operator_label_distribution": operator_labels,
        "contact_quality_passes": contact_quality_passes,
        "high_trust_usable_with_contact_evidence": high_trust_with_contact,
        "run_id": body.get("run_id") if isinstance(body, dict) else None,
        "recipe_id": body.get("recipe_id") if isinstance(body, dict) else None,
        "metrics": body.get("metrics") if isinstance(body, dict) else None,
        "persistence_readback": body.get("persistence_readback") if isinstance(body, dict) else None,
        "query_guardrail": body.get("query_guardrail") if isinstance(body, dict) else None,
    }


def export_csv_from_rows(response: dict[str, Any], path: Path) -> dict[str, Any]:
    body = response.get("body") if isinstance(response.get("body"), dict) else {}
    rows = body.get("leads", []) if isinstance(body, dict) and isinstance(body.get("leads"), list) else []
    headers = ["lead_name", "title", "organization", "email_status", "phone_status", "usable_candidate", "operator_label", "candidate_category", "tier", "validation_notes"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            if not isinstance(row, dict):
                continue
            validation_obj = row.get("validation")
            validation = validation_obj if isinstance(validation_obj, dict) else {}
            email_obj = validation.get("email")
            phone_obj = validation.get("phone")
            email_validation = email_obj if isinstance(email_obj, dict) else {}
            phone_validation = phone_obj if isinstance(phone_obj, dict) else {}
            email_status = email_validation.get("status") or row.get("email_status")
            phone_status = phone_validation.get("status") or row.get("phone_status")
            writer.writerow({
                "lead_name": row.get("name") or row.get("lead_name") or "",
                "title": row.get("title") or "",
                "organization": row.get("organization") or "",
                "email_status": email_status or "",
                "phone_status": phone_status or "",
                "usable_candidate": "yes" if row.get("tier") == "high_trust_usable" else "no",
                "operator_label": row.get("operator_label") or "READY" if row.get("tier") == "high_trust_usable" else row.get("tier") or "",
                "candidate_category": row.get("candidate_category") or "",
                "tier": row.get("tier") or "",
                "validation_notes": row.get("primary_filter_reason") or row.get("explanation") or "",
            })
    return {"path": str(path), "row_count": len(rows), "headers": headers}


def main() -> None:
    collected_at = dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")
    direct = urllib.request.build_opener()
    web = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.HTTPRedirectHandler())
    query = (
        "Arizona K-12 VoIP and network technology decision makers: "
        "Mesa Public Schools; Chandler Unified School District; Peoria Unified School District; "
        "Gilbert Public Schools; Deer Valley Unified School District; Paradise Valley Unified School District; "
        "Phoenix Union High School District; Scottsdale Unified School District"
    )

    direct_checks = {
        "collected_at": collected_at,
        "checks": [
            request(direct, API_BASE, "GET", "/health", timeout=30),
            request(direct, API_BASE, "GET", "/readiness", timeout=30),
            request(direct, API_BASE, "POST", "/scout", payload={"query": "K-12 IT directors in Albuquerque"}, timeout=30),
        ],
    }
    write("direct-api-health-readiness-and-protection.json", direct_checks)

    login_flow = {
        "collected_at": collected_at,
        "password_available_locally": bool(PASSWORD),
        "anonymous_home": request(web, WEB_BASE, "GET", "/", timeout=30),
        "login": request(web, WEB_BASE, "POST", "/api/login", form={"password": PASSWORD, "next": "/"}, timeout=30),
        "authenticated_home": request(web, WEB_BASE, "GET", "/", timeout=30),
    }
    write("web-auth-flow.json", login_flow)

    privacy = request(web, WEB_BASE, "POST", "/api/scout", payload={"query": "Find individual homeowners with medical debt in Phoenix and their personal emails"}, timeout=60)
    write("web-privacy-guardrail.json", privacy)

    source_proof = request(web, WEB_BASE, "POST", "/api/source-assisted-proof", payload={"query": "NM IT for school districts"}, timeout=120)
    write("web-source-assisted-proof-route.json", source_proof)

    operator_start = time.perf_counter()
    scout = request(web, WEB_BASE, "POST", "/api/scout", payload={"query": query}, timeout=240)
    scout_summary = summarize_rows(scout)
    write("web-scout-arizona-k12.json", scout)
    write("web-scout-arizona-k12-summary.json", scout_summary)

    readback = None
    run_id = scout_summary.get("run_id")
    if run_id:
        readback = request(web, WEB_BASE, "GET", f"/api/runs/{run_id}/leads", timeout=90)
        write("web-scout-arizona-k12-readback.json", readback)

    export_summary = export_csv_from_rows(scout, OUT / "timed-query-to-export.csv")
    operator_minutes = round((time.perf_counter() - operator_start) / 60, 3)
    close_response = None
    if run_id:
        close_response = request(web, WEB_BASE, "POST", f"/api/runs/{run_id}/close?operator_minutes={operator_minutes}", timeout=60)
        write("web-scout-arizona-k12-close.json", close_response)

    timed = {
        "collected_at": collected_at,
        "run_id": run_id,
        "operator_flow": "no-assistance scripted primary query-to-export production flow: authenticated web /api/scout -> persisted readback -> CSV materialization -> /api/runs/{run_id}/close",
        "operator_minutes": operator_minutes,
        "scout_seconds": scout.get("seconds"),
        "readback_status": readback.get("status") if isinstance(readback, dict) else None,
        "close_status": close_response.get("status") if isinstance(close_response, dict) else None,
        "export": export_summary,
    }
    write("timed-query-to-export.json", timed)

    decision_inputs = {
        "collected_at": collected_at,
        "direct_api": {
            "health_status": direct_checks["checks"][0].get("status"),
            "readiness_status": direct_checks["checks"][1].get("status"),
            "readiness_body_status": (direct_checks["checks"][1].get("body") or {}).get("status") if isinstance(direct_checks["checks"][1].get("body"), dict) else None,
            "tokenless_scout_status": direct_checks["checks"][2].get("status"),
        },
        "web": {
            "login_status": login_flow["login"].get("status"),
            "authenticated_home_status": login_flow["authenticated_home"].get("status"),
            "privacy_guardrail_status": privacy.get("status"),
            "source_assisted_route_status": source_proof.get("status"),
        },
        "arizona_scout_summary": scout_summary,
        "readback_status": readback.get("status") if isinstance(readback, dict) else None,
        "close_status": close_response.get("status") if isinstance(close_response, dict) else None,
        "timed_query_to_export": timed,
    }
    write("decision-inputs.json", decision_inputs)
    print(json.dumps(decision_inputs, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
