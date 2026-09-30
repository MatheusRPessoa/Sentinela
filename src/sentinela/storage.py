from pathlib import Path
from tempfile import TemporaryDirectory

from sentinela.ingestion import filter_by_residence, read_srag_chunks
from sentinela.validation import validate_dates
from sentinela.transformation import add_epidemiological_week_2026

def export_srag_csv(
    source_path: Path,
    output_path: Path,
    uf: str,
    chunk_size: int = 50_000,
    expected_rows: int | None = None,
) -> int:
    if source_path.resolve() == output_path.resolve():
        raise ValueError("A saída não pode substituir a fonte.")
    if output_path.exists():
        raise FileExistsError(f"A saída já existe: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    exported_rows = 0
    first_write =True

    with TemporaryDirectory(
        dir=output_path.parent,
        prefix="srag_export_",
    ) as temporary_directory:
        temporary_path = Path(temporary_directory) / "records.csv"

        for chunk in read_srag_chunks(source_path, chunk_size):
            selected = filter_by_residence(chunk, uf)
            validated, _ = validate_dates(selected)
            transformed = add_epidemiological_week_2026(validated)

            transformed.to_csv(
                temporary_path,
                sep=";",
                index=False,
                encoding="utf-8",
                mode="w" if first_write else "a",
                header=first_write,
            )

            exported_rows += len(validated)
            first_write = False


        if first_write:
            raise ValueError("A leitura não produziu blocos para exportar.")


        if expected_rows is not None and exported_rows != expected_rows:
            raise ValueError(
                "Contagem exportada diferente da esperada: "
                f"esperado={expected_rows}, encontrado={exported_rows}."
            )

        temporary_path.replace(output_path)


    return exported_rows
