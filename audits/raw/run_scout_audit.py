"""Phase 2 audit driver — run the real scout() pipeline against 4 locked queries.

Run from repo root:
    cd packages/core && .venv/bin/python ../../audits/raw/run_scout_audit.py

Captures JSON per query and a quality matrix that scores each lead on:
- name: looks like a real first+last person name (not a title)
- email: real-format or empty (never not_available@*)
- explanation: cites query intent, no vertical leakage
- gate_passed self-consistency vs the three sub-scores
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Make sure src is importable
ROOT = Path(__file__).resolve().parents[2]
CORE_SRC = ROOT / "packages" / "core" / "src"
sys.path.insert(0, str(CORE_SRC))

# Load env from apps/api/.env
from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / "apps" / "api" / ".env")

from core.orchestrator import scout  # noqa: E402

QUERIES = {
    "Q1_healthcare": "Healthcare IT directors in Phoenix",
    "Q2_finance": "Financial services CISOs at mid-size banks in New York",
    "Q3_manufacturing": "Manufacturing operations VPs in Detroit",
    "Q4_k12_albuquerque": "K-12 IT directors in Albuquerque",
}

ROLE_TOKENS = {
    "director", "manager", "officer", "vp", "vice president", "chief", "executive",
    "coordinator", "supervisor", "head of", "lead", "principal",
}
VERTICAL_LEAK_TOKENS = {
    "healthcare": ["voip", "telecom", "telecommunications"],
    "finance": ["voip", "telecom", "telecommunications"],
    "manufacturing": ["voip", "telecom", "telecommunications"],
    "k12_albuquerque": [],  # baseline — VoIP language is at least adjacent here
}
EMAIL_PLACEHOLDER_RE = re.compile(r"^(not_available|noreply|no-reply|info|admin|contact|placeholder)@", re.IGNORECASE)
EMAIL_FORMAT_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def looks_like_real_name(name: str) -> tuple[bool, str]:
    if not name or not name.strip():
        return False, "empty"
    parts = name.strip().split()
    if len(parts) < 2:
        return False, f"single-word: '{name}'"
    lower = name.lower()
    for tok in ROLE_TOKENS:
        if tok in lower:
            return False, f"contains role token '{tok}'"
    return True, "ok"


def email_verdict(email: str) -> tuple[str, str]:
    """Return (status, detail). Status one of: real, empty, placeholder, malformed."""
    if not email or not email.strip():
        return "empty", "blank — acceptable"
    if EMAIL_PLACEHOLDER_RE.match(email):
        return "placeholder", f"matches placeholder pattern: {email}"
    if not EMAIL_FORMAT_RE.match(email):
        return "malformed", f"not a valid format: {email}"
    return "real", email


def explanation_verdict(explanation: str, query_key: str) -> tuple[bool, str]:
    if not explanation:
        return False, "empty explanation"
    leaks = VERTICAL_LEAK_TOKENS.get(query_key.replace("Q1_", "").replace("Q2_", "").replace("Q3_", "").replace("Q4_", ""), [])
    lower = explanation.lower()
    for leak in leaks:
        if leak in lower:
            return False, f"contains vertical leak '{leak}'"
    return True, "ok"


def gate_consistency(lead) -> tuple[bool, str]:
    expected = (lead.fit_score >= 0.6 and lead.evidence_score >= 0.6 and lead.contact_score >= 0.6)
    if lead.gate_passed != expected:
        return False, f"gate_passed={lead.gate_passed} but scores ({lead.fit_score}, {lead.evidence_score}, {lead.contact_score}) imply {expected}"
    return True, "ok"


async def run_one(key: str, query: str) -> dict:
    print(f"\n=== {key}: {query} ===")
    if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("TAVILY_API_KEY"):
        return {"error": "missing API keys"}

    started = datetime.utcnow()
    try:
        leads, metrics = await scout(query)
    except Exception as exc:
        print(f"  FAILED: {exc}")
        return {"key": key, "query": query, "error": str(exc)}

    elapsed = (datetime.utcnow() - started).total_seconds()
    print(f"  -> {len(leads)} leads in {elapsed:.1f}s, est cost ${metrics.estimated_cost_usd:.4f}")

    leads_out = []
    quality = {"name_ok": 0, "name_bad": 0, "email_real": 0, "email_empty": 0, "email_placeholder": 0,
               "email_malformed": 0, "explanation_ok": 0, "explanation_leak": 0, "gate_ok": 0, "gate_bad": 0}
    for lead in leads:
        name_ok, name_detail = looks_like_real_name(lead.name)
        email_status, email_detail = email_verdict(lead.email)
        expl_ok, expl_detail = explanation_verdict(lead.explanation, key)
        gate_ok, gate_detail = gate_consistency(lead)

        if name_ok:
            quality["name_ok"] += 1
        else:
            quality["name_bad"] += 1
        quality[f"email_{email_status}"] += 1
        if expl_ok:
            quality["explanation_ok"] += 1
        else:
            quality["explanation_leak"] += 1
        if gate_ok:
            quality["gate_ok"] += 1
        else:
            quality["gate_bad"] += 1

        leads_out.append({
            "name": lead.name,
            "title": lead.title,
            "organization": lead.organization,
            "email": lead.email,
            "email_status": lead.email_status,
            "source_url": lead.source_url,
            "confidence": lead.confidence,
            "fit_score": lead.fit_score,
            "evidence_score": lead.evidence_score,
            "contact_score": lead.contact_score,
            "gate_passed": lead.gate_passed,
            "why_target": lead.why_target,
            "icebreaker": lead.icebreaker,
            "explanation": lead.explanation,
            "_audit": {
                "name_ok": name_ok,
                "name_detail": name_detail,
                "email_status": email_status,
                "email_detail": email_detail,
                "explanation_ok": expl_ok,
                "explanation_detail": expl_detail,
                "gate_consistent": gate_ok,
                "gate_detail": gate_detail,
            },
        })

    out = {
        "key": key,
        "query": query,
        "elapsed_s": round(elapsed, 2),
        "lead_count": len(leads),
        "metrics": {
            "estimated_cost_usd": metrics.estimated_cost_usd,
            "input_tokens": metrics.input_tokens,
            "output_tokens": metrics.output_tokens,
            "tavily_searches": metrics.tavily_searches,
        },
        "quality_summary": quality,
        "leads": leads_out,
    }
    print(f"  quality: {quality}")
    return out


async def main():
    out_dir = ROOT / "audits" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for key, query in QUERIES.items():
        result = await run_one(key, query)
        results[key] = result
        out_file = out_dir / f"scout-{key}.json"
        out_file.write_text(json.dumps(result, indent=2))
        print(f"  wrote {out_file.relative_to(ROOT)}")

    # Aggregate quality matrix
    rows = ["| Query | Leads | Names ok | Emails real | Emails placeholder | Explanation leaks | Gate inconsistencies |",
            "|-------|-------|----------|-------------|--------------------|--------------------|----------------------|"]
    for key, r in results.items():
        if "error" in r:
            rows.append(f"| {key} | ERROR: {r['error']} | | | | | |")
            continue
        q = r["quality_summary"]
        rows.append(f"| {key} | {r['lead_count']} | {q['name_ok']}/{r['lead_count']} | {q['email_real']}/{r['lead_count']} | {q['email_placeholder']}/{r['lead_count']} | {q['explanation_leak']}/{r['lead_count']} | {q['gate_bad']}/{r['lead_count']} |")
    matrix_path = out_dir / "lead-quality-matrix.md"
    matrix_path.write_text("# Lead quality matrix — Phase 2\n\n" + "\n".join(rows) + "\n")
    print(f"\nwrote {matrix_path.relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())
