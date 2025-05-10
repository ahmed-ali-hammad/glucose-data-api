from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StatusResponse(BaseModel):
    status: str


class RecordCSV(BaseModel):
    Gerät: str
    Seriennummer: str
    Gerätezeitstempel: datetime
    Aufzeichnungstyp: int
    Glukosewert_Verlauf_mg_dL: Optional[int] = Field(
        None, alias="Glukosewert-Verlauf mg/dL"
    )
    Glukose_Scan_mg_dL: Optional[int] = None
    Nicht_numerisches_schnellwirkendes_Insulin: Optional[str] = None
    Schnellwirkendes_Insulin_Einheiten: Optional[float] = None
    Nicht_numerische_Nahrungsdaten: Optional[str] = None
    Kohlenhydrate_Gramm: Optional[float] = None
    Kohlenhydrate_Portionen: Optional[float] = None
    Nicht_numerisches_Depotinsulin: Optional[str] = None
    Depotinsulin_Einheiten: Optional[float] = None
    Notizen: Optional[str] = None
    Glukose_Teststreifen_mg_dL: Optional[int] = None
    Keton_mmol_L: Optional[float] = None
    Mahlzeiteninsulin_Einheiten: Optional[float] = None
    Korrekturinsulin_Einheiten: Optional[float] = None
    Insulin_Änderung_durch_Anwender_Einheiten: Optional[float] = None

    @field_validator("Gerätezeitstempel", mode="before")
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%d-%m-%Y %H:%M")
        return value

    @field_validator("Glukosewert_Verlauf_mg_dL", mode="before")
    def empty_str_to_none(cls, v):
        return None if v == "" else v


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class GlucoseLevelResponse(BaseModel):
    id: int
    user_id: str
    device: str
    serial_number: str
    device_timestamp: datetime
    record_type: int
    glucose_value_history: Optional[int]
    glucose_scan: Optional[float]
    non_numeric_fast_insulin: Optional[str]
    fast_insulin_units: Optional[float]
    non_numeric_food: Optional[str]
    carbs_grams: Optional[float]
    carbs_portions: Optional[float]
    non_numeric_long_insulin: Optional[str]
    long_insulin_units: Optional[float]
    notes: Optional[str]
    glucose_teststrip: Optional[float]
    ketone: Optional[float]
    meal_insulin: Optional[float]
    correction_insulin: Optional[float]
    insulin_change_by_user: Optional[float]

    model_config = ConfigDict(from_attributes=True)
