from datetime import date, datetime

from pydantic import BaseModel


class MetadataResponse(BaseModel):
    source: str
    region: str
    year: int
    source_updated_at: datetime
    observed_through: date
    first_observed_week: int
    last_observed_week: int
    observed_weeks: int
    historical_start_year: int
    historical_end_year: int
    limitations: list[str]