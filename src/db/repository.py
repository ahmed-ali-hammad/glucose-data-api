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

    async def save_records_to_database(
        self,
        records: list,
        user_id: str,
    ):
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
        query = select(UserGlucoseData).where(UserGlucoseData.id == id)

        result = await self.session.execute(query)

        glucose_level = result.scalars().first()

        return glucose_level
