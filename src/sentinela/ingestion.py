from collections.abc import Iterator
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "NU_NOTIFIC",
    "SG_UF",
    "SG_UF_NOT",
    "DT_SIN_PRI",
    "SEM_PRI",
    "DT_NOTIFIC",
    "CLASSI_FIN",
    "HOSPITAL",
    "EVOLUCAO",
]

def read_srag_chunks(
    csv_path: Path,
    chunk_size: int = 50_000,
) -> Iterator[pd.DataFrame]:
    if not csv_path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    if chunk_size <= 0:
        raise ValueError("O tamanho dos blocos deve ser positivo")

    header = pd.read_csv(
        csv_path,
        sep=";",
        encoding="utf-8-sig",
        nrows=0,
    )

    missing_columns = sorted(
        set(REQUIRED_COLUMNS) - set(header.columns)
    )

    if missing_columns:
        raise ValueError(f"Campos ausentes: {missing_columns}")

    yield from pd.read_csv(
        csv_path,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        usecols=REQUIRED_COLUMNS,
        chunksize=chunk_size,
    )
