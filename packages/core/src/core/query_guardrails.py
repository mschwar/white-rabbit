from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

QueryGuardrailStatus = Literal['clear', 'needs_more_detail', 'blocked']

_ROLE_HINTS = (
    'ciso',
    'cio',
    'cto',
    'coo',
    'cfo',
    'director',
    'manager',
    'operations leader',
    'operations leaders',
    'operations manager',
    'contractor',
    'contractors',
    'procurement manager',
    'procurement leader',
    'vp',
    'vice president',
    'head of',
    'owner',
    'founder',
    'principal',
    'chair',
    'it director',
    'technology director',
    'it leader',
    'technology leader',
    'sales leader',
    'sales leaders',
    'decision maker',
    'decision makers',
    'general manager',
    'plant manager',
)

_ORG_HINTS = (
    'k-12',
    'k12',
    'school',
    'district',
    'financial services',
    'manufacturing',
    'food and beverage',
    'construction',
    'contractor',
    'contractors',
    'company',
    'org',
    'organization',
    'agency',
    'clinic',
    'hospital',
    'university',
    'college',
    'nonprofit',
    'smb',
    'startup',
    'firm',
    'practice',
    'department',
    'public sector',
    'healthcare',
    'education',
    'telecom',
    'logistics',
    'retail',
    'hospitality',
    'energy',
)

_LOCATION_HINTS = (
    ' in ',
    ' near ',
    ' around ',
    ' based in ',
    ' across ',
    ' from ',
    ' california',
    ' texas',
    ' new york',
    ' florida',
    ' new mexico',
    ' colorado',
    ' arizona',
    ' oklahoma',
    ' kansas',
    ' utah',
    ' nevada',
    ' albuquerque',
    ' santa fe',
)

_LOCATION_NAME_HINTS = (
    'california',
    'texas',
    'new york',
    'florida',
    'new mexico',
    'colorado',
    'arizona',
    'oklahoma',
    'kansas',
    'utah',
    'nevada',
    'albuquerque',
    'santa fe',
    'phoenix',
    'detroit',
    'washington',
    'illinois',
)

_LEAD_INTENT_HINTS = (
    'lead',
    'leads',
    'prospect',
    'prospects',
    'prospecting',
    'contact',
    'contacts',
    'decision maker',
    'decision makers',
    'buyer',
    'buyers',
    'account',
    'accounts',
    'target',
    'targets',
    'find',
    'list',
    'directory',
    'directory of',
)

_OFF_TOPIC_HINTS = (
    'advice',
    'strategy',
    'brainstorm',
    'write',
    'draft',
    'summarize',
    'summary',
    'explain',
    'teach me',
    'code',
    'build',
    'general research',
    'research me',
    'help me',
    'what is',
    'how do i',
    'how to',
    'compare',
    'optimize',
    'review',
)

_WEAPON_HINTS = (
    'weapon',
    'weapons',
    'gun',
    'guns',
    'firearm',
    'firearms',
    'bomb',
    'bombs',
    'explosive',
    'explosives',
    'ammo',
    'stalking',
    'dox',
    'doxx',
    'hack',
    'phish',
)

_PRIVACY_HINTS = (
    'personal email',
    'personal phone',
    'cell phone',
    'home address',
    'private person',
    'private people',
    'home refinance',
    'home mortgage',
    'mortgage refinance',
    'homeowner',
    'homeowners',
    'vacation photo',
    'vacation photos',
    'family',
    'parents',
    'kids',
    'children',
    'spouse',
    'resident',
    'residents',
    'neighbor',
    'neighbors',
    'personal contact',
    'personal contacts',
)


class QueryGuardrailResult(BaseModel):
    status: QueryGuardrailStatus
    message: str
    suggestions: list[str] = Field(default_factory=list)
    missing_criteria: list[str] = Field(default_factory=list)


def _normalize(query: str) -> str:
    return ' '.join(query.lower().split())


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    for phrase in phrases:
        if not phrase:
            continue
        if len(phrase) <= 3 and phrase.isalpha():
            if re.search(rf'(?<!\w){re.escape(phrase)}(?!\w)', text):
                return True
            continue
        if phrase in text:
            return True
    return False


def _contains_word_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    for phrase in phrases:
        if re.search(rf'(?<!\w){re.escape(phrase)}(?!\w)', text):
            return True
    return False


def _has_role_target(text: str) -> bool:
    return _contains_any(text, _ROLE_HINTS)


def _has_org_target(text: str) -> bool:
    return _contains_any(text, _ORG_HINTS)


def _has_location(text: str) -> bool:
    return _contains_any(text, _LOCATION_HINTS) or _contains_word_phrase(text, _LOCATION_NAME_HINTS)


def _has_lead_intent(text: str) -> bool:
    return _contains_any(text, _LEAD_INTENT_HINTS)


def _looks_off_topic(text: str) -> bool:
    return _contains_any(text, _OFF_TOPIC_HINTS)


def _looks_unsafe(text: str) -> bool:
    return _contains_any(text, _WEAPON_HINTS)


def _looks_privacy_sensitive(text: str) -> bool:
    return _contains_any(text, _PRIVACY_HINTS)


def evaluate_query_guardrails(query: str) -> QueryGuardrailResult:
    normalized = _normalize(query)

    if not normalized:
        return QueryGuardrailResult(
            status='blocked',
            message='White Rabbit needs a lead-generation query. Name the people or organizations you want to target.',
            suggestions=[
                'Try: K-12 IT directors in Albuquerque',
                'Try: operations managers at regional clinics in New Mexico',
            ],
            missing_criteria=['target people or organizations'],
        )

    has_role_target = _has_role_target(normalized)
    has_org_target = _has_org_target(normalized)
    has_location = _has_location(normalized)
    looks_off_topic = _looks_off_topic(normalized)
    looks_unsafe = _looks_unsafe(normalized)
    looks_privacy_sensitive = _looks_privacy_sensitive(normalized)

    if looks_unsafe:
        return QueryGuardrailResult(
            status='blocked',
            message='White Rabbit blocks weapon, harm, and surveillance requests. Reframe this around legitimate B2B lead generation.',
            suggestions=[
                'Try: IT directors at school districts in New Mexico',
                'Try: procurement managers at mid-market manufacturers in Texas',
            ],
            missing_criteria=['target people or organizations'],
        )

    if looks_privacy_sensitive:
        return QueryGuardrailResult(
            status='blocked',
            message='White Rabbit only runs privacy-safe B2B lead-generation queries. Queries aimed at private people, home/consumer targeting, or personal contact discovery are blocked before search.',
            suggestions=[
                'Try: IT directors at school districts in New Mexico',
                'Try: procurement managers at mid-market manufacturers in Texas',
            ],
            missing_criteria=['target people or organizations'],
        )

    if looks_off_topic:
        return QueryGuardrailResult(
            status='blocked',
            message='White Rabbit only runs lead-generation queries. Reframe this around people or organizations to target instead of advice, writing, code, or general research.',
            suggestions=[
                'Try: IT directors at school districts in New Mexico',
                'Try: procurement managers at mid-market manufacturers in Texas',
            ],
            missing_criteria=['target people or organizations'],
        )

    missing_criteria: list[str] = []
    suggestions: list[str] = []

    if not has_role_target:
        missing_criteria.append('target title or role')
        suggestions.append('Add a title or role, such as director, manager, VP, or owner.')
    if not has_org_target:
        missing_criteria.append('company type or vertical')
        suggestions.append('Add a vertical or company type, such as school district, clinic, nonprofit, or SMB.')
    if not has_location:
        missing_criteria.append('location')
        suggestions.append('Add a geography, such as a city, state, or region.')

    if missing_criteria:
        return QueryGuardrailResult(
            status='needs_more_detail',
            message='This is a lead-generation query, but tighter results will come from adding a title, vertical/company type, and location.',
            suggestions=suggestions,
            missing_criteria=missing_criteria,
        )

    return QueryGuardrailResult(
        status='clear',
        message='Query looks like a lead-generation request.',
    )
