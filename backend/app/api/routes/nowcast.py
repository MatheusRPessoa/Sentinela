from fastapi import APIRouter, HTTPException, Query

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)
from backend.app.schemas.nowcast import (
    NowcastResponse,
)
from backend.app.services.nowcast import (
    NowcastService,
)


router = APIRouter(
    prefix="/api/nowcast",
    tags=["nowcast"],
)


@router.get(
    "",
    response_model=NowcastResponse,
)
def read_nowcast(
    region: str = Query(
        ...,
        min_length=2,
        max_length=2,
    ),
    year: int = Query(
        ...,
        ge=2019,
        le=2100,
    ),
):
    normalized_region = region.strip().upper()

    repository = EpidemiologicalRepository()

    service = NowcastService(
        repository
    )

    try:
        weeks = service.get_nowcast(
            region=normalized_region,
            year=year,
        )
    except (
        FileNotFoundError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    if not weeks:
        raise HTTPException(
            status_code=404,
            detail=(
                "Nowcast não encontrado para "
                f"{normalized_region}/{year}."
            ),
        )

    return NowcastResponse(
        region=normalized_region,
        year=year,
        weeks=weeks,
    )
