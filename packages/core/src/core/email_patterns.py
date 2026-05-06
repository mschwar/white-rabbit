from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
import re
from typing import Any

from pydantic import BaseModel, Field
from .models import Lead


class EmailPatternInsight(BaseModel):
    organization: str
    domain: str
    inferred_pattern: str
    matched_leads: int
    total_leads: int
    confidence: float
    examples: list[str] = Field(default_factory=list)


def _split_name(name: str) -> tuple[str, str]:
    parts = [part for part in re.split(r"\s+", name.strip()) if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]


def _clean_part(value: str) -> str:
    return re.sub(r"[^a-z]", "", value.lower())


def _classify_local_part(local_part: str, first: str, last: str) -> str:
    local = re.sub(r"[._-]+", ".", local_part.strip().lower())
    local_compact = _clean_part(local)
    first_clean = _clean_part(first)
    last_clean = _clean_part(last)

    if not first_clean or not last_clean:
        return "unknown"

    if local == f"{first_clean}.{last_clean}":
        return "first.last"
    if local == f"{first_clean}{last_clean}":
        return "firstlast"
    if local == f"{first_clean[0]}.{last_clean}":
        return "first_initial.last"
    if local == f"{first_clean[0]}{last_clean}":
        return "first_initiallast"
    if local == first_clean:
        return "first"
    if local == last_clean:
        return "last"
    if "." in local and local_compact == f"{first_clean}{last_clean}":
        return "first.last"
    if "." in local and local_compact == f"{first_clean[0]}{last_clean}":
        return "first_initial.last"
    if local.startswith(first_clean) and local.endswith(last_clean):
        return "first.last"
    return "unknown"


def _email_domain(email: str) -> str:
    if "@" not in email:
        return ""
    return email.rsplit("@", 1)[1].strip().lower()


def _lead_pattern(lead: Lead | Mapping[str, Any]) -> tuple[str, str, str] | None:
    if isinstance(lead, Lead):
        name = lead.name
        email = lead.email
        organization = lead.organization
    else:
        name = str(lead.get("name") or lead.get("Name") or "")
        email = str(lead.get("email") or lead.get("Email") or lead.get("Email (Deduced)") or "")
        organization = str(lead.get("organization") or lead.get("Organization") or "")

    if not email or "@" not in email:
        return None

    first, last = _split_name(name)
    local_part, _domain = email.split("@", 1)
    pattern = _classify_local_part(local_part, first, last)
    return organization or "", _email_domain(email), pattern


def infer_email_patterns(leads: Iterable[Lead | Mapping[str, Any]]) -> list[EmailPatternInsight]:
    groups: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)

    for lead in leads:
        lead_data = _lead_pattern(lead)
        if lead_data is None:
            continue
        organization, domain, pattern = lead_data
        if not organization or not domain:
            continue
        if isinstance(lead, Lead):
            email = lead.email
        else:
            email = str(lead.get("email") or lead.get("Email") or lead.get("Email (Deduced)") or "")
        groups[(organization, domain)].append((pattern, email))

    insights: list[EmailPatternInsight] = []
    for (organization, domain), pattern_rows in sorted(groups.items()):
        observed_patterns = [pattern for pattern, _ in pattern_rows if pattern != "unknown"]
        if observed_patterns:
            counts = Counter(observed_patterns)
            inferred_pattern, matched_leads = counts.most_common(1)[0]
            confidence = round(matched_leads / len(observed_patterns), 3)
        else:
            inferred_pattern = "unknown"
            matched_leads = 0
            confidence = 0.0

        examples = [email for pattern, email in pattern_rows if pattern == inferred_pattern][:3]
        insights.append(
            EmailPatternInsight(
                organization=organization,
                domain=domain,
                inferred_pattern=inferred_pattern,
                matched_leads=matched_leads,
                total_leads=len(pattern_rows),
                confidence=confidence,
                examples=examples,
            )
        )

    return insights
