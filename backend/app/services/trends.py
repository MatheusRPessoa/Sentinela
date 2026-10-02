from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def get_trends(region: str, year: int) -> list[dict]:
    region = region.strip().upper()

    if region != "MG" or year != 2026:
        return []

    weekly_path = (
        PROCESSED_DATA_DIR
        / "srag_2026_mg_weekly.csv"
    )

    reference_path = (
        PROCESSED_DATA_DIR
        / "srag_mg_historical_reference_2019_2025.csv"
    )

    if not weekly_path.exists():
        raise FileNotFoundError(
            f"Arquivo semanal não encontrado: {weekly_path}"
        )

    if not reference_path.exists():
        raise FileNotFoundError(
            f"Referência histórica não encontrada: {reference_path}"
        )

    weekly = pd.read_csv(weekly_path, sep=";")
    reference = pd.read_csv(reference_path, sep=";")

    weekly_required = {
        "epi_week",
        "record_count",
    }

    reference_required = {
        "epi_week",
        "historical_median",
        "q25",
        "q75",
    }

    missing_weekly = weekly_required - set(weekly.columns)
    missing_reference = reference_required - set(reference.columns)

    if missing_weekly:
        raise ValueError(
            "Colunas ausentes na série semanal: "
            f"{sorted(missing_weekly)}"
        )

    if missing_reference:
        raise ValueError(
            "Colunas ausentes na referência histórica: "
            f"{sorted(missing_reference)}"
        )

    if weekly["epi_week"].duplicated().any():
        raise ValueError(
            "A série semanal contém semanas duplicadas."
        )

    if reference["epi_week"].duplicated().any():
        raise ValueError(
            "A referência histórica contém semanas duplicadas."
        )

    trends = weekly.merge(
        reference[
            [
                "epi_week",
                "historical_median",
                "q25",
                "q75",
            ]
        ],
        on="epi_week",
        how="left",
        validate="one_to_one",
    )

    historical_columns = [
        "historical_median",
        "q25",
        "q75",
    ]

    if trends[historical_columns].isna().any().any():
        raise ValueError(
            "Existem semanas observadas sem referência histórica."
        )

    trends = trends.sort_values("epi_week")

    return [
        {
            "epi_week": int(row.epi_week),
            "record_count": int(row.record_count),
            "historical_median": float(row.historical_median),
            "q25": float(row.q25),
            "q75": float(row.q75),
        }
        for row in trends.itertuples(index=False)
    ]