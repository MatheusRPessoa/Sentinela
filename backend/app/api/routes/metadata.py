from fastapi import APIRouter, HTTPException, Query

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)
from backend.app.schemas.metadata import MetadataResponse
from backend.app.services.metadata import MetadataService


router = APIRouter(
    prefix="/api/metadata",
    tags=["metadata"],
)

repository = EpidemiologicalRepository()
service = MetadataService(repository)

@router.get("", response_model=MetadataResponse)
def read_metadata(
    region: str = Query(..., min_length=2, max_length=2),
    year: int = Query(..., ge=2019, le=2100),
):
    normalized_region = region.strip().upper()

    try:
        metadata = service.get_metadata(
            region=normalized_region,
            year=year,
       )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    if not metadata:
        raise HTTPException(
            status_code=404,
            detail=(
                "Metadados não encontrados para "
                f"{normalized_region}/{year}."
            ),
        )
    return MetadataResponse(**metadata)
