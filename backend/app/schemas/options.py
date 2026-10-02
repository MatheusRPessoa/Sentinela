from pydantic import BaseModel

class RegionOption(BaseModel):
    value: str
    label: str

class OptionsResponse(BaseModel):
    regions: list[RegionOption]
    years: list[int]
