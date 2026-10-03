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

        regions = sorted(
            {
                region
                for region, _ in datasets
            }
        )

        years = sorted(
            {
                year
                for _, year in datasets
            },
            reverse=True,
        )

        return {
            "regions": [
                {
                    "value": region,
                    "label": REGION_LABELS.get(
                        region,
                        region,
                    )
                }
                for region in regions
            ],
            "years": years,
        }
