import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repository import DatabaseRepository
from src.domain.service import ActionService


@pytest_asyncio.fixture
async def mock_db_session(mocker):
    session = mocker.MagicMock(spec=AsyncSession)
    yield session


@pytest_asyncio.fixture
async def action_service_test_instance(test_db_session):
    """
    Provide an instance of the ActionService for testing purposes.
    """
    database_storage = DatabaseRepository(test_db_session)
    action_service = ActionService(database_storage)

    return action_service
