from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.trend import TrendResponse
from backend.app.dependencies import TrendsServiceDep

router = APIRouter(
    prefix="/api/trends",
    tags=["trends"],
)

@router.get("", response_model=TrendResponse)
def read_trends(
    service: TrendsServiceDep,
    region: str = Query(..., min_length=2, max_length=2),
    year: int = Query(..., ge=2019, le=2100),
):
    normalized_region = region.strip().upper()

    try:
        weeks = service.get_trends(
            region=normalized_region,
            year=year,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    if not weeks:
        raise HTTPException(
            status_code=404,
            detail=(
                "Dados não encontrados para "
                f"{normalized_region}/{year}."
            ),
        )

    return TrendResponse(
        region=normalized_region,
        year=year,
        weeks=weeks,
    )
