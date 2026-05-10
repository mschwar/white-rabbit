import asyncio
import os
import re
from typing import Any

import pytest

from core.orchestrator import scout

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PLACEHOLDER_EMAIL_RE = re.compile(
    r"^(not_available|noreply|no-reply|info|admin|contact|placeholder)@",
    re.IGNORECASE,
)
ROLE_TOKENS = (
    "director",
    "manager",
    "officer",
    "vp",
    "vice president",
    "chief",
    "executive",
    "coordinator",
    "supervisor",
    "head of",
    "principal",
    "lead",
)


needs_real_keys = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or not os.getenv("TAVILY_API_KEY"),
    reason="needs real keys",
)


QUERY_CASES: list[tuple[str, str, bool]] = [
    ("healthcare", "Healthcare IT directors in Phoenix", False),
    ("finance", "Financial services CISOs at mid-size banks in New York", False),
    ("manufacturing", "Manufacturing operations VPs in Detroit", False),
    ("k12", "K-12 IT directors in Albuquerque", True),
]


async def _run_scout(query: str) -> tuple[list[Any], Any]:
    return await scout(query)


def _assert_valid_name(lead: Any) -> None:
    name = (lead.name or "").strip()
    assert name, f"{lead.name!r}: name is empty"
    assert " " in name, f"{lead.name!r}: expected first and last name"
    lowered = name.lower()
    for token in ROLE_TOKENS:
        assert token not in lowered, f"{lead.name!r}: name contains role token {token!r}"


def _assert_valid_email(lead: Any) -> None:
    email = (lead.email or "").strip()
    if not email:
        return
    assert not PLACEHOLDER_EMAIL_RE.match(email), f"{lead.name!r}: placeholder email {email!r}"
    assert EMAIL_RE.match(email), f"{lead.name!r}: malformed email {email!r}"


def _gate_passed_from_evidence(lead: Any) -> bool:
    validation = getattr(lead, "validation", None)
    if validation is None:
        return False

    return (
        getattr(lead, "candidate_category", None) == "person_lead"
        and lead.fit_score >= 0.6
        and lead.evidence_score >= 0.6
        and lead.contact_score >= 0.6
        and validation.name.status == "supported"
        and validation.title.status == "supported"
        and validation.organization.status == "supported"
        and validation.source.status == "supported"
        and validation.email.status in {"verified_found", "deduced_with_pattern_evidence"}
    )


def _assert_lead_quality(lead: Any, *, allow_vertical_leak: bool) -> None:
    _assert_valid_name(lead)
    _assert_valid_email(lead)
    assert lead.gate_passed == _gate_passed_from_evidence(lead), (
        f"{lead.name!r}: gate_passed={lead.gate_passed} does not match "
        f"evidence=({lead.validation.name.status}, {lead.validation.title.status}, "
        f"{lead.validation.organization.status}, {lead.validation.email.status}, "
        f"{lead.validation.source.status}) scores=({lead.fit_score}, {lead.evidence_score}, {lead.contact_score})"
    )
    if not allow_vertical_leak:
        explanation = (lead.explanation or "").lower()
        assert "voip" not in explanation, f"{lead.name!r}: explanation leaks voip: {lead.explanation!r}"
        assert "telecom" not in explanation, f"{lead.name!r}: explanation leaks telecom: {lead.explanation!r}"


@needs_real_keys
@pytest.mark.integration
def test_scout_integration_healthcare_query():
    leads, _ = asyncio.run(_run_scout("Healthcare IT directors in Phoenix"))
    assert len(leads) > 0, "healthcare query returned no leads"
    for lead in leads:
        _assert_lead_quality(lead, allow_vertical_leak=False)


@needs_real_keys
@pytest.mark.integration
def test_scout_integration_finance_query():
    leads, _ = asyncio.run(_run_scout("Financial services CISOs at mid-size banks in New York"))
    assert len(leads) > 0, "finance query returned no leads"
    for lead in leads:
        _assert_lead_quality(lead, allow_vertical_leak=False)


@needs_real_keys
@pytest.mark.integration
def test_scout_integration_manufacturing_query():
    leads, _ = asyncio.run(_run_scout("Manufacturing operations VPs in Detroit"))
    assert len(leads) > 0, "manufacturing query returned no leads"
    for lead in leads:
        _assert_lead_quality(lead, allow_vertical_leak=False)


@needs_real_keys
@pytest.mark.integration
def test_scout_integration_k12_baseline_query():
    leads, _ = asyncio.run(_run_scout("K-12 IT directors in Albuquerque"))
    assert len(leads) > 0, "k12 baseline query returned no leads"
    for lead in leads:
        _assert_valid_name(lead)
        _assert_valid_email(lead)
        assert lead.gate_passed == _gate_passed_from_evidence(lead), (
            f"{lead.name!r}: gate_passed={lead.gate_passed} does not match "
            f"evidence=({lead.validation.name.status}, {lead.validation.title.status}, "
            f"{lead.validation.organization.status}, {lead.validation.email.status}, "
            f"{lead.validation.source.status}) scores=({lead.fit_score}, {lead.evidence_score}, {lead.contact_score})"
        )


@needs_real_keys
@pytest.mark.integration
def test_scout_integration_gate_passed_matches_subscores():
    for label, query, allow_vertical_leak in QUERY_CASES:
        leads, _ = asyncio.run(_run_scout(query))
        assert len(leads) > 0, f"{label} query returned no leads"
        for lead in leads:
            _assert_lead_quality(lead, allow_vertical_leak=allow_vertical_leak)
