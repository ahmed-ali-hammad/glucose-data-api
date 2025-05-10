from datetime import datetime

import pytest
from sqlalchemy import select

from src.db.models import UserGlucoseData
from src.webapp.schema import GlucoseRecordCSV


@pytest.mark.asyncio
class TestGlucoseDataService:
    async def test_store_glucose_records_success(
        self, glucose_data_service_test_instance, test_db_session
    ):
        dummy_records = [
            GlucoseRecordCSV(
                Gerät="FreeStyle LibreLink",
                Seriennummer="1D48A10E-DDFB-4888-8158-026F08814832",
                Gerätezeitstempel="10-02-2021 10:25",
                Aufzeichnungstyp=0,
                Glukosewert_Verlauf_mg_dL=77,
            )
        ]

        await glucose_data_service_test_instance.store_glucose_records(
            records=dummy_records, user_id="rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr"
        )

        query = select(UserGlucoseData)
        result = await test_db_session.execute(query)
        glucose_level = result.scalars().all()

        assert len(glucose_level) == 1

    async def test_store_multiple_glucose_records_success(
        self, glucose_data_service_test_instance, test_db_session
    ):
        dummy_records = [
            GlucoseRecordCSV(
                Gerät="FreeStyle LibreLink",
                Seriennummer="1D48A10E-DDFB-4888-8158-026F08814832",
                Gerätezeitstempel="10-02-2021 10:25",
                Aufzeichnungstyp=0,
                Glukosewert_Verlauf_mg_dL=77,
            ),
            GlucoseRecordCSV(
                Gerät="FreeStyle LibreLink",
                Seriennummer="1D48A10E-DDFB-4888-8158-026F08814832",
                Gerätezeitstempel="10-02-2021 10:35",
                Aufzeichnungstyp=0,
                Glukosewert_Verlauf_mg_dL=78,
            ),
        ]

        await glucose_data_service_test_instance.store_glucose_records(
            records=dummy_records, user_id="rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr"
        )

        query = select(UserGlucoseData)
        result = await test_db_session.execute(query)
        glucose_level = result.scalars().all()

        assert len(glucose_level) == 2

    async def test_store_empty_glucose_records(
        self, glucose_data_service_test_instance, test_db_session
    ):
        dummy_records = []

        await glucose_data_service_test_instance.store_glucose_records(
            records=dummy_records, user_id="rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr"
        )

        query = select(UserGlucoseData)
        result = await test_db_session.execute(query)
        glucose_level = result.scalars().all()

        assert len(glucose_level) == 0

    async def test_store_glucose_records_multiple_users(
        self, glucose_data_service_test_instance, test_db_session
    ):
        dummy_records = [
            GlucoseRecordCSV(
                Gerät="FreeStyle LibreLink",
                Seriennummer="1D48A10E-DDFB-4888-8158-026F08814832",
                Gerätezeitstempel="10-02-2021 10:25",
                Aufzeichnungstyp=0,
                Glukosewert_Verlauf_mg_dL=77,
            ),
        ]

        await glucose_data_service_test_instance.store_glucose_records(
            records=dummy_records, user_id="rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr"
        )

        await glucose_data_service_test_instance.store_glucose_records(
            records=dummy_records, user_id="ssssssss-ssss-ssss-ssss-ssssssssssss"
        )

        query = select(UserGlucoseData)
        result = await test_db_session.execute(query)
        glucose_level = result.scalars().all()

        assert len(glucose_level) == 2

    async def test_get_user_glucose_data_success(
        self, glucose_data_service_test_instance, create_dummpy_glucose_records
    ):
        glucose_levels = await glucose_data_service_test_instance.get_user_glucose_data(
            user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        )

        assert isinstance(glucose_levels, list)
        assert len(glucose_levels) == 5

    async def test_get_user_glucose_data_no_records(
        self, glucose_data_service_test_instance
    ):
        # Using a user ID that does not exist or has no records
        glucose_levels = await glucose_data_service_test_instance.get_user_glucose_data(
            user_id="nonexistent-user-id"
        )

        assert isinstance(glucose_levels, list)
        assert len(glucose_levels) == 0

    async def test_get_user_glucose_data_with_time_range(
        self, glucose_data_service_test_instance, create_dummpy_glucose_records
    ):
        start = datetime(2021, 2, 18, 10, 57)
        end = datetime(2021, 2, 18, 11, 57)

        glucose_levels = await glucose_data_service_test_instance.get_user_glucose_data(
            user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", start=start, end=end
        )

        assert isinstance(glucose_levels, list)
        assert len(glucose_levels) == 5
        assert all(start <= level.device_timestamp <= end for level in glucose_levels)

    async def test_get_user_glucose_data_sorting(
        self, glucose_data_service_test_instance, create_dummpy_glucose_records
    ):
        glucose_levels_desc = (
            await glucose_data_service_test_instance.get_user_glucose_data(
                user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", sort="desc"
            )
        )

        glucose_levels_asc = (
            await glucose_data_service_test_instance.get_user_glucose_data(
                user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", sort="asc"
            )
        )

        assert isinstance(glucose_levels_desc, list)
        assert isinstance(glucose_levels_asc, list)

        assert glucose_levels_desc[0].id >= glucose_levels_asc[0].id

    async def test_get_user_glucose_data_pagination(
        self, glucose_data_service_test_instance, create_dummpy_glucose_records
    ):
        # Request first page with a limit of 2 records
        glucose_levels_page_1 = (
            await glucose_data_service_test_instance.get_user_glucose_data(
                user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", limit=2, offset=0
            )
        )

        # Request second page with a limit of 2 records
        glucose_levels_page_2 = (
            await glucose_data_service_test_instance.get_user_glucose_data(
                user_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", limit=2, offset=2
            )
        )

        assert len(glucose_levels_page_1) == 2
        assert len(glucose_levels_page_2) == 2

        page_1_ids = {level.id for level in glucose_levels_page_1}
        page_2_ids = {level.id for level in glucose_levels_page_2}

        # Making sure the returned ids are unique
        assert page_1_ids.isdisjoint(page_2_ids)

    async def test_get_glucose_level_by_id_success(
        self, glucose_data_service_test_instance, create_dummpy_glucose_records
    ):

        glucose_level = (
            await glucose_data_service_test_instance.get_glucose_level_by_id(1)
        )

        assert glucose_level is not None
        assert isinstance(glucose_level, UserGlucoseData)

    async def test_get_glucose_level_by_id_not_found(
        self, glucose_data_service_test_instance, create_dummpy_glucose_records
    ):
        glucose_level = (
            await glucose_data_service_test_instance.get_glucose_level_by_id(9999)
        )

        assert glucose_level is None
