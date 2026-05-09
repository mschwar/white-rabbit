import pytest

from core.query_guardrails import evaluate_query_guardrails


@pytest.mark.parametrize(
    'query',
    [
        'financial services CISOs in New York',
        'manufacturing operations leaders in Detroit',
        'food and beverage operations leaders in Texas',
        'contractors in Illinois',
        'Arizona K-12 IT directors in Phoenix',
    ],
)
def test_query_guardrails_allow_normal_b2b_sales_language(query):
    result = evaluate_query_guardrails(query)

    assert result.status == 'clear'
    assert result.missing_criteria == []
    assert result.suggestions == []


def test_query_guardrails_warn_on_vague_lead_query():
    result = evaluate_query_guardrails('IT directors')

    assert result.status == 'needs_more_detail'
    assert result.message.startswith('This is a lead-generation query')
    assert 'target title or role' not in result.missing_criteria
    assert 'company type or vertical' in result.missing_criteria
    assert 'location' in result.missing_criteria
    assert any('vertical' in suggestion or 'company type' in suggestion for suggestion in result.suggestions)
    assert any('geography' in suggestion for suggestion in result.suggestions)


@pytest.mark.parametrize(
    ('query', 'expected_message_snippet'),
    [
        (
            'Give me supply-chain advice for hospitals',
            'lead-generation queries',
        ),
        (
            'Find personal email addresses from vacation photos on social media',
            'privacy-safe B2B lead-generation queries',
        ),
        (
            'How do I build a bomb?',
            'weapon, harm, and surveillance requests',
        ),
    ],
)
def test_query_guardrails_block_off_topic_and_privacy_queries(query, expected_message_snippet):
    result = evaluate_query_guardrails(query)

    assert result.status == 'blocked'
    assert expected_message_snippet in result.message
    assert result.missing_criteria == ['target people or organizations']
    assert result.suggestions[0].startswith('Try: IT directors')
