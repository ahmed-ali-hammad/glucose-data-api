from datetime import datetime

from sqlalchemy import BIGINT, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserGlucoseData(Base):
    """
    ORM model.
    """

    __tablename__ = "user_glucose_data"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)

    device: Mapped[str] = mapped_column(String(100))
    serial_number: Mapped[str] = mapped_column(String(100))
    device_timestamp: Mapped[datetime] = mapped_column()
    record_type: Mapped[int] = mapped_column(Integer)

    glucose_value_history: Mapped[int] = mapped_column(Integer, nullable=True)
    glucose_scan: Mapped[float] = mapped_column(Float, nullable=True)

    non_numeric_fast_insulin: Mapped[str] = mapped_column(Text, nullable=True)
    fast_insulin_units: Mapped[float] = mapped_column(Float, nullable=True)

    non_numeric_food: Mapped[str] = mapped_column(Text, nullable=True)
    carbs_grams: Mapped[float] = mapped_column(Float, nullable=True)
    carbs_portions: Mapped[float] = mapped_column(Float, nullable=True)

    non_numeric_long_insulin: Mapped[str] = mapped_column(Text, nullable=True)
    long_insulin_units: Mapped[float] = mapped_column(Float, nullable=True)

    notes: Mapped[str] = mapped_column(Text, nullable=True)
    glucose_teststrip: Mapped[float] = mapped_column(Float, nullable=True)
    ketone: Mapped[float] = mapped_column(Float, nullable=True)

    meal_insulin: Mapped[float] = mapped_column(Float, nullable=True)
    correction_insulin: Mapped[float] = mapped_column(Float, nullable=True)
    insulin_change_by_user: Mapped[float] = mapped_column(Float, nullable=True)

    @staticmethod
    def convert_item_to_db_model(item, user_id: str):
        return UserGlucoseData(
            user_id=user_id,
            device=item.Gerät,
            serial_number=item.Seriennummer,
            device_timestamp=item.Gerätezeitstempel,
            record_type=item.Aufzeichnungstyp,
            glucose_value_history=item.Glukosewert_Verlauf_mg_dL,
            glucose_scan=item.Glukose_Scan_mg_dL,
            non_numeric_fast_insulin=item.Nicht_numerisches_schnellwirkendes_Insulin,
            fast_insulin_units=item.Schnellwirkendes_Insulin_Einheiten,
            non_numeric_food=item.Nicht_numerische_Nahrungsdaten,
            carbs_grams=item.Kohlenhydrate_Gramm,
            carbs_portions=item.Kohlenhydrate_Portionen,
            non_numeric_long_insulin=item.Nicht_numerisches_Depotinsulin,
            long_insulin_units=item.Depotinsulin_Einheiten,
            notes=item.Notizen,
            glucose_teststrip=item.Glukose_Teststreifen_mg_dL,
            ketone=item.Keton_mmol_L,
            meal_insulin=item.Mahlzeiteninsulin_Einheiten,
            correction_insulin=item.Korrekturinsulin_Einheiten,
            insulin_change_by_user=item.Insulin_Änderung_durch_Anwender_Einheiten,
        )
