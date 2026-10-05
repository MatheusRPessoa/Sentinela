from fastapi import APIRouter, HTTPException, Query

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)
from backend.app.schemas.coverage import CoverageResponse
from backend.app.services.coverage import CoverageService


router = APIRouter(
    prefix="/api/coverage",
    tags=["coverage"],
)

repository = EpidemiologicalRepository()
service = CoverageService(repository)

@router.get("", response_model=CoverageResponse)
def read_coverage(
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

    try:
        weeks = service.get_coverage(
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
                "Dados de cobertura não encontrados para "
                f"{normalized_region}/{year}."
            ),
        )
    
    return CoverageResponse(
        region=normalized_region,
        year=year,
        weeks=weeks,
    )
