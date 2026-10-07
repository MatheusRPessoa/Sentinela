from typing import Literal

from pydantic import BaseModel


OperationalState = Literal[
    "NORMAL",
    "SIGNAL",
    "ALERT",
    "PENDING",
]


class OperationalWeek(BaseModel):
    epi_week: int
    is_mature: bool
    has_signal: bool | None
    operational_state: OperationalState
    last_stable_state: Literal[
        "NORMAL",
        "SIGNAL",
        "ALERT",
    ]
    consecutive_signals: int
    consecutive_no_signals: int


class OperationalStatusResponse(BaseModel):
    region: str
    year: int
    weeks: list[OperationalWeek]
