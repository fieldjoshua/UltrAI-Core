import pytest
from app.services.health_service import HealthService
from app.services.cache_service import cache_service


@pytest.fixture(autouse=True)
def setup_dependencies(monkeypatch):
    # Patch DB connection check
    import app.database.connection as db_conn

    monkeypatch.setattr(db_conn, "check_database_connection", lambda: True)
    # Patch cache availability
    monkeypatch.setattr(cache_service, "is_redis_available", lambda: False)
    # Patch LLM config service from health_service module
    import app.services.health_service as hs

    monkeypatch.setattr(
        hs.llm_config_service, "get_available_models", lambda: [{"provider": "test"}]
    )


def test_get_health_simple():
    service = HealthService()
    status = service.get_health_status(detailed=False)
    assert status["status"] in ("ok", "degraded")
    assert "timestamp" in status


def test_get_health_detailed():
    service = HealthService()
    status = service.get_health_status(detailed=True)
    assert "services" in status
    assert "llm_providers" in status
