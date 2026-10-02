from fastapi import APIRouter, HTTPException, Query

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)
from backend.app.schemas.signal import SignalResponse
from backend.app.services.signals import SignalsService

router = APIRouter(
    prefix="/api/signals",
    tags=["signals"],
)

repository = EpidemiologicalRepository()
service = SignalsService(repository)

@router.get("", response_model=SignalResponse)
def read_signals(
    region: str = Query(..., min_length=2, max_length=2),
    year: int = Query(..., ge=2019, le=2100),
):
    normalized_region = region.strip().upper()

    try:
        signals = service.get_signals(
            region=normalized_region,
            year=year,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return SignalResponse(
        region=normalized_region,
        year=year,
        signals=signals,
    )
