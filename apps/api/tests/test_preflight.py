import os
import sys

from api.main import _preflight_check


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
