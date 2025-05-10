import pytest_asyncio

from src.db.repository import DatabaseRepository
from src.domain.service import ActionService
from src.tests.integration.helpers import get_session_test


@pytest_asyncio.fixture
async def test_db_session():
    async for session in get_session_test():
        yield session


@pytest_asyncio.fixture
async def action_service_test_instance(test_db_session):
    """
    Provide an instance of the ActionService for testing purposes.
    """
    database_storage = DatabaseRepository(test_db_session)
    action_service = ActionService(database_storage)

    return action_service
