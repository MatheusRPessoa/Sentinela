from fastapi import APIRouter

from backend.app.schemas.options import OptionsResponse
from backend.app.services.options import get_available_options

router = APIRouter(
    prefix="/api/options",
    tags=["options"],
)

@router.get("", response_model=OptionsResponse)
def read_options():
    return get_available_options()
