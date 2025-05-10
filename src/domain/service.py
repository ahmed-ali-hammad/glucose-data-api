import csv
import logging
from datetime import datetime
from io import StringIO
from typing import Any, Sequence

from src.db.models import UserGlucoseData
from src.db.repository import DatabaseRepository
from src.domain.exceptions import WrongFileFormatException

_logger = logging.getLogger(__name__)


class ActionService:
    """
    Service class.
    """

    def __init__(self, database_repository: DatabaseRepository) -> None:
        self.database_repository = database_repository

    async def process_csv_file(self, file) -> tuple[Any, csv.DictReader[str]]:
        # Check if the file is a valid CSV
        if file.filename is None or not file.filename.lower().endswith(".csv"):
            raise WrongFileFormatException

        # Extract user_id from the file name
        user_id = file.filename.removesuffix(".csv")

        # Read and decode the file contents
        contents = await file.read()
        csv_text = contents.decode("utf-8")

        # Remove the header and any empty line
        filtered_lines = [
            line
            for line in csv_text.splitlines()
            if line.strip() != "" and "Glukose-Werte" not in line
        ]
        csv_data = "\n".join(filtered_lines)  # Rejoin the remaining lines

        # Parse the CSV data
        csv_reader = csv.DictReader(StringIO(csv_data))

        # Return the parsed CSV data as a list of dictionaries
        return user_id, csv_reader

    async def save_to_database(self, records: list, user_id: str):
        await self.database_repository.save_records_to_database(
            records=records, user_id=user_id
        )

    async def get_user_glucose_data(
        self,
        user_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
        sort: str = "desc",
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[UserGlucoseData]:

        levels = await self.database_repository.get_user_glucose_data_from_database(
            user_id=user_id,
            start=start,
            end=end,
            sort=sort,
            limit=limit,
            offset=offset,
        )

        return levels

    async def get_glucose_level_by_id(self, id: int) -> UserGlucoseData | None:
        glucose_level = (
            await self.database_repository.get_glucose_level_by_id_from_database(id=id)
        )
        return glucose_level
