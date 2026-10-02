from datetime import date

from pydantic import BaseModel

class Signal(BaseModel):
    epi_week: int
    week_start: date
    week_end: date
    record_count: float | None
    historical_median: float | None
    q75: float | None
    median_threshold: float | None
    ratio_to_median: float | None
    historical_years: int
    data_status: str
    signal_status: str
    signal_reason: str

class SignalResponse(BaseModel):
    region: str
    year: int
    signals: list[Signal]
