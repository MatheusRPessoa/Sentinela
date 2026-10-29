from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from sentinela.config import (
    ALGORITHM_VERSION,
    REGIONS,
)

from sentinela.transformation import (
    build_flu_weekly_for_state_year,
)

from sentinela.readiness import (
    calculate_readiness,
)

from sentinela.validation import (
    validate_weekly_environment,
)


@dataclass
class SentinelaEnvironment:
    source_path: Path
    epi_year: int
    algorithm_version: str

    weekly: dict[str, pd.DataFrame]

    readiness_grid: pd.DataFrame
    readiness_summary: pd.DataFrame

    latest_ready_week: int | None


def prepare_sentinela_environment(
    influd_path: Path,
    year: int,
) -> SentinelaEnvironment:

    influd_path = Path(
        influd_path
    ).resolve()

    if not influd_path.exists():
        raise FileNotFoundError(
            influd_path
        )

    print("=" * 60)
    print("SENTINELA — BOOTSTRAP")
    print("=" * 60)

    print(
        f"Fonte: {influd_path.name}"
    )

    print(
        f"Ano: {year}"
    )

    print(
        f"Algoritmo: "
        f"{ALGORITHM_VERSION}"
    )

    weekly = {}

    for region in REGIONS:

        state_weekly = (
            build_flu_weekly_for_state_year(
                path=influd_path,
                region=region,
                year=year,
            )
        )

        if state_weekly.empty:
            raise RuntimeError(
                f"{region}: série vazia"
            )

        weekly[region] = (
            state_weekly
        )

    (
        readiness_grid,
        readiness_summary,
        latest_ready_week,
    ) = calculate_readiness(
        weekly
    )

    print(
        f"UFs processadas: "
        f"{len(weekly)}"
    )

    validate_weekly_environment(
        weekly_by_region=weekly,
        expected_regions=REGIONS,
        year=year,
    )

    print(
        "✓ Validação estrutural concluída"
    )

    print(
        "Última semana READY:",
        latest_ready_week,
    )

    print(
        "✓ Ambiente preparado"
    )

    return SentinelaEnvironment(
        source_path=influd_path,
        epi_year=year,
        algorithm_version=
            ALGORITHM_VERSION,
        weekly=weekly,
        readiness_grid=
            readiness_grid,
        readiness_summary=
            readiness_summary,
        latest_ready_week=
            latest_ready_week,
    )
