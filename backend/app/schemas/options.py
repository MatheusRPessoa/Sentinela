from pydantic import BaseModel

class RegionOption(BaseModel):
    value: str
    label: str
    years: list[int]

class OptionsResponse(BaseModel):
    regions: list[RegionOption]
