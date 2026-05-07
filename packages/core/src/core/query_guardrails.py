from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

QueryGuardrailStatus = Literal['clear', 'needs_more_detail', 'blocked']

_ROLE_HINTS = (
    'director',
    'manager',
    'vp',
    'vice president',
    'head of',
    'owner',
    'founder',
    'principal',
    'chair',
    'cto',
    'cio',
    'it leader',
    'technology leader',
)

_ORG_HINTS = (
    'k-12',
    'k12',
    'school',
    'district',
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
    'write',
    'draft',
    'summarize',
    'summary',
    'explain',
    'code',
    'build',
    'brainstorm',
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


class QueryGuardrailResult(BaseModel):
    status: QueryGuardrailStatus
    message: str
    suggestions: list[str] = Field(default_factory=list)
    missing_criteria: list[str] = Field(default_factory=list)


def _normalize(query: str) -> str:
    return ' '.join(query.lower().split())


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def _has_role_target(text: str) -> bool:
    return _contains_any(text, _ROLE_HINTS)


def _has_org_target(text: str) -> bool:
    return _contains_any(text, _ORG_HINTS)


def _has_location(text: str) -> bool:
    return _contains_any(text, _LOCATION_HINTS)


def _has_lead_intent(text: str) -> bool:
    return _contains_any(text, _LEAD_INTENT_HINTS)


def _looks_off_topic(text: str) -> bool:
    return _contains_any(text, _OFF_TOPIC_HINTS)


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
    has_lead_intent = _has_lead_intent(normalized)
    looks_off_topic = _looks_off_topic(normalized)

    if looks_off_topic and not has_lead_intent:
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
