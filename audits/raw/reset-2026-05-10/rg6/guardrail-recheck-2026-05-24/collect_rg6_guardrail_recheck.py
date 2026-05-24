#!/usr/bin/env python3
"""RG6 production guardrail recheck against stable Vercel alias.

Writes sanitized evidence only. Does not print or save secrets/cookies/contacts.
"""
from __future__ import annotations

import datetime as dt
import http.cookiejar
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

OUT = Path("audits/raw/reset-2026-05-10/rg6/guardrail-recheck-2026-05-24")
WEB_BASE = "https://white-rabbit-ten.vercel.app"
QUERY = (
    "Arizona K-12 VoIP and network technology decision makers: "
    "Mesa Public Schools; Chandler Unified School District; Peoria Unified School District; "
    "Gilbert Public Schools; Deer Valley Unified School District; Paradise Valley Unified School District"
)
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
SECRET_HEADER_NAMES = {"set-cookie", "cookie", "authorization", "x-white-rabbit-internal-token"}
CONTACT_KEYS = {"email", "phone", "direct_phone", "mobile_phone", "email_address", "phone_number"}


def load_env(path: str) -> dict[str, str]:
    vals: dict[str, str] = {}
    try:
        for raw in Path(path).read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            vals[key] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return vals


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
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


def request(opener, method: str, path: str, *, payload=None, form=None, timeout=60) -> dict[str, Any]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["content-type"] = "application/json"
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["content-type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(WEB_BASE + path, data=data, headers=headers, method=method)
    started = time.time()
    try:
        with opener.open(req, timeout=timeout) as resp:
            raw = resp.read().decode(errors="replace")
            return {
                "method": method,
                "url": WEB_BASE + path,
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
            "url": WEB_BASE + path,
            "final_url": exc.url,
            "status": exc.code,
            "seconds": round(time.time() - started, 3),
            "headers": sanitize_headers(dict(exc.headers)),
            "body": redact(parse_body(raw)),
        }
    except Exception as exc:
        return {
            "method": method,
            "url": WEB_BASE + path,
            "status": "ERROR",
            "seconds": round(time.time() - started, 3),
            "error_type": type(exc).__name__,
            "message": str(exc),
        }


def write(name: str, obj: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(redact(obj), indent=2, sort_keys=True) + "\n")


def summarize_scout(response: dict[str, Any]) -> dict[str, Any]:
    body = response.get("body") if isinstance(response.get("body"), dict) else {}
    leads = body.get("leads", []) if isinstance(body, dict) else []
    rows = leads if isinstance(leads, list) else []
    tiers: dict[str, int] = {}
    categories: dict[str, int] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        tiers[row.get("tier", "unknown")] = tiers.get(row.get("tier", "unknown"), 0) + 1
        categories[row.get("candidate_category", "unknown")] = categories.get(row.get("candidate_category", "unknown"), 0) + 1
    guardrail = body.get("query_guardrail") if isinstance(body, dict) else None
    expected_guardrail_shape = guardrail is None or (isinstance(guardrail, dict) and guardrail.get("status") == "clear")
    return {
        "status": response.get("status"),
        "seconds": response.get("seconds"),
        "run_id": body.get("run_id") if isinstance(body, dict) else None,
        "row_count": len(rows),
        "tier_distribution": tiers,
        "candidate_category_distribution": categories,
        "query_guardrail_present": guardrail is not None,
        "query_guardrail": guardrail,
        "expected_pass_condition_met": response.get("status") == 200 and expected_guardrail_shape,
    }


def main() -> None:
    collected_at = dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")
    env_file = os.environ.get("WR_ENV_FILE", "apps/web/.env.local")
    password = load_env(env_file).get("WR_SHARED_PASSWORD", "")
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
        urllib.request.HTTPRedirectHandler(),
    )
    metadata = {
        "collected_at": collected_at,
        "web_base": WEB_BASE,
        "query": QUERY,
        "password_available_locally": bool(password),
        "scope": "RG6 production guardrail false-positive recheck only",
    }
    write("metadata.json", metadata)
    login = {
        "anonymous_home": request(opener, "GET", "/", timeout=30),
        "login": request(opener, "POST", "/api/login", form={"password": password, "next": "/"}, timeout=30),
        "authenticated_home": request(opener, "GET", "/", timeout=30),
    }
    write("web-auth-flow.json", login)
    scout = request(opener, "POST", "/api/scout", payload={"query": QUERY}, timeout=240)
    write("web-scout-arizona-k12-guardrail-recheck.json", scout)
    summary = {
        "collected_at": collected_at,
        "web_base": WEB_BASE,
        "auth": {
            "login_status": login["login"].get("status"),
            "authenticated_home_status": login["authenticated_home"].get("status"),
        },
        "scout_summary": summarize_scout(scout),
    }
    write("decision-inputs.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
