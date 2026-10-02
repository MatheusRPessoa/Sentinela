from pydantic import BaseModel


class TrendWeek(BaseModel):
    epi_week: int
    record_count: int
    historical_median: float
    q25: float
    q75: float


class TrendResponse(BaseModel):
    region: str
    year: int
    weeks: list[TrendWeek]