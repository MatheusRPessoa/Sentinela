from backend.app.services.options import OptionsService


class FakeEpidemiologicalRepository:
    def get_available_datasets(
        self,
    ) -> list[tuple[str, int]]:
        return [
            ("MG", 2026),
            ("MG", 2025),
            ("SP", 2026),
        ]


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
                "label": "SP",
                "years": [
                    2026,
                ],
            },
        ],
    }


class EmptyEpidemiologicalRepository:
    def get_available_datasets(
        self,
    ) -> list[tuple[str, int]]:
        return []


def test_get_options_returns_empty_options_when_no_dataset_exists():
    repository = EmptyEpidemiologicalRepository()
    service = OptionsService(repository)

    result = service.get_options()

    assert result == {
        "regions": [],
    }
