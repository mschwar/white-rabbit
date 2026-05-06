from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent.parent / "src" / "core")]


def hello() -> str:
    return "Hello from core!"
