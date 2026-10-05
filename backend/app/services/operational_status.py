from backend.app.repositories.epidemiological import (
    EpidemiologicalRepository,
)


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

        df = df.sort_values("epi_week")

        return [
            {
                "epi_week": int(row.epi_week),
                "has_signal": bool(row.has_signal),
                "operational_state": (
                    row.operational_state
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