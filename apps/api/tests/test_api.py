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
