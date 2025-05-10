import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.db.main import DatabaseManager
from src.tests.integration.helpers import get_session_test, get_settings_test
from src.webapp.main import app, get_settings

client = TestClient(app)


@pytest_asyncio.fixture(scope="class", autouse=True)
async def override_dependency():
    app.dependency_overrides[DatabaseManager.get_session] = get_session_test
    app.dependency_overrides[get_settings] = get_settings_test
    yield
    app.dependency_overrides = {}


@pytest.mark.asyncio
class TestRoutes:
    async def test_health_check_healthy(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}
