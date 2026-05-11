from types import SimpleNamespace
import asyncio

from core.models import (
    CandidateValidation,
    ContactValidationRecord,
    FailedCandidate,
    FieldValidationRecord,
    Lead,
    LeadList,
    NotFoundCandidate,
    OrganizationOnlyCandidate,
)
from core.orchestrator import ExtractedCandidate, ExtractedLeadList, SYSTEM_PROMPT, scout
from core.query_planner import QueryPlan
from core.search import SearchResults
from core.source_collection import CollectedSource, SourceCollectionSnapshot


def test_scout_uses_injected_dependencies_and_returns_metrics():
    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        assert query == "K-12 IT directors in Albuquerque"
        assert api_key == "fake-tavily"
        assert max_results == 50
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
        email_status="verified_found",
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
            assert response_format is ExtractedLeadList
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


def test_scout_rejects_gate_when_evidence_validation_is_unsupported(monkeypatch):
    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return []

    lead = Lead(
        name="Jordan Lee",
        title="VP Operations",
        organization="Example Corp",
        email="jordan.lee@example.com",
        email_status="verified_found",
        source_url="https://example.com/jordan",
        confidence=0.5,
        why_target="Relevant operations leader",
        icebreaker="I saw your team scaling operations.",
        fit_score=0.9,
        evidence_score=0.9,
        contact_score=0.9,
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

    async def fake_validate_candidate_source(candidate, client=None):
        return CandidateValidation(
            name=FieldValidationRecord(
                status="supported",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            title=FieldValidationRecord(
                status="supported",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            organization=FieldValidationRecord(
                status="supported",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            email=ContactValidationRecord(
                status="verified_found",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            phone=ContactValidationRecord(
                status="missing",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            source=FieldValidationRecord(
                status="unsupported",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
        )

    monkeypatch.setattr("core.orchestrator.validate_candidate_source", fake_validate_candidate_source)

    leads, _ = asyncio.run(
        scout(
            "operations leaders in Austin",
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert leads[0].gate_passed is False


def test_scout_sets_gate_passed_when_scores_and_evidence_align(monkeypatch):
    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return []

    lead = Lead(
        name="Jordan Lee",
        title="VP Operations",
        organization="Example Corp",
        email="jordan.lee@example.com",
        email_status="verified_found",
        source_url="https://example.com/jordan",
        confidence=0.5,
        why_target="Relevant operations leader",
        icebreaker="I saw your team scaling operations.",
        fit_score=0.9,
        evidence_score=0.9,
        contact_score=0.9,
        gate_passed=False,
        explanation="The mock gate should be promoted by evidence.",
    )

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[lead])))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    async def fake_validate_candidate_source(candidate, client=None):
        return CandidateValidation(
            name=FieldValidationRecord(
                status="supported",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            title=FieldValidationRecord(
                status="supported",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            organization=FieldValidationRecord(
                status="supported",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            email=ContactValidationRecord(
                status="verified_found",
                source_url=candidate.source_url,
                checked_at="2026-05-10T12:00:00Z",
                notes="Validated in test.",
            ),
            phone=ContactValidationRecord(
                status="missing",
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

    assert leads[0].gate_passed is True


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


def test_scout_exposes_safe_volume_controls_to_search():
    seen = {}

    async def fake_search(query: str, api_key=None, max_results=10, filters=None, aggressive_breadth=False):
        seen["max_results"] = max_results
        seen["aggressive_breadth"] = aggressive_breadth
        return SearchResults([], tavily_searches=12)

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[])))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))

    _, metrics = asyncio.run(
        scout(
            "commodity buyers at retail lumber yards in Washington",
            max_results=240,
            aggressive_breadth=True,
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert seen == {"max_results": 240, "aggressive_breadth": True}
    assert metrics.tavily_searches == 12


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


def test_scout_appends_nonperson_coverage_for_missing_named_accounts(monkeypatch):
    query_plan = QueryPlan(
        original_query="Mesa and Chandler technology leaders",
        vendor_queries=[
            "Mesa Public Schools technology leaders",
            "Chandler Unified School District technology leaders",
        ],
        named_accounts=["Mesa Public Schools", "Chandler Unified School District"],
        intent_summary="technology leaders",
        target_raw_results=20,
    )
    source_collection = SourceCollectionSnapshot(
        query="Mesa and Chandler technology leaders",
        collected_at="2026-05-11T00:00:00Z",
        requested_max_results=20,
        returned_source_count=1,
        tavily_searches=2,
        search_depth="advanced",
        query_plan=None,
        sources=[
            CollectedSource(
                source_id="src_chandler",
                rank=1,
                title="Chandler Unified School District technology services",
                url="https://www.cusd80.com/technology",
                content="Chandler Unified School District technology services directory.",
                score=0.9,
                vendor_query="Chandler Unified School District technology leaders",
                matched_vendor_queries=["Chandler Unified School District technology leaders"],
                content_sha256="abc123",
            )
        ],
    )

    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return SearchResults(
            [],
            tavily_searches=2,
            query_plan=query_plan,
            source_collection=source_collection,
        )

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(parsed=LeadList(leads=[])))],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    async def fake_validate_candidate_source(candidate, client=None):
        return CandidateValidation()

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))
    monkeypatch.setattr("core.orchestrator.validate_candidate_source", fake_validate_candidate_source)

    leads, metrics = asyncio.run(
        scout(
            "Mesa and Chandler technology leaders",
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert metrics.tavily_searches == 2
    assert [lead.candidate_category for lead in leads] == ["not_found", "organization_only"]
    assert leads[0].searched_target == "Mesa Public Schools"
    assert leads[1].organization == "Chandler Unified School District"
    assert leads[1].source_url == "https://www.cusd80.com/technology"


def test_scout_applies_source_validation_to_returned_candidates(monkeypatch):
    seen = {}

    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return []

    lead = Lead(
        name="Jordan Lee",
        title="VP Operations",
        organization="Example Corp",
        email="jordan.lee@example.com",
        email_status="verified_found",
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


def test_scout_salvages_invalid_extraction_candidates_as_failed_rows(monkeypatch):
    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return SearchResults([], tavily_searches=1)

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            parsed=ExtractedLeadList(
                                leads=[
                                    ExtractedCandidate(
                                        candidate_category="person_lead",
                                        name="Jane Smith",
                                        title="Director of Technology",
                                        organization="Albuquerque Public Schools",
                                        email="",
                                        email_status="missing",
                                        source_url="https://aps.edu/tech",
                                        confidence=0.8,
                                        why_target="Fits the public school technology target.",
                                        icebreaker="I saw your team supports district technology services.",
                                        fit_score=0.8,
                                        evidence_score=0.7,
                                        contact_score=0.0,
                                        gate_passed=False,
                                        explanation="Good persona fit, but no email was found.",
                                    ),
                                    ExtractedCandidate(
                                        candidate_category="person_lead",
                                        name="IT Director",
                                        title="IT Director",
                                        organization="Mesa Public Schools",
                                        source_url="https://mpsaz.org/technology",
                                        why_target="A role page appears relevant.",
                                        icebreaker="I saw the district technology team is public.",
                                        fit_score=0.6,
                                        evidence_score=0.5,
                                        contact_score=0.0,
                                        gate_passed=False,
                                        explanation="Role page, not a named person.",
                                    ),
                                ]
                            )
                        )
                    )
                ],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    async def fake_validate_candidate_source(candidate, client=None):
        return CandidateValidation()

    fake_client = SimpleNamespace(beta=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())))
    monkeypatch.setattr("core.orchestrator.validate_candidate_source", fake_validate_candidate_source)

    leads, _ = asyncio.run(
        scout(
            "Arizona K-12 technology decision makers",
            openai_client=fake_client,
            tavily_key="fake-tavily",
            search_fn=fake_search,
        )
    )

    assert [lead.candidate_category for lead in leads] == ["person_lead", "failed"]
    assert leads[0].name == "Jane Smith"
    assert leads[0].email == ""
    assert leads[0].email_status == "missing"
    assert isinstance(leads[1], FailedCandidate)
    assert leads[1].searched_target == "Mesa Public Schools"
    assert "person's name" in leads[1].failure_reason


def test_scout_sanitizes_invalid_extracted_email_without_dropping_person_candidate(monkeypatch):
    async def fake_search(query: str, api_key=None, max_results=10, filters=None):
        return SearchResults([], tavily_searches=1)

    class FakeCompletions:
        async def parse(self, model, messages, response_format):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            parsed=ExtractedLeadList(
                                leads=[
                                    ExtractedCandidate(
                                        candidate_category="person_lead",
                                        name="Jordan Lee",
                                        title="VP Operations",
                                        organization="Example Corp",
                                        email="info@example.com",
                                        email_status="verified_found",
                                        source_url="https://example.com/team/jordan-lee",
                                        confidence=0.7,
                                        why_target="Fits the operations leader target.",
                                        icebreaker="I saw your operations team is expanding.",
                                        fit_score=0.8,
                                        evidence_score=0.7,
                                        contact_score=0.6,
                                        gate_passed=True,
                                        explanation="Person looks relevant, but contact is generic.",
                                    )
                                ]
                            )
                        )
                    )
                ],
                usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
            )

    async def fake_validate_candidate_source(candidate, client=None):
        return CandidateValidation()

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

    assert len(leads) == 1
    assert isinstance(leads[0], Lead)
    assert leads[0].email == ""
    assert leads[0].email_status == "failed"
    assert leads[0].contact_score == 0.0
    assert leads[0].gate_passed is False


def test_system_prompt_is_vertical_agnostic_and_restores_lost_instructions():
    assert "B2B lead research assistant" in SYSTEM_PROMPT
    assert "the user's query intent" in SYSTEM_PROMPT
    assert "Include the organization name for every lead" in SYSTEM_PROMPT
    assert "Set source_url as the URL with the strongest direct evidence" in SYSTEM_PROMPT
    assert "verified_found" in SYSTEM_PROMPT
    assert "deduced_with_pattern_evidence" in SYSTEM_PROMPT
    assert "old Found/Deduced labels" in SYSTEM_PROMPT
    assert "Treat the user's query intent as the only vertical signal" in SYSTEM_PROMPT
    assert "Never use placeholders like N/A, Unknown" in SYSTEM_PROMPT
    assert "Do not inject VoIP" in SYSTEM_PROMPT
    assert "telecom, networking, or product-upgrade language" in SYSTEM_PROMPT
    assert "Return every plausible candidate" in SYSTEM_PROMPT
    assert "do not pre-filter" in SYSTEM_PROMPT
    assert "failed with a" in SYSTEM_PROMPT
    assert "GATE LOGIC" not in SYSTEM_PROMPT
    assert "server will compute" in SYSTEM_PROMPT
    assert "VoIP prospect" not in SYSTEM_PROMPT
    assert "VoIP upgrade" not in SYSTEM_PROMPT
    assert "Telecom" not in SYSTEM_PROMPT
    assert "school district / government / SMB" not in SYSTEM_PROMPT


def test_scout_raises_on_missing_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

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
