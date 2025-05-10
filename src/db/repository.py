from datetime import datetime
from typing import Sequence

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import UserGlucoseData


class DatabaseRepository:
    """
    A class for handling db operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initializes the `DatabaseRepository` with an asynchronous session.

        Args:
            session (AsyncSession): database session.
        """
        self.session = session

    async def save_glucose_records_to_database(
        self,
        records: list,
        user_id: str,
    ) -> None:
        """
        Saves a list of parsed glucose records to the database for a specific user.

        Args:
            records (list): A list of parsed glucose data records.
            user_id (str): The ID of the user associated with the records.

        Returns:
            None
        """
        for record in records:
            db_record = UserGlucoseData.convert_item_to_db_model(record, user_id)
            self.session.add(db_record)
        await self.session.commit()

    async def get_user_glucose_data_from_database(
        self,
        user_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
        sort: str = "desc",
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[UserGlucoseData]:
        """
        Retrieves glucose records for a specific user from the database.

        Args:
            user_id (str): The ID of the user.
            start (datetime | None): Start timestamp for filtering (optional).
            end (datetime | None): End timestamp for filtering (optional).
            sort (str): Sort order based on device timestamp ("asc" or "desc").
            limit (int): Maximum number of records to retrieve.
            offset (int): Number of records to skip (for pagination).

        Returns:
            Sequence[UserGlucoseData]: A list of matching glucose records.
        """
        # Base query
        query = select(UserGlucoseData).where(UserGlucoseData.user_id == user_id)

        # Filtering
        if start:
            query = query.where(UserGlucoseData.device_timestamp >= start)
        if end:
            query = query.where(UserGlucoseData.device_timestamp <= end)

        # Apply sorting
        order = desc if sort == "desc" else asc
        query = query.order_by(order(UserGlucoseData.device_timestamp))

        # Pagination
        query = query.offset(offset).limit(limit)

        # Execute query and get results
        result = await self.session.execute(query)
        levels = result.scalars().all()

        return levels

    async def get_glucose_level_by_id_from_database(
        self, id: int
    ) -> UserGlucoseData | None:
        """
        Retrieves a single glucose record from the database by its unique ID.

        Args:
            id (int): The ID of the glucose record.

        Returns:
            UserGlucoseData | None: The matching glucose record if found, otherwise None.
        """
        query = select(UserGlucoseData).where(UserGlucoseData.id == id)
        result = await self.session.execute(query)
        glucose_level = result.scalars().first()

        return glucose_level
