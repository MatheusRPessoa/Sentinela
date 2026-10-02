from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

SOURCE_UPDATED_AT = datetime.fromisoformat(
    "2026-09-28T00:47:00-03:00"
)

def get_metadata(region: str, year: int) -> dict | None:
    region = region.strip().upper()

    if region != "MG" or year != 2026:
        return None

    file_path = (
        PROCESSED_DATA_DIR
        / "srag_2026_mg_weekly_coverage.csv"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo de cobertura não encontrado: {file_path}"
        )
    
    df = pd.read_csv(file_path, sep=";")

    required_columns = {
        "epi_week",
        "epi_year",
        "week_start",
        "week_end",
        "record_count",
        "calendar_status",
        "data_status",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Colunas obrigatórias ausentes: "
            f"{sorted(missing_columns)}"
        )

    df = df.loc[df["epi_year"].eq(year)].copy()

    observed = df.loc[
        df["data_status"].eq("observado")
    ].copy()

    if observed.empty:
        raise ValueError(
            "Nenhuma semana observada encontrada."
        )

    observed = observed.sort_values("epi_week")

    last_observed = observed.iloc[-1]

    return {
        "source": "OpenDataSUS",
        "region": region,
        "year": year,
        "source_updated_at": SOURCE_UPDATED_AT,
        "observed_through": last_observed["week_end"],
        "first_observed_week": int(
            observed["epi_week"].min()
        ),
        "last_observed_week": int(
            observed["epi_week"].max()
        ),
        "observed_weeks": int(
            observed["epi_week"].nunique()
        ),
        "limitations": [
            (
                "Semanas sem cobertura confirmada não são "
                "tratadas como zero."
            ),
            (
                "Um sinal estatístico não representa "
                "confirmação de surto."
            ),
            (
                "A referência histórica utiliza os anos "
                "de 2019 a 2025."
            ),
        ],
    }