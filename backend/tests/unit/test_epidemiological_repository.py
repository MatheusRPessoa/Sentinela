from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)


def test_dataset_exists_returns_true_for_available_dataset():
    repository = EpidemiologicalRepository()

    result = repository.dataset_exists(
        region="MG",
        year=2026,
    )

    assert result is True


def test_dataset_exists_normalizes_region():
    repositories = EpidemiologicalRepository()

    result = repositories.dataset_exists(
        region="mg",
        year=2026,
    )

    assert result is True

def test_dataset_exists_returns_false_for_unavailable_region():
    repository = EpidemiologicalRepository()

    result = repository.dataset_exists(
        region="SP",
        year=2026,
    )

    assert result is False

def test_dataset_exists_returns_false_for_unavailable_year():
    repository = EpidemiologicalRepository()

    result = repository.dataset_exists(
        region="MG",
        year=2024,
    )

    assert result is False
