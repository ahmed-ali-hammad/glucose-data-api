import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repository import DatabaseRepository
from src.domain.service import GlucoseDataService


@pytest_asyncio.fixture
async def mock_db_session(mocker):
    session = mocker.MagicMock(spec=AsyncSession)
    yield session


@pytest_asyncio.fixture
async def glucose_data_service_test_instance(test_db_session):
    """
    Provide an instance of the GlucoseDataService for testing purposes.
    """
    database_repository = DatabaseRepository(test_db_session)
    glucose_data_service = GlucoseDataService(database_repository)

    return glucose_data_service
