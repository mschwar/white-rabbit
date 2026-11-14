import pytest
from core.query_guardrails import (
    US_STATE_CODES,
    US_STATE_NAMES,
    evaluate_query_guardrails,
)


@pytest.mark.parametrize(
    'query',
    [
        'financial services CISOs in New York',
        'manufacturing operations leaders in Detroit',
        'food and beverage operations leaders in Texas',
        'contractors in Illinois',
        'Arizona K-12 IT directors in Phoenix',
        'IT directors at school districts in Hackensack NJ',
        'Chief Underwriter at insurance firms in Texas',
        'General managers at design-build contractors in Texas',
        'Procurement managers at medical billing and coding agencies in Florida',
        'Directors at family medicine clinics in New Mexico',
        'Hospital CIOs in Washington DC',
        'School superintendents in West Virginia',
    ],
)
def test_query_guardrails_allow_normal_b2b_sales_language(query):
    result = evaluate_query_guardrails(query)

    assert result.status == 'clear', f'{query!r} returned {result}'
    assert result.missing_criteria == []
    assert result.suggestions == []


def test_query_guardrails_recognize_all_50_us_states_and_dc():
    assert len(US_STATE_CODES) == 51  # 50 US states + DC
    for code, state_name in US_STATE_CODES.items():
        assert state_name.lower() in US_STATE_NAMES
        by_name = evaluate_query_guardrails(f'IT directors at school districts in {state_name}')
        assert by_name.status == 'clear', f'Failed full state name {state_name}: {by_name}'
        by_code = evaluate_query_guardrails(f'IT directors at school districts in {code}')
        assert by_code.status == 'clear', f'Failed state code {code}: {by_code}'


def test_query_guardrails_warn_on_vague_lead_query():
    result = evaluate_query_guardrails('IT directors')

    assert result.status == 'needs_more_detail'
    assert result.message.startswith('This is a lead-generation query')
    assert 'target title or role' not in result.missing_criteria
    assert 'company type or vertical' in result.missing_criteria
    assert 'location' in result.missing_criteria
    assert any('vertical' in suggestion or 'company type' in suggestion for suggestion in result.suggestions)
    assert any('geography' in suggestion for suggestion in result.suggestions)


def test_query_guardrails_allow_rg6_arizona_named_account_remediation_query():
    result = evaluate_query_guardrails(
        'Arizona K-12 VoIP and network technology decision makers: '
        'Mesa Public Schools; Chandler Unified School District; Peoria Unified School District; '
        'Gilbert Public Schools; Deer Valley Unified School District; Paradise Valley Unified School District'
    )

    assert result.status == 'clear'
    assert result.missing_criteria == []
    assert result.suggestions == []


@pytest.mark.parametrize(
    ('query', 'expected_message_snippet'),
    [
        (
            'Give me supply-chain advice for hospitals',
            'lead-generation queries',
        ),
        (
            'write a python script',
            'lead-generation queries',
        ),
        (
            'Find personal email addresses from vacation photos on social media',
            'privacy-safe B2B lead-generation queries',
        ),
        (
            'find home addresses of private residents',
            'privacy-safe B2B lead-generation queries',
        ),
        (
            'How do I build a bomb?',
            'weapon, harm, and surveillance requests',
        ),
        (
            "hack my neighbor's wifi",
            'weapon, harm, and surveillance requests',
        ),
    ],
)
def test_query_guardrails_block_off_topic_and_privacy_queries(query, expected_message_snippet):
    result = evaluate_query_guardrails(query)

    assert result.status == 'blocked', f'{query!r} was not blocked: {result}'
    assert expected_message_snippet in result.message
    assert result.missing_criteria == ['target people or organizations']
    assert result.suggestions[0].startswith('Try: IT directors')
