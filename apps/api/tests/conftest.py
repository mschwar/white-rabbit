from pathlib import Path
import os
import sys

# Match API startup defaults before tests import FastAPI, Pydantic, or SQLAlchemy.
os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "__all__")
os.environ.setdefault("DISABLE_SQLALCHEMY_CEXT_RUNTIME", "1")

REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_SRC = REPO_ROOT / "packages" / "core" / "src"
APP_ROOT = Path(__file__).resolve().parents[1]

for candidate in (CORE_SRC, APP_ROOT, REPO_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
