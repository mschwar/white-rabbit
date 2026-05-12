import time
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

    payload = collect_readiness(timeout_seconds=0.05, dependency_timeout_seconds=0.05).model_dump()

    assert payload["status"] == "unavailable"
    assert payload["budget_seconds"] == 0.05
    assert payload["elapsed_seconds"] < 0.15
    process = next(check for check in payload["checks"] if check["name"] == "process")
    assert process["status"] == "ready"
    config = next(check for check in payload["checks"] if check["name"] == "config")
    assert config["status"] == "misconfigured"
    assert "OPENAI_API_KEY" in config["details"]["missing"]
    assert config["details"]["env_presence"]["OPENAI_API_KEY"] == {"present": False}
    assert "value" not in config["details"]["env_presence"]["OPENAI_API_KEY"]
    env_key_map = {
        "database": "DATABASE_URL",
        "openai": "OPENAI_API_KEY",
        "tavily": "TAVILY_API_KEY",
        "sandbox": "DATABASE_URL",
    }
    for name in ("database", "openai", "tavily", "sandbox"):
        check = next(item for item in payload["checks"] if item["name"] == name)
        assert check["status"] == "misconfigured"
        assert check["details"]["env_presence"][env_key_map[name]] == {"present": False}


def test_health_route_does_not_invoke_readiness_dependencies(monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("readiness dependency should not be called by /health")

    monkeypatch.setattr("api.main._check_database", _fail)
    monkeypatch.setattr("api.main._check_openai", _fail)
    monkeypatch.setattr("api.main._check_tavily", _fail)
    monkeypatch.setattr("api.main._check_sandbox", _fail)

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "white-rabbit-api"}


def test_readiness_returns_within_budget_when_dependencies_are_slow(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "set")
    monkeypatch.setenv("TAVILY_API_KEY", "set")
    monkeypatch.setenv("WR_SHARED_PASSWORD", "set")
    monkeypatch.setenv("WR_SESSION_SECRET", "set")
    monkeypatch.setenv("WR_API_INTERNAL_TOKEN", "set")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    def _slow_check(name: str):
        def _inner(timeout_seconds: float = 1.0):
            time.sleep(0.2)
            return ReadinessCheck(
                name=name,
                status="ready",
                message=f"{name} ready.",
                elapsed_seconds=0.2,
                details={"timeout_seconds": timeout_seconds},
            )

        return _inner

    monkeypatch.setattr("api.main._check_database", _slow_check("database"))
    monkeypatch.setattr("api.main._check_openai", _slow_check("openai"))
    monkeypatch.setattr("api.main._check_tavily", _slow_check("tavily"))
    monkeypatch.setattr("api.main._check_sandbox", _slow_check("sandbox"))

    start = time.perf_counter()
    payload = collect_readiness(timeout_seconds=0.05, dependency_timeout_seconds=0.2).model_dump()
    elapsed = time.perf_counter() - start

    assert elapsed < 0.15
    assert payload["elapsed_seconds"] < 0.15
    assert payload["budget_seconds"] == 0.05
    assert payload["status"] == "unavailable"
    for name in ("database", "openai", "tavily", "sandbox"):
        check = next(item for item in payload["checks"] if item["name"] == name)
        assert check["status"] == "unavailable"
        assert check["details"]["timed_out"] is True


def test_health_does_not_require_database_url_at_startup(monkeypatch):
    monkeypatch.setenv("WR_ENV", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
