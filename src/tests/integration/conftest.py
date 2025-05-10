import pytest_asyncio
from sqlalchemy.dialects.mysql import insert

from src.db.models import UserGlucoseData
from src.db.repository import DatabaseRepository
from src.domain.service import GlucoseDataService
from src.tests.integration.helpers import get_session_test


@pytest_asyncio.fixture
async def test_db_session():
    async for session in get_session_test():
        yield session


@pytest_asyncio.fixture
async def glucose_data_service_test_instance(test_db_session):
    """
    Provide an instance of the GlucoseDataService for testing purposes.
    """
    database_repository = DatabaseRepository(test_db_session)
    glucose_data_service = GlucoseDataService(database_repository)

    return glucose_data_service


@pytest_asyncio.fixture
async def create_dummpy_glucose_records(test_db_session):
    dummy_records = [
        {
            "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "device": "FreeStyle LibreLink",
            "serial_number": "1D48A10E-DDFB-4888-8158-026F08814832",
            "device_timestamp": "2021-02-18 10:57:00",
            "record_type": 0,
            "glucose_value_history": 77,
        },
        {
            "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "device": "FreeStyle LibreLink",
            "serial_number": "1D48A10E-DDFB-4888-8158-026F08814832",
            "device_timestamp": "2021-02-18 11:12:00",
            "record_type": 0,
            "glucose_value_history": 78,
        },
        {
            "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "device": "FreeStyle LibreLink",
            "serial_number": "1D48A10E-DDFB-4888-8158-026F08814832",
            "device_timestamp": "2021-02-18 11:27:00",
            "record_type": 0,
            "glucose_value_history": 78,
            "glucose_scan": None,
        },
        {
            "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "device": "FreeStyle LibreLink",
            "serial_number": "1D48A10E-DDFB-4888-8158-026F08814832",
            "device_timestamp": "2021-02-18 11:42:00",
            "record_type": 0,
            "glucose_value_history": 76,
        },
        {
            "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "device": "FreeStyle LibreLink",
            "serial_number": "1D48A10E-DDFB-4888-8158-026F08814832",
            "device_timestamp": "2021-02-18 11:57:00",
            "record_type": 0,
            "glucose_value_history": 75,
        },
    ]

    statement = insert(UserGlucoseData).values(dummy_records)
    await test_db_session.execute(statement)
    await test_db_session.commit()
