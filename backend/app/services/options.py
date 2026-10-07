from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)


REGION_LABELS = {
    "MG": "Minas Gerais",
    "SP": "São Paulo",
}


class OptionsService:
    def __init__(
        self,
        repository: EpidemiologicalRepository,
    ):
        self.repository = repository

    def get_options(self) -> dict:
        regions = []

        for region, label in REGION_LABELS.items():
            years = [
                year
                for year in range(2019, 2027)
                if self.repository.dataset_exists(
                    region=region,
                    year=year,
                )
            ]

            if not years:
                continue

            regions.append(
                {
                    "value": region,
                    "label": label,
                    "years": sorted(
                        years,
                        reverse=True,
                    ),
                }
            )

        return {
            "regions": regions,
        }
