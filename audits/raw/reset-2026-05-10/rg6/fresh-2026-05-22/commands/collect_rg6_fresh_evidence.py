#!/usr/bin/env python3
"""Collect fresh RG6 live evidence without printing or saving secrets."""
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import http.cookiejar
from pathlib import Path
from typing import Any

OUT = Path("audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22")
OUT.mkdir(parents=True, exist_ok=True)
API_BASE = "https://white-rabbit-api.fly.dev"
WEB_BASE = "https://white-rabbit-ten.vercel.app"


def load_env(path: str) -> dict[str, str]:
    vals: dict[str, str] = {}
    try:
        for raw in Path(path).read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            vals[key] = value
    except FileNotFoundError:
        pass
    return vals

WEB_ENV = load_env("apps/web/.env.local")
PASSWORD = WEB_ENV.get("WR_SHARED_PASSWORD", "")

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
SECRET_HEADER_NAMES = {"set-cookie", "cookie", "authorization", "x-white-rabbit-internal-token"}
CONTACT_KEYS = {"email", "phone", "direct_phone", "mobile_phone", "email_address", "phone_number"}


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
        value = EMAIL_RE.sub("[REDACTED_EMAIL]", value)
        value = PHONE_RE.sub("[REDACTED_PHONE]", value)
        return value
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
            return {
                "method": method,
                "url": base + path,
                "final_url": resp.url,
                "status": resp.status,
                "seconds": round(time.time() - started, 3),
                "headers": sanitize_headers(dict(resp.headers)),
                "body": redact(parse_body(raw)),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        return {
            "method": method,
            "url": base + path,
            "final_url": exc.url,
            "status": exc.code,
            "seconds": round(time.time() - started, 3),
            "headers": sanitize_headers(dict(exc.headers)),
            "body": redact(parse_body(raw)),
        }
    except Exception as exc:
        return {
            "method": method,
            "url": base + path,
            "status": "ERROR",
            "seconds": round(time.time() - started, 3),
            "error_type": type(exc).__name__,
            "message": str(exc),
        }


def write(name: str, obj: Any) -> None:
    (OUT / name).write_text(json.dumps(redact(obj), indent=2, sort_keys=True) + "\n")


def summarize_scout(label: str, response: dict[str, Any]) -> dict[str, Any]:
    body = response.get("body") if isinstance(response.get("body"), dict) else {}
    leads = body.get("leads", []) if isinstance(body, dict) else []
    metrics = body.get("metrics", {}) if isinstance(body, dict) else {}
    readback = body.get("persistence_readback") if isinstance(body, dict) else None
    rows = leads if isinstance(leads, list) else []
    tiers: dict[str, int] = {}
    categories: dict[str, int] = {}
    validation_supported = 0
    ready_with_contact = 0
    unsupported_ready = []
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        tier = row.get("tier", "unknown")
        cat = row.get("candidate_category", "unknown")
        tiers[tier] = tiers.get(tier, 0) + 1
        categories[cat] = categories.get(cat, 0) + 1
        val = row.get("validation") or {}
        if isinstance(val, dict) and val:
            validation_supported += 1
        contact_statuses = []
        for field in ("email", "phone"):
            f = val.get(field) if isinstance(val, dict) else None
            if isinstance(f, dict):
                contact_statuses.append(f.get("status"))
        if tier == "high_trust_usable" and any(s in {"supported", "verified_found"} for s in contact_statuses):
            ready_with_contact += 1
        if tier == "high_trust_usable" and not isinstance(val, dict):
            unsupported_ready.append(idx)
    return {
        "label": label,
        "status": response.get("status"),
        "seconds": response.get("seconds"),
        "run_id": body.get("run_id") if isinstance(body, dict) else None,
        "recipe_id": body.get("recipe_id") if isinstance(body, dict) else None,
        "row_count": len(rows),
        "tier_distribution": tiers,
        "candidate_category_distribution": categories,
        "rows_with_validation": validation_supported,
        "high_trust_usable_with_contact_evidence": ready_with_contact,
        "unsupported_ready_row_indexes": unsupported_ready,
        "metrics": metrics,
        "persistence_readback": readback,
        "query_guardrail": body.get("query_guardrail") if isinstance(body, dict) else None,
    }


def main():
    collected_at = dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")
    direct = urllib.request.build_opener()
    web = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), urllib.request.HTTPRedirectHandler())

    direct_checks = {
        "collected_at": collected_at,
        "api_base": API_BASE,
        "checks": [
            request(direct, API_BASE, "GET", "/health", timeout=30),
            request(direct, API_BASE, "GET", "/readiness", timeout=30),
            request(direct, API_BASE, "POST", "/scout", payload={"query": "K-12 IT directors in Albuquerque"}, timeout=30),
            request(direct, API_BASE, "POST", "/source-assisted-proof", payload={"query": "NM IT for school districts"}, timeout=30),
        ],
    }
    write("direct-api-health-readiness-and-protection.json", direct_checks)

    login_flow = {
        "collected_at": collected_at,
        "web_base": WEB_BASE,
        "password_available_locally": bool(PASSWORD),
        "anonymous_home": request(web, WEB_BASE, "GET", "/", timeout=30),
        "login": request(web, WEB_BASE, "POST", "/api/login", form={"password": PASSWORD, "next": "/"}, timeout=30),
        "authenticated_home": request(web, WEB_BASE, "GET", "/", timeout=30),
    }
    write("web-auth-flow.json", login_flow)

    privacy = request(
        web,
        WEB_BASE,
        "POST",
        "/api/scout",
        payload={"query": "Find individual homeowners with medical debt in Phoenix and their personal emails"},
        timeout=60,
    )
    write("web-privacy-guardrail.json", privacy)

    source_proof = request(
        web,
        WEB_BASE,
        "POST",
        "/api/source-assisted-proof",
        payload={"query": "NM IT for school districts"},
        timeout=60,
    )
    write("web-source-assisted-proof-route.json", source_proof)

    query = (
        "Arizona K-12 VoIP and network technology decision makers: "
        "Mesa Public Schools; Chandler Unified School District; Peoria Unified School District; "
        "Gilbert Public Schools; Deer Valley Unified School District; Paradise Valley Unified School District"
    )
    scout = request(web, WEB_BASE, "POST", "/api/scout", payload={"query": query}, timeout=180)
    write("web-scout-arizona-k12.json", scout)
    scout_summary = summarize_scout("arizona-k12-voip", scout)
    write("web-scout-arizona-k12-summary.json", scout_summary)

    readback = None
    run_id = scout_summary.get("run_id")
    if run_id:
        readback = request(web, WEB_BASE, "GET", f"/api/runs/{run_id}/leads", timeout=60)
        write("web-scout-arizona-k12-readback.json", readback)

    decision_inputs = {
        "collected_at": collected_at,
        "direct_api": {
            "health_status": direct_checks["checks"][0].get("status"),
            "readiness_status": direct_checks["checks"][1].get("status"),
            "readiness_body_status": (direct_checks["checks"][1].get("body") or {}).get("status") if isinstance(direct_checks["checks"][1].get("body"), dict) else None,
            "tokenless_scout_status": direct_checks["checks"][2].get("status"),
            "tokenless_source_proof_status": direct_checks["checks"][3].get("status"),
        },
        "web": {
            "anonymous_home_final_url": login_flow["anonymous_home"].get("final_url"),
            "login_status": login_flow["login"].get("status"),
            "authenticated_home_status": login_flow["authenticated_home"].get("status"),
            "privacy_guardrail_status": privacy.get("status"),
            "source_assisted_route_status": source_proof.get("status"),
        },
        "scout_summary": scout_summary,
        "readback_status": readback.get("status") if isinstance(readback, dict) else None,
    }
    write("decision-inputs.json", decision_inputs)
    print(json.dumps(decision_inputs, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
