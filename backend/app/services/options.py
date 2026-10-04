from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)


REGION_LABELS = {
    "MG": "Minas Gerais",
}


class OptionsService:
    def __init__(
        self,
        repository: EpidemiologicalRepository,
    ):
        self.repository = repository

    def get_options(self) -> dict:
        datasets = self.repository.get_available_datasets()

        regions_with_years: dict[str, set[int]] = {}

        for region, year in datasets:
            regions_with_years.setdefault(
                region,
                set(),
            ).add(year)

        return {
            "regions": [
                {
                    "value": region,
                    "label": REGION_LABELS.get(
                        region,
                        region,
                    ),
                    "years": sorted(
                        years,
                        reverse=True,
                    ),
                }
                for region, years in sorted(
                    regions_with_years.items()
                )
            ],
        }
