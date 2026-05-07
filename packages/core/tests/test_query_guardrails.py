from core.query_guardrails import evaluate_query_guardrails


def test_query_guardrails_allow_specific_lead_query():
    result = evaluate_query_guardrails('K-12 IT directors in Albuquerque')

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


def test_query_guardrails_block_broad_advice_queries():
    result = evaluate_query_guardrails('Give me supply-chain advice for hospitals')

    assert result.status == 'blocked'
    assert 'lead-generation queries' in result.message
    assert result.missing_criteria == ['target people or organizations']
    assert result.suggestions[0].startswith('Try: IT directors')
