from fastapi import APIRouter

from backend.app.schemas.options import OptionsResponse
from backend.app.dependencies import OptionsServiceDep

router = APIRouter(
    prefix="/api/options",
    tags=["options"],
)

@router.get("", response_model=OptionsResponse)
def read_options(
    service: OptionsServiceDep,
):
    options = service.get_options()

    return OptionsResponse(**options)
