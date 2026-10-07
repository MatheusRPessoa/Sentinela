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
        region = region.strip().lower()

        path = (
            PROCESSED_DATA_DIR
            / f"srag_{year}_{region}_weekly.csv"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo semanal não encontrado: {path}"
            )

        return pd.read_csv(path, sep=";")

    def get_historical_reference(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        historical_end_year = year - 1
        region = region.strip().lower()

        path = ( 
            PROCESSED_DATA_DIR
            / (
                f"srag_{region}_"
                f"historical_reference_2019_{historical_end_year}.csv"
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
        region = region.strip().lower()

        path = (
            PROCESSED_DATA_DIR
            / f"srag_{year}_{region}_signal_evaluation.csv"
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
        region = region.strip().lower()

        path = (
            PROCESSED_DATA_DIR
            / f"srag_{year}_{region}_weekly_coverage.csv"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo de cobertura não encontrado: {path}"
            )

        return pd.read_csv(path, sep=";")

    def get_available_datasets(
        self,
    ) -> list[tuple[str, int]]:
        pattern = "srag_*_*_signal_evaluation.csv"

        datasets: list[tuple[str, int]] = []

        for path in PROCESSED_DATA_DIR.glob(pattern):
            parts = path.stem.split("_")

            if len(parts) < 5:
                continue

            try:
                year = int(parts[1])
            except ValueError:
                continue

            region = parts[2].upper()


            weekly_path = (
                PROCESSED_DATA_DIR
                / f"srag_{year}_{region.lower()}_weekly.csv"
            )

            coverage_path = (
                PROCESSED_DATA_DIR
                / f"srag_{year}_{region.lower()}_weekly_coverage.csv"
            )

            if not weekly_path.exists():
                continue

            if not coverage_path.exists():
                continue

            datasets.append((region, year))

        return sorted(set(datasets))

    def dataset_exists(
        self,
        region: str,
        year: int,
    ) -> bool:
        region = region.strip().lower()

        path = (
            PROCESSED_DATA_DIR
            / f"srag_{year}_{region}_weekly_coverage.csv"
        )

        return path.exists()

    def get_nowcast(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        region = region.strip().lower()

        path = (
            PROCESSED_DATA_DIR
            / f"srag_{year}_{region}_nowcast.csv"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo de nowcast não encontrado: {path}"
            )

        return pd.read_csv(
            path,
            sep=";",
        )

    def get_operational_status(
        self,
        region: str,
        year: int,
    ) -> pd.DataFrame:
        region = region.strip().lower()

        path = (
            PROCESSED_DATA_DIR
            / f"srag_{year}_{region}_operational_status.csv"
        )

        if not path.exists():
            raise FileNotFoundError(
                "Arquivo de estado operacional "
                f"não encontrado: {path}"
        )

        return pd.read_csv(
            path,
            sep=";",
        )