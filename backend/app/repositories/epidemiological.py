from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


class EpidemiologicalRepository:
    def get_weekly(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        path = (
            PROCESSED_DATA_DIR
            / f"srag_{year}_{region.lower()}_weekly.csv"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo semanal não encontrado: {path}"
            )

        return pd.read_csv(path, sep=";")

    def get_historical_reference(
        self,
        region: str,
    ) -> pd.DataFrame:
        # Por enquanto nossa referência disponível é 2019–2025.
        path = (
            PROCESSED_DATA_DIR
            / (
                f"srag_{region.lower()}_"
                "historical_reference_2019_2025.csv"
            )
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Referência histórica não encontrada: {path}"
            )

        return pd.read_csv(path, sep=";")

    def get_signal_evaluation(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        path = (
            PROCESSED_DATA_DIR
            / f"srag_{year}_{region.lower()}_signal_evaluation.csv"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo de avaliação de sinais não encontrado: {path}"
            )

        return pd.read_csv(path, sep=";")

    def get_coverage(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        path = (
            PROCESSED_DATA_DIR
            / f"srag_{year}_{region.lower()}_weekly_coverage.csv"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo de cobertura não encontrado: {path}"
            )

        return pd.read_csv(path, sep=";")
