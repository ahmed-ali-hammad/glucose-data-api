import logging
from contextlib import asynccontextmanager
from datetime import datetime
from functools import lru_cache
from typing import List, Optional, Sequence

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.main import DatabaseManager, check_db_connection
from src.domain.exceptions import WrongFileFormatException
from src.domain.service import GlucoseDataService
from src.webapp.dependencies import get_glucose_data_service
from src.webapp.schema import (
    GlucoseLevelResponse,
    GlucoseRecordCSV,
    SortOrder,
    StatusResponse,
)
from src.webapp.settings import Settings

_logger = logging.getLogger(__name__)


@lru_cache
def get_settings():
    """
    Loads the application settings.

    Returns:
        Settings: The cached settings object.
    """
    return Settings()


@asynccontextmanager
async def life_span(app: FastAPI):
    # Initialize DB and Logging
    DatabaseManager(get_settings().ASYNC_DATABASE_URI)
    logging.basicConfig(
        level=get_settings().LOG_LEVEL,
        format="%(levelname)s:%(asctime)s: %(name)s: %(message)s",
    )
    _logger.info("Starting API service...")

    yield

    _logger.info("Shutting down API service...")
    await DatabaseManager.dispose_engine()
    _logger.info("Cleanup complete. Bye!")


app = FastAPI(
    title="Glucose Data API",
    description="An API for uploading, storing, and retrieving glucose level records.",
    version="1.0.0",
    lifespan=life_span,
)


@app.get(
    "/api/v1/health",
    status_code=status.HTTP_200_OK,
    responses={500: {"description": "Internal server error"}},
)
async def health_check(
    session: AsyncSession = Depends(DatabaseManager.get_session),
) -> StatusResponse:
    """
    Endpoint that checks if the app and database are functioning.

    Args:
        session (AsyncSession): The database session.

    Returns:
        - HTTP 200:: `OK` status for the application and database.
        - HTTP 500: If something goes wrong.
    """

    db_connection_status = await check_db_connection(session)

    if not db_connection_status:
        _logger.warning("Health check failed due to unhealty Database!")
        raise HTTPException(status_code=500, detail="Database connection failed")

    return StatusResponse(status="OK")


@app.post(
    "/api/v1/upload-csv/",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Wrong File format"},
        500: {"description": "Internal server error"},
    },
)
async def ingest_glucose_csv(
    glucose_data_service: GlucoseDataService = Depends(get_glucose_data_service),
    file: UploadFile = File(...),
) -> StatusResponse:
    """
    An endpoint for uploading a CSV file containing a user glucose data.

    Args:
        file (UploadFile): The uploaded CSV file.

    Returns:
        - HTTP 200: Indicating the success of the upload.
        - HTTP 400: If the file is not in a CSV format.
        - HTTP 422: If the CSV data is invalid.
        - HTTP 500: If something goes wrong.
    """
    # First step: Check and extract data from CSV file.
    try:
        user_id, csv_reader = await glucose_data_service.process_csv_file(file)
    except WrongFileFormatException:
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    except Exception as ex:
        _logger.error(
            f"Error while extracting records from CSV. Exception: {ex}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )

    # Second step: Validate and process rows
    try:
        records: List[GlucoseRecordCSV] = []
        for row in csv_reader:
            try:
                records.append(GlucoseRecordCSV(**row))
            except Exception as e:
                raise HTTPException(
                    status_code=422, detail=f"Invalid CSV data: {str(e)}"
                )

        await glucose_data_service.store_glucose_records(
            records=records, user_id=user_id
        )
        return StatusResponse(status=f"Successfully processed {len(records)} recordes")

    except HTTPException:
        raise  # Re-raise existing HTTP exceptions

    except Exception as ex:
        _logger.error(
            f"Error while validating or saving records. Exception: {ex}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@app.get(
    "/api/v1/levels/",
    status_code=status.HTTP_200_OK,
    responses={
        500: {"description": "Internal server error"},
    },
)
async def get_glucose_levels(
    glucose_data_service: GlucoseDataService = Depends(get_glucose_data_service),
    user_id: str = Query(..., description="User ID"),
    start: Optional[datetime] = Query(None, description="Start timestamp (ISO format)"),
    end: Optional[datetime] = Query(None, description="End timestamp (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    sort: SortOrder = SortOrder.desc,
) -> Sequence[GlucoseLevelResponse]:
    """
    Endpoint for retrieving glucose data for a specific user, with optional
    filters for timestamps, pagination, and sorting.

    Args:
        user_id (str): User ID for whom the glucose data is requested.
        start (Optional[datetime]): Start timestamp for filtering records (ISO format).
        end (Optional[datetime]): End timestamp for filtering records (ISO format).
        limit (int): Number of results to return (between 1 and 1000).
        offset (int): Pagination offset.
        sort (SortOrder): Sorting order for the results (`asc` or `desc`).

    Returns:
        - HTTP 200: A list of glucose level records for the user.
        - HTTP 500: If something goes wrong.
    """
    try:
        levels = await glucose_data_service.get_user_glucose_data(
            user_id=user_id,
            start=start,
            end=end,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        return levels
    except Exception as ex:
        _logger.error(
            f"Failed to retrieve glucose records for user_id= {user_id}. Exception: {ex}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@app.get(
    "/api/v1/levels/{id}/",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "ID doesn't exist"},
        500: {"description": "Internal server error"},
    },
)
async def get_glucose_level_by_id(
    id: int,
    glucose_data_service: GlucoseDataService = Depends(get_glucose_data_service),
) -> GlucoseLevelResponse:
    """
    Endpoint for retrieving a specific glucose level record by its ID.

    Args:
        id (int): The ID of the glucose level record to retrieve.

    Returns:
        GlucoseLevelResponse: The glucose level record corresponding to the provided ID.

    Raises:
        - HTTP 200: A glucose level record identified by the ID.
        - HTTP 404: if the glucose level with the specified ID doesn't exist.
        - HTTP 500: If something goes wrong.
    """
    try:
        glucose_level = await glucose_data_service.get_glucose_level_by_id(id=id)
    except Exception as ex:
        _logger.error(
            f"Failed to retrieve glucose level record with ID={id}. Exception: {ex}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )

    if glucose_level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Glucose level with ID={id} not found.",
        )
    return GlucoseLevelResponse.model_validate(glucose_level)
