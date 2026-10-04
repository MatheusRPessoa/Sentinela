from pydantic import BaseModel


class TrendWeek(BaseModel):
    epi_week: int
    record_count: int
    historical_median: float | None
    q25: float | None
    q75: float | None


class TrendResponse(BaseModel):
    region: str
    year: int
    weeks: list[TrendWeek]