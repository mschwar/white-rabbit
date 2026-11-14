import logging
import sys
import time

import pytest
from api.main import (
    ReadinessCheck,
    _check_database,
    _check_openai,
    _preflight_check,
    _redact_database_url,
    app,
    collect_readiness,
)
from fastapi.testclient import TestClient


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
    monkeypatch.setenv("WR_API_INTERNAL_TOKEN", "set")
    monkeypatch.setenv("DATABASE_URL", "set")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://fake.invalid/v1")
    monkeypatch.setattr("sys.modules", {**sys.modules})
    # Remove pytest from modules to trigger full check
    fake_modules = {k: v for k, v in sys.modules.items() if k != "pytest"}
    monkeypatch.setattr("api.main.sys.modules", fake_modules)

    class FakeClient:
        class models:
            @staticmethod
            def retrieve(model):
                return {"id": model}

    monkeypatch.setattr("openai.OpenAI", lambda **kwargs: FakeClient())
    _preflight_check()  # should not raise


def test_preflight_redacts_database_url_credentials(monkeypatch, caplog):
    secret_pw = "s3cr3t_db_p4ssw0rd!"
    monkeypatch.setenv("OPENAI_API_KEY", "set")
    monkeypatch.setenv("TAVILY_API_KEY", "set")
    monkeypatch.setenv("WR_SHARED_PASSWORD", "set")
    monkeypatch.setenv("WR_SESSION_SECRET", "set")
    monkeypatch.setenv("WR_API_INTERNAL_TOKEN", "set")
    monkeypatch.setenv(
        "DATABASE_URL",
        f"postgresql://wr_admin:{secret_pw}@db.internal.example:5432/white_rabbit",
    )
    fake_modules = {k: v for k, v in sys.modules.items() if k != "pytest"}
    monkeypatch.setattr("api.main.sys.modules", fake_modules)

    class FakeClient:
        class models:
            @staticmethod
            def retrieve(model):
                return {"id": model}

    monkeypatch.setattr("openai.OpenAI", lambda **kwargs: FakeClient())

    with caplog.at_level(logging.INFO, logger="white_rabbit.api"):
        _preflight_check()

    assert secret_pw not in caplog.text
    assert "db.internal.example" in caplog.text
    assert "***" in caplog.text
    assert secret_pw not in _redact_database_url(
        f"postgresql://wr_admin:{secret_pw}@db.internal.example:5432/wr?password={secret_pw}"
    )
    assert _redact_database_url(f"dbname=wr password={secret_pw}") == "<configured>"


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

    with pytest.raises(RuntimeError, match="Missing required env") as exc_info:
        _preflight_check()

    message = str(exc_info.value)
    assert "OPENAI_API_KEY" in message
    assert "TAVILY_API_KEY" in message
    assert "DATABASE_URL" in message


def test_check_database_reuses_shared_engine_and_never_leaks_error_strings(monkeypatch):
    calls: list[str] = []

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, statement):
            return 1

    class FakeEngine:
        def connect(self):
            return FakeConnection()

    fake_engine = FakeEngine()

    def fake_get_shared_engine(url: str | None = None):
        calls.append(url or "")
        return fake_engine

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:supersecret@db.example:5432/wr")
    monkeypatch.setattr("api.main.get_shared_engine", fake_get_shared_engine)

    first = _check_database(timeout_seconds=0.5)
    second = _check_database(timeout_seconds=0.5)

    assert first.status == "ready"
    assert second.status == "ready"
    assert first.details["shared_engine"] is True
    assert len(calls) == 2

    def failing_shared_engine(url: str | None = None):
        raise RuntimeError("FATAL: password authentication failed with secret=top_secret_pw")

    monkeypatch.setattr("api.main.get_shared_engine", failing_shared_engine)
    failed = _check_database(timeout_seconds=0.5)
    assert failed.status == "unavailable"
    assert "top_secret_pw" not in failed.message
    assert "top_secret_pw" not in str(failed.details)
    assert failed.details["error_type"] == "RuntimeError"


def test_check_openai_uses_config_only_probe_without_live_network_call(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-secret")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    def forbid_openai_client(**kwargs):
        raise AssertionError("OpenAI client should not be instantiated during readiness checks")

    monkeypatch.setattr("openai.OpenAI", forbid_openai_client)

    result = _check_openai(timeout_seconds=0.5)
    assert result.status == "ready"
    assert result.details["probe"] == "config_only"
    assert "sk-test-secret" not in result.message
    assert "sk-test-secret" not in str(result.details)


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
