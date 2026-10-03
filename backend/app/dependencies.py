from typing import Annotated

from fastapi import Depends

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)
from backend.app.services.metadata import MetadataService
from backend.app.services.signals import SignalsService
from backend.app.services.trends import TrendsService


def get_epidemiological_repository() -> EpidemiologicalRepository:
    return EpidemiologicalRepository()


RepositoryDep = Annotated[
    EpidemiologicalRepository,
    Depends(get_epidemiological_repository),
]


def get_trends_service(
    repository: RepositoryDep,
) -> TrendsService:
    return TrendsService(repository)


def get_signals_service(
    repository: RepositoryDep,
) -> SignalsService:
    return SignalsService(repository)


def get_metadata_service(
    repository: RepositoryDep,
) -> MetadataService:
    return MetadataService(repository)


TrendsServiceDep = Annotated[
    TrendsService,
    Depends(get_trends_service),
]

SignalsServiceDep = Annotated[
    SignalsService,
    Depends(get_signals_service),
]

MetadataServiceDep = Annotated[
    MetadataService,
    Depends(get_metadata_service),
]