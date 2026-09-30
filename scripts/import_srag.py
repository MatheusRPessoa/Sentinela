import json
from datetime import datetime, timezone

import argparse
from pathlib import Path

from collections import Counter

from sentinela.validation import validate_dates
from sentinela.storage import export_srag_csv

from sentinela.ingestion import (
    filter_by_residence,
    read_srag_chunks,
)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Confere a leitura de um CSV de SRAG."
    )

    parser.add_argument(
        "csv_path",
        type=Path,
        help="Caminho do arquivo CSV.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=50_000,
        help="Quantidade de linhas por bloco.",
    )

    parser.add_argument(
        "--expected-rows",
        type=int,
        help="Total esperado de linhas para esta versão do arquivo.",
    )

    parser.add_argument(
        "--uf",
        required=True,
        help="UF de residência a selecionar, por exemplo MG."
    )

    parser.add_argument(
        "--expected-selected-rows",
        type=int,
        help="Total esperado de linhas para a UF selecionada.",
    )

    parser.add_argument(
        "--report",
        type=Path,
        help="Caminho para salvar relatório JSON da execução.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Caminho para exportar os registros selecionados.",
    )

    args = parser.parse_args()

    if args.output is not None and args.report is not None:
        if args.output.resolve() == args.report.resolve():
            parser.error("CSV e relatório devem ter caminhos diferentes.")

    total_rows = 0
    total_chunks = 0
    selected_rows = 0
    date_issues = Counter()

    for chunk in read_srag_chunks(
        args.csv_path,
        chunk_size=args.chunk_size,
    ):
        total_rows += len(chunk)
        total_chunks += 1

        selected = filter_by_residence(chunk, args.uf)
        selected_rows += len(selected)

        _, chunk_issues = validate_dates(selected)
        date_issues.update(chunk_issues)

    print(f"Arquivo: {args.csv_path.name}")
    print(f"Blocos lidos: {total_chunks}")
    print(f"Total de linhas: {total_rows}")
    print(f"UF de residência: {args.uf.strip().upper()}")
    print(f"Linhas selecionadas: {selected_rows}")

    if args.expected_rows is not None:
        if total_rows != args.expected_rows:
            raise SystemExit(
                "Contagem diferente da esperada: "
                f"esperado={args.expected_rows}, "
                f"encontrado={total_rows}."
            )

        print("Contagem esperada confirmada.")

    if args.expected_selected_rows is not None:
        if selected_rows != args.expected_selected_rows:
            raise SystemExit(
                "Contagem da UF diferente da esperada: "
                f"esperado={args.expected_selected_rows}, "
                f"encontrado={selected_rows}"
            )

        print("Contagem de UF confirmada")

    print("\nValidação das datas:")

    for issue, quantity in sorted(date_issues.items()):
        print(f"{issue}: {quantity}")

    if args.report is not None:
        if args.report.resolve() == args.csv_path.resolve():
            raise SystemExit(
                "O relatório não pode substituir o arquivo original."
            )


        report = {
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "source_file": args.csv_path.name,
            "source_size_bytes": args.csv_path.stat().st_size,
            "residence_uf": args.uf.strip().upper(),
            "total_rows": total_rows,
            "selected_rows": selected_rows,
            "chunks_read": total_chunks,
            "expected_rows": args.expected_rows,
            "expected_selected_rows": args.expected_selected_rows,
            "date_validation": dict(date_issues),
        }

        args.report.parent.mkdir(parents=True, exist_ok=True)

        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        print(f"\nRelatório salvo: {args.report}")


    if args.output is not None:
        exported_rows = export_srag_csv(
            source_path=args.csv_path,
            output_path=args.output,
            uf=args.uf,
            chunk_size=args.chunk_size,
            expected_rows=selected_rows,
        )

        print(f"CSV salvo: {args.output}")
        print(f"Linhas exportadas: {exported_rows}")

if __name__ == "__main__":
    main()
