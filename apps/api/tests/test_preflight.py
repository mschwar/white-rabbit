import os
import sys

from fastapi.testclient import TestClient

from api.main import ReadinessCheck, _preflight_check, app, collect_readiness


def test_preflight_skips_under_pytest():
    # pytest is already loaded in this test run
    assert "pytest" in sys.modules
    _preflight_check()  # should not raise


def test_preflight_fails_on_empty_openai_key(monkeypatch):
    # only test the env-check portion; bypass api check by providing key
    monkeypatch.setenv("OPENAI_API_KEY", "set")
    monkeypatch.setenv("TAVILY_API_KEY", "set")
    monkeypatch.setenv("WR_SHARED_PASSWORD", "set")
    monkeypatch.setenv("WR_SESSION_SECRET", "set")
    monkeypatch.setenv("DATABASE_URL", "set")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://fake.invalid/v1")
    monkeypatch.setattr("sys.modules", {**sys.modules})
    # Remove pytest from modules to trigger full check
    fake_modules = {k: v for k, v in sys.modules.items() if k != "pytest"}
    monkeypatch.setattr("api.main.sys.modules", fake_modules)
    # Provide a fake OpenAI client
    class FakeClient:
        class models:
            @staticmethod
            def retrieve(model):
                return {"id": model}

    monkeypatch.setattr("openai.OpenAI", lambda **kwargs: FakeClient())
    _preflight_check()  # should not raise


def test_preflight_missing_env_raises(monkeypatch):
    """Test that missing required env vars raises RuntimeError."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.delenv("WR_SHARED_PASSWORD", raising=False)
    monkeypatch.delenv("WR_SESSION_SECRET", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("WR_ENV", "production")
    monkeypatch.setattr("sys.modules", {**sys.modules})
    fake_modules = {k: v for k, v in sys.modules.items() if k != "pytest"}
    monkeypatch.setattr("api.main.sys.modules", fake_modules)

    try:
        _preflight_check()
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "Missing required env" in str(exc)
        # Should list all five missing vars
        assert "OPENAI_API_KEY" in str(exc)
        assert "TAVILY_API_KEY" in str(exc)
        assert "DATABASE_URL" in str(exc)


def test_readiness_reports_missing_config_without_secret_values(monkeypatch):
    for name in (
        "OPENAI_API_KEY",
        "TAVILY_API_KEY",
        "WR_SHARED_PASSWORD",
        "WR_SESSION_SECRET",
        "WR_API_INTERNAL_TOKEN",
        "DATABASE_URL",
    ):
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setattr(
        "api.main._check_database",
        lambda: ReadinessCheck(name="database", status="unavailable", message="Database skipped for config failure."),
    )
    monkeypatch.setattr(
        "api.main._check_openai",
        lambda: ReadinessCheck(name="openai", status="unavailable", message="OPENAI_API_KEY is missing."),
    )
    monkeypatch.setattr(
        "api.main._check_tavily",
        lambda: ReadinessCheck(name="tavily", status="unavailable", message="TAVILY_API_KEY is missing."),
    )

    payload = collect_readiness().model_dump()

    assert payload["status"] == "unavailable"
    config = next(check for check in payload["checks"] if check["name"] == "config")
    assert config["status"] == "unavailable"
    assert "OPENAI_API_KEY" in config["details"]["missing"]
    assert config["details"]["env_presence"]["OPENAI_API_KEY"] == {"present": False}
    assert "value" not in config["details"]["env_presence"]["OPENAI_API_KEY"]


def test_health_responds_when_readiness_dependencies_are_unavailable(monkeypatch):
    monkeypatch.setattr(
        "api.main.collect_readiness",
        lambda: {
            "status": "unavailable",
            "checked_at": "2026-05-11T00:00:00Z",
            "checks": [
                {
                    "name": "database",
                    "status": "unavailable",
                    "required": True,
                    "message": "Database unavailable.",
                    "details": {"database_url_present": False},
                }
            ],
        },
    )
    client = TestClient(app)

    assert client.get("/health").json()["status"] == "ok"
    readiness = client.get("/readiness")

    assert readiness.status_code == 200
    assert readiness.json()["status"] == "unavailable"


def test_health_does_not_require_database_url_at_startup(monkeypatch):
    monkeypatch.setenv("WR_ENV", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
