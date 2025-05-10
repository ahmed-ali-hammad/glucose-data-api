import csv
from datetime import datetime
from io import StringIO
from typing import Any, Sequence

from src.db.models import UserGlucoseData
from src.db.repository import DatabaseRepository
from src.domain.exceptions import WrongFileFormatException


class GlucoseDataService:
    """
    Service class for managing and processing glucose data.
    """

    def __init__(self, database_repository: DatabaseRepository) -> None:
        self.database_repository = database_repository

    async def process_csv_file(self, file: Any) -> tuple[Any, csv.DictReader[str]]:
        """
        Processes a CSV file, validates its format, and extracts the user ID.

        Args:
            file (UploadFile): The uploaded CSV file containing glucose data.

        Returns:
            Tuple[str, csv.DictReader]: user ID and a CSV DictReader object that parses the CSV data.

        Raises:
            WrongFileFormatException: If the uploaded file is not a CSV format.
        """
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

        return user_id, csv_reader

    async def store_glucose_records(self, records: list, user_id: str) -> None:
        """
        Saves a list of glucose records for the specified user.

        Args:
            records (list): A list of parsed glucose records.
            user_id (str): The ID of the user the records belong to.
        """
        await self.database_repository.save_glucose_records_to_database(
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
        """
        Retrieves a paginated list of glucose records for a specific user,

        Args:
            user_id (str): The ID of the user whose glucose data should be retrieved.
            start (datetime | None): Optional start date for filtering records.
            end (datetime | None): Optional end date for filtering records.
            sort (str): Sort direction, either 'asc' or 'desc'. Defaults to 'desc'.
            limit (int): Maximum number of records to return. Defaults to 100.
            offset (int): Number of records to skip for pagination. Defaults to 0.

        Returns:
            Sequence[UserGlucoseData]: A list of glucose records matching the criteria.
        """
        glucose_levels = (
            await self.database_repository.get_user_glucose_data_from_database(
                user_id=user_id,
                start=start,
                end=end,
                sort=sort,
                limit=limit,
                offset=offset,
            )
        )
        return glucose_levels

    async def get_glucose_level_by_id(self, id: int) -> UserGlucoseData | None:
        """
        Retrieves a single glucose level record by its unique ID.

        Args:
            id (int): The ID of the glucose level record to retrieve.

        Returns:
            UserGlucoseData | None: The glucose level record if found, otherwise None.
        """
        glucose_level = (
            await self.database_repository.get_glucose_level_by_id_from_database(id=id)
        )
        return glucose_level
