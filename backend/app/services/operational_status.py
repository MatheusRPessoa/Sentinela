import pandas as pd

from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)

def parse_optional_bool(value):
    if pd.isna(value):
        return None
    
    normalized = str(value).strip().lower()

    if normalized == "true":
        return True
    
    if normalized == "false":
        return False

    return None


class OperationalStatusService:
    def __init__(
        self,
        repository: EpidemiologicalRepository,
    ):
        self.repository = repository

    def get_operational_status(
        self,
        region: str,
        year: int,
    ) -> list[dict]:
        region = region.strip().upper()

        if not self.repository.dataset_exists(
            region=region,
            year=year,
        ):
            return []

        df = self.repository.get_operational_status(
            region=region,
            year=year,
        )

        required_columns = {
            "epi_week",
            "has_signal",
            "operational_state",
            "consecutive_signals",
            "consecutive_no_signals",
        }

        missing_columns = (
            required_columns
            - set(df.columns)
        )

        if missing_columns:
            raise ValueError(
                "Colunas obrigatórias ausentes no "
                "estado operacional: "
                f"{sorted(missing_columns)}"
            )

        if "is_mature" not in df.columns:
            df["is_mature"] = True
        
        if "last_stable_state" not in df.columns:
            df["last_stable_state"] = (
                df["operational_state"]
            ) 

        df["has_signal"] = (
            df["has_signal"]
            .apply(parse_optional_bool)
        )

        df["is_madure"] = (
            df["is_mature"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("true")
        )

        df = df.sort_values("epi_week")

        return [
            {
                "epi_week": int(row.epi_week),
                "is_mature": bool(
                    row.is_mature
                ),
                "has_signal": row.has_signal,
                "operational_state": (
                    row.operational_state
                ),
                "last_stable_state": (
                    row.last_stable_state
                ),
                "consecutive_signals": int(
                    row.consecutive_signals
                ),
                "consecutive_no_signals": int(
                    row.consecutive_no_signals
                ),
            }
            for row in df.itertuples(
                index=False
            )
        ]