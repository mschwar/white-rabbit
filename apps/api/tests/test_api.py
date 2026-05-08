from contextlib import contextmanager
from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from core.cost import RunMetrics
from core.models import Lead
from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_scout_endpoint_returns_scoped_payload(monkeypatch):
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

    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/scout", json={"query": "K-12 IT directors in Albuquerque"})

    assert response.status_code == 200
    body = response.json()
    assert body["leads"][0]["name"] == "Jane Smith"
    assert body["metrics"]["input_tokens"] == 123
    assert body["metrics"]["tavily_searches"] == 1


def test_scout_endpoint_forwards_filters(monkeypatch):
    captured = {}

    async def fake_scout(query: str, **kwargs):
        captured["query"] = query
        captured["filters"] = kwargs.get("filters")
        return [], RunMetrics()

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


def test_scout_endpoint_forwards_filters(monkeypatch):
    captured = {}

    async def fake_scout(query: str, **kwargs):
        captured["query"] = query
        captured["filters"] = kwargs.get("filters")
        return [], RunMetrics()

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
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/scout", json={"query": "K-12 IT directors in Albuquerque"})

    assert response.status_code == 429
    assert called["scout"] is False
    detail = response.json()["detail"]
    assert detail["error"] == "Sandbox query cap reached. Reset the sandbox before running more queries."
    assert detail["sandbox_usage"]["total_queries"] == 10
    assert detail["sandbox_usage"]["remaining_queries"] == 0


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
    monkeypatch.setattr("api.main.record_sandbox_rows", fake_record_sandbox_rows)
    monkeypatch.setattr("api.main.scout", fake_scout)

    response = client.post("/full", json={"query": "K-12 IT directors in Albuquerque"})

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "22222222-2222-2222-2222-222222222222"
    assert body["recipe_id"] == "11111111-1111-1111-1111-111111111111"
    assert len(body["leads"]) == 1
    assert body["leads"][0]["id"] == "33333333-3333-3333-3333-333333333333"
    assert captured["saved_leads"][0]["name"] == "Jane Smith"
