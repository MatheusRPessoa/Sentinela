from typing import Literal

from pydantic import BaseModel


OperationalState = Literal[
    "NORMAL",
    "SIGNAL",
    "ALERT",
]


class OperationalWeek(BaseModel):
    epi_week: int
    has_signal: bool
    operational_state: OperationalState
    consecutive_signals: int
    consecutive_no_signals: int


class OperationalStatusResponse(BaseModel):
    region: str
    year: int
    weeks: list[OperationalWeek]
