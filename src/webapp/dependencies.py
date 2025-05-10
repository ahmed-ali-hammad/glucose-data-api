"""
Dependency Injection container.
Centralizes factory functions for clean dependency management.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.main import DatabaseManager
from src.db.repository import DatabaseRepository
from src.domain.service import ActionService


def get_database_repository(
    session: AsyncSession = Depends(DatabaseManager.get_session),
) -> DatabaseRepository:
    """
    Creates and returns an instance of DatabaseRepository.

    Args:
        session (AsyncSession): The database session.

    Returns:
        DatabaseRepository: An instance of DatabaseRepository.
    """
    return DatabaseRepository(session)


def get_action_service(
    database_repository: DatabaseRepository = Depends(get_database_repository),
) -> ActionService:
    """
    Creates and returns an instance of ActionService with the provided storage.

    Args:
        storage (DatabaseRepository): The repository instance used for data storage and retrieval.

    Returns:
        ActionService: A configured ActionService instance ready for use.
    """
    return ActionService(database_repository=database_repository)
