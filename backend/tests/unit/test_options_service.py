from backend.app.services.options import OptionsService


class FakeEpidemiologicalRepository:
    def dataset_exists(
        self,
        region: str,
        year: int,
    ) -> bool:
        available = {
            ("MG", 2025),
            ("MG", 2026),
            ("SP", 2026),
        }

        return (
            region.upper(),
            year,
        ) in available

def test_get_options_from_available_datasets():
    repository = FakeEpidemiologicalRepository()
    service = OptionsService(repository)

    result = service.get_options()

    assert result == {
        "regions": [
            {
                "value": "MG",
                "label": "Minas Gerais",
                "years": [
                    2026,
                    2025,
                ],
            },
            {
                "value": "SP",
                "label": "São Paulo",
                "years": [
                    2026,
                ],
            },
        ],
    }


class EmptyEpidemiologicalRepository:
    def dataset_exists(
        self,
        region: str,
        year: int,
    ) -> bool:
        _ = region, year
        return False

def test_get_options_returns_empty_options_when_no_dataset_exists():
    repository = EmptyEpidemiologicalRepository()
    service = OptionsService(repository)

    result = service.get_options()

    assert result == {
        "regions": [],
    }
