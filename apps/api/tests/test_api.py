import os
from contextlib import contextmanager
from datetime import datetime
import asyncio
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import CheckConstraint

from core.cost import RunMetrics
from core.models import Lead, NotFoundCandidate, OrganizationOnlyCandidate

INTERNAL_API_TOKEN_HEADER = "x-white-rabbit-internal-token"
INTERNAL_API_TOKEN = "test-internal-token"

os.environ["WR_API_INTERNAL_TOKEN"] = INTERNAL_API_TOKEN

from api.main import app
from api.models import CorrectionField, CorrectionLabel, FeedbackLabel, LeadCorrection, LeadFeedback
from api.db import get_db_session, get_recipe_scoreboard, get_sandbox_state

client = TestClient(app)
client.headers.update({INTERNAL_API_TOKEN_HEADER: INTERNAL_API_TOKEN})
public_client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("post", "/scout", {"query": "K-12 IT directors in Albuquerque"}),
        ("post", "/full", {"query": "K-12 IT directors in Albuquerque"}),
        ("post", "/batch", {"name": "Test batch", "queries": [{"query": "K-12 IT directors in Albuquerque"}]}),
        ("post", "/sandbox/reset", {}),
        ("get", "/recipes", None),
        ("get", "/recipes/11111111-1111-1111-1111-111111111111/runs", None),
        ("get", "/recipes/11111111-1111-1111-1111-111111111111/scoreboard", None),
        ("get", "/sandbox", None),
        ("post", "/leads/11111111-1111-1111-1111-111111111111/feedback", {"label": "usable"}),
        (
            "post",
            "/leads/qa-usable-1/corrections",
            {
                "run_id": "qa-validation-buckets-run",
                "query": "K-12 IT directors in Albuquerque",
                "label": "wrong_persona",
                "field_name": "title",
            },
        ),
        ("get", "/runs/qa-validation-buckets-run/corrections", None),
        ("post", "/runs/11111111-1111-1111-1111-111111111111/close", {"operator_minutes": 10}),
        ("get", "/batch", None),
        ("get", "/batch/11111111-1111-1111-1111-111111111111", None),
    ],
)
def test_protected_api_endpoints_require_internal_token(method, path, payload):
    request_kwargs = {"json": payload} if payload is not None else {}
    response = getattr(public_client, method)(path, **request_kwargs)

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid internal API token."}


def test_scout_endpoint_returns_scoped_payload(monkeypatch):
    state = SimpleNamespace(
        total_queries=0,
        total_rows=0,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    @contextmanager
    def fake_db_session():
        yield object()

    async def fake_scout(query: str, **kwargs):
        assert query == "K-12 IT directors in Albuquerque"
        return (
            [
                Lead(
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
            ],
            RunMetrics(
                input_tokens=123,
                output_tokens=45,
                tavily_searches=1,
                openai_web_searches=0,
                elapsed_seconds=1.23,
                estimated_cost_usd=0.010123,
            ),
        )

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)
    monkeypatch.setattr("api.main.record_sandbox_rows", lambda session, rows: None)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/scout", json={"query": "K-12 IT directors in Albuquerque"})

    assert response.status_code == 200
    body = response.json()
    assert body["leads"][0]["name"] == "Jane Smith"
    assert body["leads"][0]["candidate_category"] == "person_lead"
    assert body["metrics"]["input_tokens"] == 123
    assert body["metrics"]["tavily_searches"] == 1


def test_scout_endpoint_preserves_candidate_categories(monkeypatch):
    state = SimpleNamespace(
        total_queries=0,
        total_rows=0,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    @contextmanager
    def fake_db_session():
        yield object()

    async def fake_scout(query: str, **kwargs):
        return (
            [
                Lead(
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
                ),
                OrganizationOnlyCandidate(
                    organization="Example Corp",
                    explanation="Account found, but no validated person lead.",
                ),
                NotFoundCandidate(
                    searched_target="Ghost District",
                    explanation="No acceptable contact was found for the target account.",
                ),
            ],
            RunMetrics(
                input_tokens=123,
                output_tokens=45,
                tavily_searches=1,
                openai_web_searches=0,
                elapsed_seconds=1.23,
                estimated_cost_usd=0.010123,
            ),
        )

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)
    monkeypatch.setattr("api.main.record_sandbox_rows", lambda session, rows: None)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/scout", json={"query": "K-12 IT directors in Albuquerque"})

    assert response.status_code == 200
    body = response.json()
    assert [lead["candidate_category"] for lead in body["leads"]] == [
        "person_lead",
        "organization_only",
        "not_found",
    ]
    assert body["leads"][1]["organization"] == "Example Corp"
    assert body["leads"][2]["searched_target"] == "Ghost District"


def test_scout_endpoint_forwards_filters(monkeypatch):
    captured = {}
    state = SimpleNamespace(
        total_queries=0,
        total_rows=0,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    @contextmanager
    def fake_db_session():
        yield object()

    async def fake_scout(query: str, **kwargs):
        captured["query"] = query
        captured["filters"] = kwargs.get("filters")
        return [], RunMetrics()

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)
    monkeypatch.setattr("api.main.record_sandbox_rows", lambda session, rows: None)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post(
        "/scout",
        json={"query": "K-12 IT directors in Albuquerque", "filters": {"location": "Albuquerque"}},
    )

    assert response.status_code == 200
    assert captured["query"] == "K-12 IT directors in Albuquerque"
    assert captured["filters"] == {"location": "Albuquerque"}


def test_scout_endpoint_blocks_broad_advice_queries(monkeypatch):
    called = {"scout": False}

    async def fake_scout(query: str, **kwargs):
        called["scout"] = True
        return [], RunMetrics()

    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/scout", json={"query": "supply chain advice for hospitals"})

    assert response.status_code == 422
    assert called["scout"] is False
    body = response.json()
    detail = body["detail"]
    assert detail["error"].startswith("White Rabbit only runs lead-generation queries")
    assert detail["query_guardrail"]["status"] == "blocked"
    assert detail["query_guardrail"]["missing_criteria"] == ["target people or organizations"]


def test_scout_endpoint_blocks_privacy_sensitive_queries(monkeypatch):
    called = {"scout": False}

    async def fake_scout(query: str, **kwargs):
        called["scout"] = True
        return [], RunMetrics()

    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post(
        "/scout",
        json={"query": "Find personal email addresses from vacation photos on social media"},
    )

    assert response.status_code == 422
    assert called["scout"] is False
    body = response.json()
    detail = body["detail"]
    assert detail["error"].startswith("White Rabbit only runs privacy-safe B2B lead-generation queries")
    assert detail["query_guardrail"]["status"] == "blocked"
    assert detail["query_guardrail"]["missing_criteria"] == ["target people or organizations"]


def test_feedback_endpoint_accepts_canonical_enum_labels(monkeypatch):
    captured = {}

    @contextmanager
    def fake_db_session():
        yield object()

    def fake_add_lead_feedback(session, lead_id, label):
        captured["lead_id"] = str(lead_id)
        captured["label"] = label

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.add_lead_feedback", fake_add_lead_feedback)

    response = client.post(
        "/leads/11111111-1111-1111-1111-111111111111/feedback",
        json={"label": "usable"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert captured["lead_id"] == "11111111-1111-1111-1111-111111111111"
    assert captured["label"] == FeedbackLabel.USABLE


def test_feedback_endpoint_rejects_noncanonical_labels(monkeypatch):
    called = {"add_lead_feedback": False}

    @contextmanager
    def fake_db_session():
        yield object()

    def fake_add_lead_feedback(session, lead_id, label):
        called["add_lead_feedback"] = True

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.add_lead_feedback", fake_add_lead_feedback)

    response = client.post(
        "/leads/11111111-1111-1111-1111-111111111111/feedback",
        json={"label": "Usable"},
    )

    assert response.status_code == 422
    assert called["add_lead_feedback"] is False
    body = response.json()
    assert body["detail"][0]["loc"] == ["body", "label"]


def test_feedback_endpoint_updates_existing_feedback(monkeypatch):
    existing_feedback = SimpleNamespace(lead_id=None, label=None)
    captured = {}

    class FakeQuery:
        def __init__(self, result):
            self._result = result

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return self._result

    class FakeSession:
        def __init__(self):
            self.added = []
            self.flushed = False

        def query(self, model):
            assert model is LeadFeedback
            return FakeQuery(existing_feedback)

        def add(self, obj):
            self.added.append(obj)

        def flush(self):
            self.flushed = True

    fake_session = FakeSession()

    @contextmanager
    def fake_db_session():
        yield fake_session

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)

    response = client.post(
        "/leads/11111111-1111-1111-1111-111111111111/feedback",
        json={"label": "wrong_persona"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert fake_session.added == []
    assert fake_session.flushed is True
    assert existing_feedback.label == FeedbackLabel.WRONG_PERSONA.value


def test_correction_endpoint_accepts_canonical_payload(monkeypatch):
    captured = {}

    @contextmanager
    def fake_db_session():
        yield object()

    def fake_add_lead_correction(session, lead_id, run_id, query, label, field_name, previous_value=None, corrected_value=None, notes=None):
        captured["lead_id"] = str(lead_id)
        captured["run_id"] = str(run_id)
        captured["query"] = query
        captured["label"] = label
        captured["field_name"] = field_name
        captured["previous_value"] = previous_value
        captured["corrected_value"] = corrected_value
        captured["notes"] = notes
        return SimpleNamespace(
            id="44444444-4444-4444-4444-444444444444",
            lead_id=lead_id,
            run_id=run_id,
            query=query,
            label=label.value,
            field_name=field_name.value,
            previous_value=previous_value,
            corrected_value=corrected_value,
            notes=notes,
            created_at=datetime(2026, 5, 10, 12, 0, 0),
        )

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.add_lead_correction", fake_add_lead_correction)

    response = client.post(
        "/leads/qa-usable-1/corrections",
        json={
            "run_id": "qa-validation-buckets-run",
            "query": "K-12 IT directors in Albuquerque",
            "label": "corrected_field",
            "field_name": "title",
            "previous_value": "Director of Technology",
            "corrected_value": "Director of IT",
            "notes": "Title was updated after a better source was found.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "corrected_field"
    assert body["field_name"] == "title"
    assert body["query"] == "K-12 IT directors in Albuquerque"
    assert captured["lead_id"] == "qa-usable-1"
    assert captured["run_id"] == "qa-validation-buckets-run"
    assert captured["label"] == CorrectionLabel.CORRECTED_FIELD
    assert captured["field_name"] == CorrectionField.TITLE
    assert captured["previous_value"] == "Director of Technology"
    assert captured["corrected_value"] == "Director of IT"
    assert captured["notes"] == "Title was updated after a better source was found."


def test_run_corrections_endpoint_returns_review_queue(monkeypatch):
    run_id = "qa-validation-buckets-run"

    @contextmanager
    def fake_db_session():
        yield object()

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr(
        "api.main.get_corrections_for_run",
        lambda session, _run_id: [
            SimpleNamespace(
                id="44444444-4444-4444-4444-444444444444",
                lead_id="qa-usable-1",
                run_id=_run_id,
                query="K-12 IT directors in Albuquerque",
                label=CorrectionLabel.WRONG_PERSONA.value,
                field_name=CorrectionField.TITLE.value,
                previous_value="Director of Technology",
                corrected_value="Director of IT",
                notes="Corrected title after source review.",
                created_at=datetime(2026, 5, 10, 12, 0, 0),
            )
        ],
    )

    response = client.get(f"/runs/{run_id}/corrections")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["run_id"] == run_id
    assert body[0]["label"] == "wrong_persona"
    assert body[0]["field_name"] == "title"
    assert body[0]["notes"] == "Corrected title after source review."


def test_lead_feedback_model_has_label_check_constraint():
    constraints = [constraint for constraint in LeadFeedback.__table__.constraints if isinstance(constraint, CheckConstraint)]

    assert any(constraint.name == "ck_lead_feedback_label" for constraint in constraints)
    assert any(
        "usable" in str(constraint.sqltext)
        and "wrong_persona" in str(constraint.sqltext)
        and "bad_source" in str(constraint.sqltext)
        and "bad_contact" in str(constraint.sqltext)
        and "duplicate" in str(constraint.sqltext)
        for constraint in constraints
    )


def test_lead_correction_model_has_constraints():
    constraints = [constraint for constraint in LeadCorrection.__table__.constraints if isinstance(constraint, CheckConstraint)]

    assert any(constraint.name == "ck_lead_correction_label" for constraint in constraints)
    assert any(constraint.name == "ck_lead_correction_field_name" for constraint in constraints)
    assert any(
        "corrected_field" in str(constraint.sqltext)
        and "wrong_persona" in str(constraint.sqltext)
        and "bad_source" in str(constraint.sqltext)
        and "bad_contact" in str(constraint.sqltext)
        and "duplicate" in str(constraint.sqltext)
        for constraint in constraints
    )
    assert any(
        "name" in str(constraint.sqltext)
        and "title" in str(constraint.sqltext)
        and "organization" in str(constraint.sqltext)
        and "email" in str(constraint.sqltext)
        and "phone" in str(constraint.sqltext)
        and "source" in str(constraint.sqltext)
        for constraint in constraints
    )


def test_get_recipe_scoreboard_seeds_canonical_feedback_counts(monkeypatch):
    recipe_id = "11111111-1111-1111-1111-111111111111"
    run_id = "22222222-2222-2222-2222-222222222222"
    lead_id = "33333333-3333-3333-3333-333333333333"

    class FakeQuery:
        def __init__(self, result):
            self._result = result

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return self._result

    class FakeSession:
        def query(self, model):
            if model is LeadFeedback:
                return FakeQuery(SimpleNamespace(label=FeedbackLabel.USABLE.value))
            raise AssertionError(f"Unexpected model queried: {model}")

    monkeypatch.setattr(
        "api.db.get_recipe_by_id",
        lambda session, _recipe_id: SimpleNamespace(id=_recipe_id, name="K-12 IT directors"),
    )
    monkeypatch.setattr(
        "api.db.get_recipe_runs",
        lambda session, recipe_id=None: [
            SimpleNamespace(
                id=run_id,
                lead_count=3,
                operator_minutes=18.5,
                api_cost_breakdown={"estimated_cost_usd": 0.42},
            )
        ],
    )
    monkeypatch.setattr(
        "api.db.get_leads_for_run",
        lambda session, _run_id: [SimpleNamespace(id=lead_id)],
    )

    scoreboard = get_recipe_scoreboard(FakeSession(), recipe_id)

    assert scoreboard["feedback_counts"] == {
        "usable": 1,
        "wrong_persona": 0,
        "bad_source": 0,
        "bad_contact": 0,
        "duplicate": 0,
    }
    assert scoreboard["usable_lead_count"] == 1
    assert scoreboard["minutes_per_usable_lead"] == 18.5
    assert scoreboard["api_cost_per_usable_lead"] == 0.42


def test_scout_endpoint_forwards_filters(monkeypatch):
    captured = {}
    state = SimpleNamespace(
        total_queries=0,
        total_rows=0,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    @contextmanager
    def fake_db_session():
        yield object()

    async def fake_scout(query: str, **kwargs):
        captured["query"] = query
        captured["filters"] = kwargs.get("filters")
        return [], RunMetrics()

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)
    monkeypatch.setattr("api.main.record_sandbox_rows", lambda session, rows: None)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post(
        "/scout",
        json={"query": "K-12 IT directors in Albuquerque", "filters": {"location": "Albuquerque"}},
    )

    assert response.status_code == 200
    assert captured["query"] == "K-12 IT directors in Albuquerque"
    assert captured["filters"] == {"location": "Albuquerque"}

def test_sandbox_usage_endpoint_returns_usage(monkeypatch):
    state = SimpleNamespace(
        total_queries=2,
        total_rows=18,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    @contextmanager
    def fake_db_session():
        yield object()

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)

    response = client.get("/sandbox")

    assert response.status_code == 200
    assert response.json() == {
        "total_queries": 2,
        "total_rows": 18,
        "max_queries": 10,
        "max_rows": 1000,
        "remaining_queries": 8,
        "remaining_rows": 982,
        "reset_at": "2026-01-01T12:00:00",
    }


def test_sandbox_atomic_cap_is_enforced_under_concurrency(monkeypatch):
    with get_db_session() as session:
        state = get_sandbox_state(session)
        original = {
            "total_queries": state.total_queries,
            "total_rows": state.total_rows,
            "max_queries": state.max_queries,
            "max_rows": state.max_rows,
            "reset_at": state.reset_at,
        }
        state.total_queries = 0
        state.total_rows = 0
        state.max_queries = 10
        state.max_rows = 1000

    async def fake_scout(query: str, **kwargs):
        await asyncio.sleep(0.05)
        return [
            Lead(
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
        ], RunMetrics(
            input_tokens=1,
            output_tokens=1,
            tavily_searches=0,
            openai_web_searches=0,
            elapsed_seconds=0.05,
            estimated_cost_usd=0.0,
        )

    monkeypatch.setattr("api.main.scout", fake_scout)

    async def run_requests():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            responses = await asyncio.gather(
                *[
                    ac.post(
                        "/scout",
                        json={"query": "K-12 IT directors in Albuquerque"},
                        headers={INTERNAL_API_TOKEN_HEADER: INTERNAL_API_TOKEN},
                    )
                    for _ in range(12)
                ]
            )
        return responses

    try:
        responses = asyncio.run(run_requests())
        statuses = [response.status_code for response in responses]
        assert statuses.count(200) == 10
        assert statuses.count(429) == 2
    finally:
        with get_db_session() as session:
            state = get_sandbox_state(session)
            state.total_queries = original["total_queries"]
            state.total_rows = original["total_rows"]
            state.max_queries = original["max_queries"]
            state.max_rows = original["max_rows"]
            state.reset_at = original["reset_at"]


def test_sandbox_reset_endpoint_clears_usage(monkeypatch):
    state = SimpleNamespace(
        total_queries=5,
        total_rows=42,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    @contextmanager
    def fake_db_session():
        yield object()

    def fake_reset_sandbox_state(session):
        state.total_queries = 0
        state.total_rows = 0
        state.reset_at = datetime(2026, 1, 2, 9, 30, 0)
        return state

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)
    monkeypatch.setattr("api.main.reset_sandbox_state", fake_reset_sandbox_state)

    response = client.post("/sandbox/reset")

    assert response.status_code == 200
    assert response.json() == {
        "sandbox_usage": {
            "total_queries": 0,
            "total_rows": 0,
            "max_queries": 10,
            "max_rows": 1000,
            "remaining_queries": 10,
            "remaining_rows": 1000,
            "reset_at": "2026-01-02T09:30:00",
        }
    }


def test_scout_endpoint_returns_sandbox_usage_and_enforces_caps(monkeypatch):
    state = SimpleNamespace(
        total_queries=10,
        total_rows=100,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )
    called = {"scout": False}

    @contextmanager
    def fake_db_session():
        yield object()

    async def fake_scout(query: str, **kwargs):
        called["scout"] = True
        return [], RunMetrics()

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/scout", json={"query": "K-12 IT directors in Albuquerque"})

    assert response.status_code == 429
    assert called["scout"] is False
    detail = response.json()["detail"]
    assert detail["error"] == "Sandbox query cap reached. Reset the sandbox before running more queries."
    assert detail["sandbox_usage"]["total_queries"] == 10
    assert detail["sandbox_usage"]["remaining_queries"] == 0


def test_scout_endpoint_returns_structured_error_on_orchestrator_failure(monkeypatch):
    state = SimpleNamespace(
        total_queries=0,
        total_rows=0,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    @contextmanager
    def fake_db_session():
        yield object()

    async def fake_scout(query: str, **kwargs):
        from core.orchestrator import OrchestratorError
        raise OrchestratorError("Tavily search failed: timeout")

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)
    monkeypatch.setattr("api.main.record_sandbox_rows", lambda session, rows: None)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/scout", json={"query": "Healthcare IT directors in Phoenix"})

    assert response.status_code == 503
    body = response.json()
    detail = body["detail"]
    assert detail["error_code"] == "tavily_failed"
    assert "Tavily search failed" in detail["message"]
    assert detail["request_id"] is not None


def test_scout_endpoint_returns_structured_error_on_openai_failure(monkeypatch):
    state = SimpleNamespace(
        total_queries=0,
        total_rows=0,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    @contextmanager
    def fake_db_session():
        yield object()

    async def fake_scout(query: str, **kwargs):
        from core.orchestrator import OrchestratorError
        raise OrchestratorError("OpenAI API error: rate limited")

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)
    monkeypatch.setattr("api.main.record_sandbox_rows", lambda session, rows: None)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/scout", json={"query": "Healthcare IT directors in Phoenix"})

    assert response.status_code == 503
    body = response.json()
    detail = body["detail"]
    assert detail["error_code"] == "openai_failed"
    assert "OpenAI API error" in detail["message"]
    assert detail["request_id"] is not None


def test_scout_endpoint_returns_structured_error_on_unexpected_exception(monkeypatch):
    state = SimpleNamespace(
        total_queries=0,
        total_rows=0,
        max_queries=10,
        max_rows=1000,
        reset_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    @contextmanager
    def fake_db_session():
        yield object()

    async def fake_scout(query: str, **kwargs):
        raise RuntimeError("Something exploded")

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: state)
    monkeypatch.setattr("api.main.record_sandbox_rows", lambda session, rows: None)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/scout", json={"query": "Healthcare IT directors in Phoenix"})

    assert response.status_code == 500
    body = response.json()
    detail = body["detail"]
    assert detail["error_code"] == "internal_error"
    assert detail["message"] == "An unexpected error occurred."
    assert detail["request_id"] is not None


def test_recipe_scoreboard_endpoint_returns_aggregates(monkeypatch):
    captured = {}

    @contextmanager
    def fake_db_session():
        yield object()

    def fake_get_recipe_scoreboard(session, recipe_id):
        captured["recipe_id"] = str(recipe_id)
        return {
            "recipe_id": recipe_id,
            "recipe_name": "K-12 IT directors",
            "total_api_cost_usd": 0.42,
            "total_leads_returned": 3,
            "usable_lead_count": 2,
            "total_operator_minutes": 18.5,
            "minutes_per_usable_lead": 9.25,
            "api_cost_per_usable_lead": 0.21,
            "feedback_counts": {
                "usable": 2,
                "wrong_persona": 0,
                "bad_source": 0,
                "bad_contact": 0,
                "duplicate": 0,
            },
        }

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.get_recipe_scoreboard", fake_get_recipe_scoreboard)

    response = client.get("/recipes/11111111-1111-1111-1111-111111111111/scoreboard")

    assert response.status_code == 200
    body = response.json()
    assert body["recipe_name"] == "K-12 IT directors"
    assert body["usable_lead_count"] == 2
    assert captured["recipe_id"] == "11111111-1111-1111-1111-111111111111"


def test_batch_endpoint_creates_job_and_runs(monkeypatch):
    from uuid import UUID

    captured = {}

    @contextmanager
    def fake_db_session():
        class FakeSession:
            def flush(self):
                pass
            def commit(self):
                pass
            def rollback(self):
                pass
            def close(self):
                pass
        yield FakeSession()

    class FakeJob:
        id = UUID("22222222-2222-2222-2222-222222222222")
        name = "Test batch"
        status = "completed"
        cap_queries = 10
        cap_max_leads = 1000
        cap_max_spend_usd = 10.0
        created_at = __import__("datetime").datetime.utcnow()
        started_at = __import__("datetime").datetime.utcnow()
        ended_at = __import__("datetime").datetime.utcnow()
        total_cost_usd = 0.02
        total_leads = 2

    class FakeRun:
        id = UUID("33333333-3333-3333-3333-333333333333")
        query = "K-12 IT directors in Albuquerque"
        status = "completed"
        lead_count = 2
        cost_usd = 0.02
        error_message = None
        recipe_id = UUID("44444444-4444-4444-4444-444444444444")
        started_at = __import__("datetime").datetime.utcnow()
        ended_at = __import__("datetime").datetime.utcnow()

    def fake_create_batch_job(session, name, cap_queries, cap_max_leads, cap_max_spend_usd):
        captured["job_name"] = name
        return FakeJob()

    def fake_create_batch_run(session, batch_job_id, query):
        captured.setdefault("queries", []).append(query)
        return FakeRun()

    def fake_update_batch_run(session, run_id, **kwargs):
        return FakeRun()

    def fake_close_batch_job(session, job_id, status, total_cost_usd, total_leads):
        captured["closed"] = True
        return FakeJob()

    def fake_get_batch_runs(session, job_id):
        return [FakeRun()]

    async def fake_scout(query, **kwargs):
        return (
            [
                Lead(
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
                ),
                Lead(
                    name="John Doe",
                    title="IT Manager",
                    organization="Santa Fe Public Schools",
                    email="john.doe@sfps.edu",
                    email_status="Found",
                    source_url="https://sfps.edu/tech",
                    confidence=0.82,
                    why_target="Manages district network infrastructure",
                    icebreaker="I noticed SFPS is expanding its digital learning initiative.",
                    fit_score=0.85,
                    evidence_score=0.80,
                    contact_score=0.75,
                    gate_passed=True,
                    explanation="Good fit with relevant experience.",
                ),
            ],
            RunMetrics(
                input_tokens=123,
                output_tokens=45,
                tavily_searches=1,
                elapsed_seconds=1.23,
                estimated_cost_usd=0.02,
            ),
        )

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.create_batch_job", fake_create_batch_job)
    monkeypatch.setattr("api.main.create_batch_run", fake_create_batch_run)
    monkeypatch.setattr("api.main.update_batch_run", fake_update_batch_run)
    monkeypatch.setattr("api.main.close_batch_job", fake_close_batch_job)
    monkeypatch.setattr("api.main.get_batch_runs", fake_get_batch_runs)
    monkeypatch.setattr("api.main.scout", fake_scout)

    # Also mock recipe creation and sandbox to avoid DB dependency
    class FakeRecipe:
        id = UUID("44444444-4444-4444-4444-444444444444")

    class FakeRecipeRun:
        id = UUID("55555555-5555-5555-5555-555555555555")

    class FakeSandboxState:
        total_queries = 0
        total_rows = 0
        max_queries = 10
        max_rows = 1000
        reset_at = datetime(2026, 1, 1, 12, 0, 0)

    monkeypatch.setattr("api.main.create_recipe", lambda session, **kwargs: FakeRecipe())
    monkeypatch.setattr("api.main.create_recipe_run", lambda session, **kwargs: FakeRecipeRun())
    monkeypatch.setattr("api.main.save_leads", lambda session, run_id, leads: None)
    monkeypatch.setattr("api.main.get_sandbox_state", lambda session: FakeSandboxState())
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", lambda session: FakeSandboxState())
    monkeypatch.setattr("api.main.record_sandbox_rows", lambda session, rows: None)

    response = client.post(
        "/batch",
        json={
            "name": "Test batch",
            "queries": [
                {"query": "K-12 IT directors in Albuquerque"},
                {"query": "City IT managers in Santa Fe", "filters": {"location": "New Mexico"}},
            ],
            "cap_queries": 5,
            "cap_max_leads": 100,
            "cap_max_spend_usd": 5.0,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Test batch"
    assert body["status"] in ("completed", "completed_with_errors")
    assert body["total_leads"] == 4
    assert len(body["runs"]) == 2
    assert captured["job_name"] == "Test batch"
    assert captured["queries"] == ["K-12 IT directors in Albuquerque", "City IT managers in Santa Fe"]
    assert captured.get("closed") is True


def test_batch_endpoint_respects_caps(monkeypatch):
    from uuid import UUID

    captured = {}

    @contextmanager
    def fake_db_session():
        class FakeSession:
            def flush(self):
                pass
            def commit(self):
                pass
            def rollback(self):
                pass
            def close(self):
                pass
        yield FakeSession()

    class FakeJob:
        id = UUID("22222222-2222-2222-2222-222222222222")
        name = "Cap test"
        status = "completed_with_errors"
        cap_queries = 10
        cap_max_leads = 1
        cap_max_spend_usd = 10.0
        created_at = __import__("datetime").datetime.utcnow()
        started_at = __import__("datetime").datetime.utcnow()
        ended_at = __import__("datetime").datetime.utcnow()
        total_cost_usd = 0.0
        total_leads = 0

    class FakeRun:
        id = UUID("33333333-3333-3333-3333-333333333333")
        query = "Query 1"
        status = "failed"
        lead_count = 0
        cost_usd = 0.0
        error_message = "Spend cap exceeded"
        recipe_id = None
        started_at = __import__("datetime").datetime.utcnow()
        ended_at = __import__("datetime").datetime.utcnow()

    def fake_create_batch_job(session, name, cap_queries, cap_max_leads, cap_max_spend_usd):
        captured["job_caps"] = {
            "cap_queries": cap_queries,
            "cap_max_leads": cap_max_leads,
            "cap_max_spend_usd": cap_max_spend_usd,
        }

        job = type("Job", (FakeJob,), {})()
        job.cap_queries = cap_queries
        job.cap_max_leads = cap_max_leads
        job.cap_max_spend_usd = cap_max_spend_usd
        return job

    def fake_create_batch_run(session, batch_job_id, query):
        return FakeRun()

    def fake_update_batch_run(session, run_id, **kwargs):
        return FakeRun()

    def fake_close_batch_job(session, job_id, status, total_cost_usd, total_leads):
        captured["closed_status"] = status
        return FakeJob()

    def fake_get_batch_runs(session, job_id):
        return [FakeRun()]

    async def fake_scout(query, **kwargs):
        return (
            [
                Lead(
                    name="Jane Smith",
                    title="Director",
                    organization="Test Org",
                    email="jane@test.org",
                    email_status="Found",
                    source_url="https://test.org",
                    confidence=0.9,
                    why_target="Test",
                    icebreaker="Test",
                    fit_score=0.9,
                    evidence_score=0.9,
                    contact_score=0.9,
                    gate_passed=True,
                    explanation="Test",
                ),
            ],
            RunMetrics(
                input_tokens=10,
                output_tokens=5,
                tavily_searches=1,
                elapsed_seconds=0.5,
                estimated_cost_usd=0.05,
            ),
        )

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.create_batch_job", fake_create_batch_job)
    monkeypatch.setattr("api.main.create_batch_run", fake_create_batch_run)
    monkeypatch.setattr("api.main.update_batch_run", fake_update_batch_run)
    monkeypatch.setattr("api.main.close_batch_job", fake_close_batch_job)
    monkeypatch.setattr("api.main.get_batch_runs", fake_get_batch_runs)
    monkeypatch.setattr("api.main.scout", fake_scout)
    monkeypatch.setattr("api.main.create_recipe", lambda session, **kwargs: type("FakeRecipe", (), {"id": UUID("44444444-4444-4444-4444-444444444444")})())
    monkeypatch.setattr("api.main.create_recipe_run", lambda session, **kwargs: type("FakeRecipeRun", (), {"id": UUID("55555555-5555-5555-5555-555555555555")})())
    monkeypatch.setattr("api.main.save_leads", lambda session, run_id, leads: [type("FakeLead", (), {"id": UUID("66666666-6666-6666-6666-666666666666")})()])

    response = client.post(
        "/batch",
        json={
            "name": "Cap test",
            "queries": [{"query": "Query 1"}],
            "cap_max_spend_usd": 0.01,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed_with_errors"
    assert any(r["status"] == "failed" for r in body["runs"])
    assert body["total_leads"] == 0
    assert body["total_cost_usd"] == 0.0


def test_full_endpoint_returns_persisted_lead_ids(monkeypatch):
    from uuid import UUID

    captured = {}

    @contextmanager
    def fake_db_session():
        class FakeSession:
            def flush(self):
                pass
            def commit(self):
                pass
            def rollback(self):
                pass
            def close(self):
                pass
        yield FakeSession()

    class FakeRecipe:
        id = UUID("11111111-1111-1111-1111-111111111111")

    class FakeRun:
        id = UUID("22222222-2222-2222-2222-222222222222")

    class FakeLead:
        id = UUID("33333333-3333-3333-3333-333333333333")

    def fake_create_recipe(session, **kwargs):
        return FakeRecipe()

    def fake_create_recipe_run(session, **kwargs):
        return FakeRun()

    def fake_save_leads(session, run_id, leads):
        captured["saved_leads"] = leads
        return [FakeLead()]

    def fake_get_sandbox_state(session):
        return SimpleNamespace(
            total_queries=0,
            total_rows=0,
            max_queries=10,
            max_rows=1000,
            reset_at=datetime.utcnow(),
        )

    def fake_record_sandbox_rows(session, rows):
        pass

    async def fake_scout(query, **kwargs):
        return (
            [
                Lead(
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
                ),
            ],
            RunMetrics(
                input_tokens=123,
                output_tokens=45,
                tavily_searches=1,
                elapsed_seconds=1.23,
                estimated_cost_usd=0.010123,
            ),
        )

    monkeypatch.setattr("api.main.get_db_session", fake_db_session)
    monkeypatch.setattr("api.main.create_recipe", fake_create_recipe)
    monkeypatch.setattr("api.main.create_recipe_run", fake_create_recipe_run)
    monkeypatch.setattr("api.main.save_leads", fake_save_leads)
    monkeypatch.setattr("api.main.get_sandbox_state", fake_get_sandbox_state)
    monkeypatch.setattr("api.main.get_sandbox_state_for_update", fake_get_sandbox_state)
    monkeypatch.setattr("api.main.record_sandbox_rows", fake_record_sandbox_rows)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/full", json={"query": "K-12 IT directors in Albuquerque"})

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "22222222-2222-2222-2222-222222222222"
    assert body["recipe_id"] == "11111111-1111-1111-1111-111111111111"
    assert len(body["leads"]) == 1
    assert body["leads"][0]["id"] == "33333333-3333-3333-3333-333333333333"
    assert body["leads"][0]["validation"]["name"]["status"] == "unsupported"
    assert body["leads"][0]["validation"]["source"]["checked_at"] is None


def test_sandbox_endpoint_after_migration():
    """Verify /sandbox works on a real DB after alembic migration (no mocks)."""
    response = client.get("/sandbox")
    assert response.status_code == 200
    data = response.json()
    # Must contain expected keys (no relation-does-not-exist error)
    assert "total_queries" in data
    assert "total_rows" in data
    assert "max_queries" in data
    assert "max_rows" in data
    assert "remaining_queries" in data
    assert "remaining_rows" in data
