import pytest
from pydantic import ValidationError

from src.db.main import check_db_connection
from src.webapp.settings import Settings


@pytest.mark.asyncio
class TestSettings:

    async def test_settings_builds_database_uri(self, monkeypatch):
        monkeypatch.setenv("DATABASE_USER", "db_hero")
        monkeypatch.setenv("DATABASE_PASSWORD", "supersecret123")
        monkeypatch.setenv("DATABASE_HOST", "database-central.de")
        monkeypatch.setenv("DATABASE_PORT", "3306")
        monkeypatch.setenv("DATABASE_NAME", "testdb")

        settings = Settings()

        assert settings.DATABASE_URI == (
            "mysql://db_hero:supersecret123@database-central.de:3306/testdb?charset=utf8mb4"
        )

        assert settings.ASYNC_DATABASE_URI == (
            "mysql+asyncmy://db_hero:supersecret123@database-central.de:3306/testdb?charset=utf8mb4"
        )

    async def test_settings_raises_error_on_missing_value(self, monkeypatch):
        monkeypatch.delenv("DATABASE_USER", raising=False)
        monkeypatch.setenv("DATABASE_PASSWORD", "supersecret123")
        monkeypatch.setenv("DATABASE_HOST", "database-central.de")
        monkeypatch.setenv("DATABASE_PORT", "3306")
        monkeypatch.setenv("DATABASE_NAME", "testdb")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "DATABASE_USER" in str(exc_info.value)
        assert "DATABASE_URI" in str(exc_info.value)


@pytest.mark.asyncio
class TestDBConnection:

    async def test_check_db_connection_success(self, mock_db_session):
        mock_db_session.execute.return_value = True
        is_connected = await check_db_connection(mock_db_session)

        mock_db_session.execute.assert_called_once()
        assert is_connected is True

    async def test_check_db_connection_failure(self, mock_db_session):
        mock_db_session.execute.side_effect = Exception("Database connection error")

        is_connected = await check_db_connection(mock_db_session)

        mock_db_session.execute.assert_called_once()
        assert is_connected is False
