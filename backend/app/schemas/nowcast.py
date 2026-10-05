from datetime import date

from pydantic import BaseModel

class NowcastWeek(BaseModel):
    epi_week: int
    lag_days: int
    snapshot_date: date
    known_cases: int
    nowcast: float
    q75: float
    median_threshold: float
    would_signal: bool


class NowcastResponse(BaseModel):
    region: str
    year: int
    weeks: list[NowcastWeek]
