from types import SimpleNamespace
import asyncio

from core.models import CandidateValidation, FieldValidationRecord, Lead, LeadList, NotFoundCandidate, OrganizationOnlyCandidate
from core.orchestrator import SYSTEM_PROMPT, scout
from core.search import SearchResults


def test_scout_uses_injected_dependencies_and_returns_metrics():
    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        assert query == "K-12 IT directors in Albuquerque"
        assert api_key == "fake-tavily"
        assert max_results == 10
        assert filters is None
        return [
            {
                "title": "Albuquerque Public Schools technology leadership",
                "url": "https://aps.edu/tech",
                "content": "APS lists its technology leadership contacts.",
                "score": 0.93,
            }
        ]

    lead = Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Albuquerque Public Schools",
        email="jane.smith@aps.edu",
        email_status="Found",
        source_url="https://aps.edu/tech",
        confidence=0.88,
        why_target="Owns district telecom decisions",
        icebreaker="I noticed APS is growing its classroom connectivity needs.",
        fit_score=0.91,
        evidence_score=0.84,
        contact_score=0.79,
        gate_passed=True,
        explanation="Strong district fit with current leadership evidence and usable email.",
    )

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            assert model == "gpt-4o-mini"
            assert response_format is LeadList
            assert messages[0]["role"] == "system"
            assert "B2B lead research assistant" in messages[0]["content"]
            assert "K-12 IT directors in Albuquerque" in messages[1]["content"]
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[lead])))],
                usage=SimpleNamespace(prompt_tokens=123, completion_tokens=45),
            )

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))

    leads, metrics = asyncio.run(
        scout(
            "K-12 IT directors in Albuquerque",
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert len(leads) == 1
    assert leads[0].name == "Jane Smith"
    assert metrics.input_tokens == 123
    assert metrics.output_tokens == 45
    assert metrics.tavily_searches == 1
    assert metrics.elapsed_seconds >= 0
    assert metrics.estimated_cost_usd > 0


def test_scout_overrides_llm_gate_passed_from_subscores():
    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return []

    lead = Lead(
        name="Jordan Lee",
        title="VP Operations",
        organization="Example Corp",
        email="jordan.lee@example.com",
        email_status="Found",
        source_url="https://example.com/jordan",
        confidence=0.5,
        why_target="Relevant operations leader",
        icebreaker="I saw your team scaling operations.",
        fit_score=0.2,
        evidence_score=0.1,
        contact_score=0.3,
        gate_passed=True,
        explanation="The mock sets gate_passed incorrectly.",
    )

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[lead])))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))

    leads, _ = asyncio.run(
        scout(
            "operations leaders in Austin",
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert leads[0].gate_passed is False


def test_scout_constructs_async_openai_with_max_retries(monkeypatch):
    created = {}

    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return []

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[])))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    class FakeAsyncOpenAI:
        def __init__(self, api_key=None, max_retries=None):
            created["api_key"] = api_key
            created["max_retries"] = max_retries
            self.beta = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

    monkeypatch.setattr("core.orchestrator.AsyncOpenAI", FakeAsyncOpenAI)

    leads, _ = asyncio.run(
        scout(
            "operations leaders in Austin",
            openai_key="fake-openai",
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert leads == []
    assert created["api_key"] == "fake-openai"
    assert created["max_retries"] == 2


def test_scout_threads_filters_through_search_and_prompt():
    seen = {}

    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        seen["search_query"] = query
        seen["search_api_key"] = api_key
        seen["search_max_results"] = max_results
        seen["search_filters"] = filters
        return []

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            seen["prompt"] = messages[1]["content"]
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[])))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))

    leads, metrics = asyncio.run(
        scout(
            "K-12 IT directors",
            filters={"location": "Albuquerque", "segment": "public schools"},
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert leads == []
    assert seen["search_query"] == "K-12 IT directors"
    assert seen["search_filters"] == {"location": "Albuquerque", "segment": "public schools"}
    assert "location: Albuquerque" in seen["prompt"]
    assert "segment: public schools" in seen["prompt"]
    assert metrics.tavily_searches == 1


def test_scout_counts_planned_tavily_searches_from_search_results():
    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return SearchResults([], tavily_searches=8)

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[])))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))

    _, metrics = asyncio.run(
        scout(
            "Arizona K-12 VoIP decision makers at Mesa, Chandler, Peoria, Gilbert, Deer Valley, Paradise Valley, Dysart, and Maricopa",
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert metrics.tavily_searches == 8


def test_scout_preserves_non_person_candidate_categories():
    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return SearchResults([], tavily_searches=1)

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            parsed=LeadList(
                                leads=[
                                    OrganizationOnlyCandidate(
                                        organization="Example Corp",
                                        explanation="The company was found, but no person was validated.",
                                    ),
                                    NotFoundCandidate(
                                        searched_target="Ghost Company",
                                        explanation="No acceptable contact was found for the target account.",
                                    ),
                                ]
                            )
                        )
                    )
                ],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))

    leads, _ = asyncio.run(
        scout(
            "operations leaders in Austin",
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert [lead.candidate_category for lead in leads] == ["organization_only", "not_found"]


def test_scout_applies_source_validation_to_returned_candidates(monkeypatch):
    seen = {}

    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return []

    lead = Lead(
        name="Jordan Lee",
        title="VP Operations",
        organization="Example Corp",
        email="jordan.lee@example.com",
        email_status="Found",
        source_url="https://example.com/jordan",
        confidence=0.5,
        why_target="Relevant operations leader",
        icebreaker="I saw your team scaling operations.",
        fit_score=0.8,
        evidence_score=0.7,
        contact_score=0.6,
        gate_passed=True,
        explanation="The mock lead should be validated by source checks.",
    )

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[lead])))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    async def fake_validate_candidate_source(candidate, client=None):
        seen["candidate_name"] = candidate.name
        seen["client_type"] = type(client).__name__ if client is not None else None
        return CandidateValidation(
            name=FieldValidationRecord(
                status="supported",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            source=FieldValidationRecord(
                status="supported",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
        )

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))

    monkeypatch.setattr("core.orchestrator.validate_candidate_source", fake_validate_candidate_source)

    leads, _ = asyncio.run(
        scout(
            "operations leaders in Austin",
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert seen["candidate_name"] == "Jordan Lee"
    assert seen["client_type"] == "AsyncClient"
    assert leads[0].validation.source.status == "supported"
    assert leads[0].validation.name.status == "supported"


def test_system_prompt_is_vertical_agnostic_and_restores_lost_instructions():
    assert "B2B lead research assistant" in SYSTEM_PROMPT
    assert "the user's query intent" in SYSTEM_PROMPT
    assert "Include the organization name for every lead" in SYSTEM_PROMPT
    assert "Set source_url as the URL with the strongest direct evidence" in SYSTEM_PROMPT
    assert "Never invent or guess an email." in SYSTEM_PROMPT
    assert "Treat the user's query intent as the only vertical signal" in SYSTEM_PROMPT
    assert "Never use placeholders like N/A, Unknown" in SYSTEM_PROMPT
    assert "Do not inject VoIP" in SYSTEM_PROMPT
    assert "telecom, networking, or product-upgrade language" in SYSTEM_PROMPT
    assert "GATE LOGIC" not in SYSTEM_PROMPT
    assert "server will compute" in SYSTEM_PROMPT
    assert "VoIP prospect" not in SYSTEM_PROMPT
    assert "VoIP upgrade" not in SYSTEM_PROMPT
    assert "Telecom" not in SYSTEM_PROMPT
    assert "school district / government / SMB" not in SYSTEM_PROMPT


def test_scout_raises_on_missing_openai_key():
    async def fake_search(*args, **kwargs):
        return []

    try:
        asyncio.run(
            scout(
                "test query",
                openai_key=None,
                tavily_key="fake-tavily",
                search_fn=fake_search,
            )
        )
        assert False, "Expected OrchestratorError"
    except Exception as exc:
        assert "OPENAI_API_KEY not found" in str(exc)


def test_scout_raises_on_tavily_failure():
    class FakeSearchError(Exception):
        pass

    async def fake_search(*args, **kwargs):
        raise FakeSearchError("Tavily API down")

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[])))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))

    try:
        asyncio.run(
            scout(
                "test query",
                openai_client=fake_client,
                tavily_key="fake-tavily",
                search_fn=fake_search,
            )
        )
        assert False, "Expected OrchestratorError"
    except Exception as exc:
        assert "Tavily search failed" in str(exc)
