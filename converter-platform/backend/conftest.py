"""
Shared pytest fixtures.

The `client` fixture provides a FastAPI TestClient wired to a
throwaway SQLite database and temp storage directory so each test
module starts with a completely clean slate — no shared state, no
leftover files.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def client(tmp_path, monkeypatch):
    """
    Isolated FastAPI TestClient per test function.

    Each invocation gets:
      - Its own SQLite database (so tests can't bleed state between runs)
      - Its own temp storage directory
      - RUN_TASKS_EAGERLY=true (no Celery/Redis needed)
    """
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/test.db")
    monkeypatch.setenv("LOCAL_STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setenv("RUN_TASKS_EAGERLY", "true")
    monkeypatch.setenv("ENV", "development")  # triggers create_all on startup

    # Settings are cached — clear the cache so fresh env vars take effect
    from app.config import get_settings
    from app.storage import get_storage
    from app.converters.registry import _instances

    get_settings.cache_clear()
    get_storage.cache_clear()
    _instances.cache_clear()

    from app.main import app

    with TestClient(app) as c:
        yield c

    # Cleanup caches after test so the next test gets a clean slate
    get_settings.cache_clear()
    get_storage.cache_clear()
    _instances.cache_clear()
