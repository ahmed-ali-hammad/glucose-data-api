"""
Dependency Injection container.
Centralizes factory functions for clean dependency management.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.main import DatabaseManager
from src.db.repository import DatabaseRepository
from src.domain.service import GlucoseDataService


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


def get_glucose_data_service(
    database_repository: DatabaseRepository = Depends(get_database_repository),
) -> GlucoseDataService:
    """
    Creates and returns an instance of GlucoseDataService with the provided storage.

    Args:
        storage (DatabaseRepository): The repository instance used for data storage and retrieval.

    Returns:
        GlucoseDataService: A configured GlucoseDataService instance ready for use.
    """
    return GlucoseDataService(database_repository=database_repository)
