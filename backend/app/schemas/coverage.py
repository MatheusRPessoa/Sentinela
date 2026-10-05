from pydantic import BaseModel


class CoverageWeek(BaseModel):
    epi_week: int
    week_start: str
    week_end: str
    record_count: int | None
    calendar_status: str
    data_status: str


class CoverageResponse(BaseModel):
    region: str
    year: int
    weeks: list[CoverageWeek]
