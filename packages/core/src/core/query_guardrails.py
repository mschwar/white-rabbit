from __future__ import annotations

import re
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field

QueryGuardrailStatus = Literal['clear', 'needs_more_detail', 'blocked']

US_STATE_NAMES: tuple[str, ...] = (
    'alabama',
    'alaska',
    'arizona',
    'arkansas',
    'california',
    'colorado',
    'connecticut',
    'delaware',
    'district of columbia',
    'washington dc',
    'd.c',
    'florida',
    'georgia',
    'hawaii',
    'idaho',
    'illinois',
    'indiana',
    'iowa',
    'kansas',
    'kentucky',
    'louisiana',
    'maine',
    'maryland',
    'massachusetts',
    'michigan',
    'minnesota',
    'mississippi',
    'missouri',
    'montana',
    'nebraska',
    'nevada',
    'new hampshire',
    'new jersey',
    'new mexico',
    'new york',
    'north carolina',
    'north dakota',
    'ohio',
    'oklahoma',
    'oregon',
    'pennsylvania',
    'rhode island',
    'south carolina',
    'south dakota',
    'tennessee',
    'texas',
    'utah',
    'vermont',
    'virginia',
    'washington',
    'west virginia',
    'wisconsin',
    'wyoming',
)

US_STATE_CODES: dict[str, str] = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'DC': 'District of Columbia',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
}

# Two-letter state codes that collide with common English words or non-location B2B acronyms
# unless anchored by uppercase geographic context or a location preposition/comma.
_AMBIGUOUS_STATE_CODES = frozenset(
    {'IN', 'OR', 'ME', 'HI', 'OK', 'DE', 'LA', 'MA', 'PA', 'CO', 'OH', 'AL', 'MD', 'VA', 'ID', 'CT'}
)
_UNAMBIGUOUS_UPPER_STATE_RE = re.compile(
    r'\b(?:' + '|'.join(sorted(set(US_STATE_CODES) - _AMBIGUOUS_STATE_CODES)) + r')\b'
)
_CONTEXTUAL_STATE_CODE_RE = re.compile(
    r'(?:,\s*|\b(?:in|near|around|across|from|throughout)\s+(?:[A-Za-z.\'-]+\s+){0,3})'
    r'\b(' + '|'.join(sorted(US_STATE_CODES)) + r')\b',
    re.IGNORECASE,
)
_TRAILING_UPPER_STATE_CODE_RE = re.compile(
    r'(?:,\s*|\s+)\b(' + '|'.join(sorted(US_STATE_CODES)) + r')\b\s*$'
)

_CITY_NAME_HINTS = (
    'albuquerque',
    'santa fe',
    'phoenix',
    'detroit',
    'hackensack',
    'chicago',
    'houston',
    'dallas',
    'austin',
    'san antonio',
    'los angeles',
    'san francisco',
    'san diego',
    'seattle',
    'portland',
    'denver',
    'miami',
    'tampa',
    'orlando',
    'atlanta',
    'boston',
    'philadelphia',
    'pittsburgh',
    'charlotte',
    'raleigh',
    'nashville',
    'memphis',
    'minneapolis',
    'milwaukee',
    'indianapolis',
    'columbus',
    'cleveland',
    'cincinnati',
    'kansas city',
    'st. louis',
    'las vegas',
    'salt lake city',
    'baltimore',
    'newark',
    'boise',
)

_ROLE_HINTS = (
    'ciso',
    'cisos',
    'cio',
    'cios',
    'cto',
    'ctos',
    'coo',
    'coos',
    'cfo',
    'cfos',
    'ceo',
    'ceos',
    'chief',
    'officer',
    'officers',
    'director',
    'directors',
    'manager',
    'managers',
    'leader',
    'leaders',
    'operations leader',
    'operations leaders',
    'operations manager',
    'operations managers',
    'contractor',
    'contractors',
    'procurement',
    'procurement manager',
    'procurement managers',
    'procurement leader',
    'procurement leaders',
    'buyer',
    'buyers',
    'underwriter',
    'underwriters',
    'superintendent',
    'superintendents',
    'administrator',
    'administrators',
    'executive',
    'executives',
    'partner',
    'partners',
    'vp',
    'vps',
    'vice president',
    'vice presidents',
    'head of',
    'heads of',
    'owner',
    'owners',
    'founder',
    'founders',
    'principal',
    'principals',
    'chair',
    'chairs',
    'it director',
    'it directors',
    'technology director',
    'technology directors',
    'it leader',
    'it leaders',
    'technology leader',
    'technology leaders',
    'sales leader',
    'sales leaders',
    'decision maker',
    'decision makers',
    'general manager',
    'general managers',
    'plant manager',
    'plant managers',
)

_ORG_HINTS = (
    'k-12',
    'k12',
    'school',
    'schools',
    'district',
    'districts',
    'financial services',
    'finance',
    'bank',
    'banks',
    'credit union',
    'credit unions',
    'insurance',
    'manufacturing',
    'manufacturer',
    'manufacturers',
    'food and beverage',
    'construction',
    'design-build',
    'contractor',
    'contractors',
    'company',
    'companies',
    'org',
    'orgs',
    'organization',
    'organizations',
    'agency',
    'agencies',
    'clinic',
    'clinics',
    'medical',
    'medicine',
    'billing',
    'hospital',
    'hospitals',
    'university',
    'universities',
    'college',
    'colleges',
    'nonprofit',
    'nonprofits',
    'smb',
    'smbs',
    'startup',
    'startups',
    'firm',
    'firms',
    'practice',
    'practices',
    'department',
    'departments',
    'public sector',
    'municipality',
    'municipalities',
    'healthcare',
    'education',
    'telecom',
    'logistics',
    'retail',
    'lumber',
    'hospitality',
    'energy',
    'software',
    'saas',
)

_LOCATION_PREPOSITION_HINTS = (
    'based in',
)

_LOCATION_NAME_HINTS = US_STATE_NAMES + _CITY_NAME_HINTS

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

_STRICT_OFF_TOPIC_HINTS = (
    'advice',
    'brainstorm',
    'draft',
    'summarize',
    'summary',
    'explain',
    'teach me',
    'general research',
    'research me',
    'help me',
    'what is',
    'how do i',
    'how to',
    'write a',
    'write an',
    'write me',
    'python script',
    'javascript',
)

# Generic words that appear legitimately in B2B verticals/titles (e.g. "design-build",
# "underwriter", "medical billing and coding", "strategy directors") and only indicate
# off-topic prompts when B2B role + organization context is absent.
_CONTEXTUAL_OFF_TOPIC_HINTS = (
    'strategy',
    'write',
    'code',
    'build',
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
    'ammunition',
    'stalk',
    'stalking',
    'dox',
    'doxx',
    'doxxing',
    'hack',
    'hacking',
    'hacker',
    'hackers',
    'phish',
    'phishing',
)

_STRICT_PRIVACY_HINTS = (
    'personal email',
    'personal emails',
    'personal phone',
    'personal phones',
    'cell phone',
    'cell phones',
    'home address',
    'home addresses',
    'residential address',
    'residential addresses',
    'private person',
    'private people',
    'private resident',
    'private residents',
    'private citizen',
    'private citizens',
    'private individual',
    'private individuals',
    'home refinance',
    'home mortgage',
    'mortgage refinance',
    'homeowner',
    'homeowners',
    'vacation photo',
    'vacation photos',
    'parents',
    'kids',
    'children',
    'spouse',
    'spouses',
    'neighbor',
    'neighbors',
    'personal contact',
    'personal contacts',
)

# Words like "family" ("family medicine clinics") and "resident" ("chief resident at teaching hospitals")
# are valid in B2B healthcare/property verticals when paired with B2B role + organization context.
_CONTEXTUAL_PRIVACY_HINTS = (
    'family',
    'resident',
    'residents',
)


class QueryGuardrailResult(BaseModel):
    status: QueryGuardrailStatus
    message: str
    suggestions: list[str] = Field(default_factory=list)
    missing_criteria: list[str] = Field(default_factory=list)


def _normalize(query: str) -> str:
    return ' '.join(query.lower().split())


@lru_cache(maxsize=64)
def _compile_word_boundary_pattern(phrases: tuple[str, ...]) -> re.Pattern[str]:
    cleaned = [re.escape(phrase.strip()) for phrase in phrases if phrase and phrase.strip()]
    if not cleaned:
        return re.compile(r'(?!x)x')
    # Sort longest-first so multi-word phrases match deterministically.
    cleaned.sort(key=len, reverse=True)
    return re.compile(r'\b(?:' + '|'.join(cleaned) + r')\b', re.IGNORECASE)


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return _compile_word_boundary_pattern(phrases).search(text) is not None


def _contains_word_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return _contains_any(text, phrases)


def extract_us_state_codes(raw_query: str) -> list[str]:
    """Extract matched 2-letter US state (+ DC) postal codes from a query."""
    collapsed = ' '.join(raw_query.split())
    if not collapsed:
        return []
    found: list[str] = []
    for match in _UNAMBIGUOUS_UPPER_STATE_RE.finditer(collapsed):
        code = match.group(0).upper()
        if code not in found:
            found.append(code)
    for match in _TRAILING_UPPER_STATE_CODE_RE.finditer(collapsed):
        code = match.group(1).upper()
        if code not in found:
            found.append(code)
    for match in _CONTEXTUAL_STATE_CODE_RE.finditer(collapsed):
        code = match.group(1).upper()
        if code not in found:
            found.append(code)
    return found


def _has_role_target(text: str) -> bool:
    return _contains_any(text, _ROLE_HINTS)


def _has_org_target(text: str) -> bool:
    return _contains_any(text, _ORG_HINTS)


def _has_location(normalized_text: str, raw_query: str = '') -> bool:
    if _contains_any(normalized_text, _LOCATION_NAME_HINTS):
        return True
    if _contains_any(normalized_text, _LOCATION_PREPOSITION_HINTS):
        return True
    if extract_us_state_codes(raw_query or normalized_text):
        return True
    # Recognize explicit "in/near/around/across <Place>" phrasing when a non-empty place follows.
    return bool(
        re.search(
            r'\b(?:in|near|around|across)\s+[a-z]{3,}',
            normalized_text,
        )
    )


def _has_lead_intent(text: str) -> bool:
    return _contains_any(text, _LEAD_INTENT_HINTS)


def _looks_off_topic(text: str, *, has_b2b_context: bool) -> bool:
    if _contains_any(text, _STRICT_OFF_TOPIC_HINTS):
        return True
    return not has_b2b_context and _contains_any(text, _CONTEXTUAL_OFF_TOPIC_HINTS)


def _looks_unsafe(text: str) -> bool:
    return _contains_any(text, _WEAPON_HINTS)


def _looks_privacy_sensitive(text: str, *, has_b2b_context: bool) -> bool:
    if _contains_any(text, _STRICT_PRIVACY_HINTS):
        return True
    return not has_b2b_context and _contains_any(text, _CONTEXTUAL_PRIVACY_HINTS)


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
    has_b2b_context = has_role_target and has_org_target
    has_location = _has_location(normalized, query)
    looks_unsafe = _looks_unsafe(normalized)
    looks_privacy_sensitive = _looks_privacy_sensitive(normalized, has_b2b_context=has_b2b_context)
    looks_off_topic = _looks_off_topic(normalized, has_b2b_context=has_b2b_context)

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
