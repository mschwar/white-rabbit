from types import SimpleNamespace
import asyncio

from core.models import Lead, LeadList
from core.orchestrator import scout


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
