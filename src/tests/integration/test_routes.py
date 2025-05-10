from io import BytesIO

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
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}

    async def test_ingest_glucose_csv_wrong_file_format(self):
        # Simulate a non-CSV file
        file = BytesIO(b'{"key": "value"}')

        response = client.post(
            "/api/v1/upload-csv/",
            files={"file": ("test.json", file, "application/json")},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Only CSV files are allowed"

    async def test_get_glucose_levels_success(self, create_dummpy_glucose_records):
        response = client.get(
            "/api/v1/levels/?user_id=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa&limit=100&offset=0&sort=desc"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 5

    async def test_get_glucose_levels_no_records(self):
        response = client.get(
            "/api/v1/levels/?user_id=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa&limit=100&offset=0&sort=desc"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    async def test_get_glucose_levels_pagination(self, create_dummpy_glucose_records):
        response = client.get(
            "/api/v1/levels/?user_id=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa&limit=3&offset=0&sort=desc"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 3

    async def test_get_glucose_levels_invalid_limit(self):
        response = client.get(
            "/api/v1/levels/?user_id=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa&limit=-1&offset=0&sort=desc"
        )
        assert response.status_code == 422

    async def test_get_glucose_level_by_id_success(self, create_dummpy_glucose_records):
        response = client.get("api/v1/levels/1/")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert response.json() == {
            "id": 1,
            "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "device": "FreeStyle LibreLink",
            "serial_number": "1D48A10E-DDFB-4888-8158-026F08814832",
            "device_timestamp": "2021-02-18T10:57:00",
            "record_type": 0,
            "glucose_value_history": 77,
            "glucose_scan": None,
            "non_numeric_fast_insulin": None,
            "fast_insulin_units": None,
            "non_numeric_food": None,
            "carbs_grams": None,
            "carbs_portions": None,
            "non_numeric_long_insulin": None,
            "long_insulin_units": None,
            "notes": None,
            "glucose_teststrip": None,
            "ketone": None,
            "meal_insulin": None,
            "correction_insulin": None,
            "insulin_change_by_user": None,
        }

    async def test_get_glucose_level_by_id_not_found(self):
        response = client.get("api/v1/levels/999999/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Glucose level with ID=999999 not found."}

    async def test_get_glucose_level_by_id_invalid_id(self):
        response = client.get("api/v1/levels/abc/")
        assert response.status_code == 422

    async def test_get_glucose_level_by_id_schema(self, create_dummpy_glucose_records):
        response = client.get("api/v1/levels/1/")
        data = response.json()
        expected_keys = [
            "id",
            "user_id",
            "device",
            "serial_number",
            "device_timestamp",
            "record_type",
            "glucose_value_history",
            "glucose_scan",
            "non_numeric_fast_insulin",
            "fast_insulin_units",
            "non_numeric_food",
            "carbs_grams",
            "carbs_portions",
            "non_numeric_long_insulin",
            "long_insulin_units",
            "notes",
            "glucose_teststrip",
            "ketone",
            "meal_insulin",
            "correction_insulin",
            "insulin_change_by_user",
        ]
        assert all(key in data for key in expected_keys)
