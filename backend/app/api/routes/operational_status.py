from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)
from backend.app.schemas.operational_status import (
    OperationalStatusResponse,
)
from backend.app.services.operational_status import (
    OperationalStatusService,
)

router = APIRouter(
    prefix="/api/status",
    tags=["status"],
)


@router.get(
    "",
    response_model=OperationalStatusResponse,
)
def read_operational_status(
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
    normalized_region = (
        region.strip().upper()
    )

    repository = EpidemiologicalRepository()

    service = OperationalStatusService(
        repository
    )

    try:
        weeks = service.get_operational_status(
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
                "Estado operacional não encontrado para "
                f"{normalized_region}/{year}."
            ),
        )

    return OperationalStatusResponse(
        region=normalized_region,
        year=year,
        weeks=weeks,
    )
