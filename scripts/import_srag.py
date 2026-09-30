import json
import pandas as pd
from datetime import datetime, timezone

import argparse
from pathlib import Path

from collections import Counter

from sentinela.validation import (
    collect_record_issues,
    validate_calendar, 
    validate_dates,
)
from sentinela.transformation import add_epidemiological_week_2026
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

    parser.add_argument(
        "--issues-output",
        type=Path,
        help="Caminho do CSV de problemas identificados.",
    )

    args = parser.parse_args()

    if args.output is not None:
        if args.output.resolve() == args.csv_path.resolve():
            parser.error("O CSV de saída não pode substituir a fonte.")

    if args.report is not None:
        if args.report.resolve() == args.csv_path.resolve():
            parser.error("O relatório não pode substituir a fonte.")

    if args.output is not None and args.report is not None:
        if args.output.resolve() == args.report.resolve():
            parser.error("CSV e relatório devem ter caminhos diferentes.")

    if args.issues_output is not None:
        protected_paths = [
            args.csv_path,
            args.output,
            args.report,
        ]

        for path in protected_paths:
            if path is not None:
                if args.issues_output.resolve() == path.resolve():
                    parser.error(
                        "O arquivo de problemas deve ter um caminho "
                        "diferente da fonte, do CSV e do relatório."
                    )

        if args.issues_output.exists():
            parser.error("O arquivo de problemas já existe.")

    total_rows = 0
    total_chunks = 0
    selected_rows = 0
    date_issues = Counter()
    calendar_issues = Counter()
    issue_parts = []

    for chunk in read_srag_chunks(
        args.csv_path,
        chunk_size=args.chunk_size,
    ):
        total_rows += len(chunk)
        total_chunks += 1

        selected = filter_by_residence(chunk, args.uf)
        selected_rows += len(selected)

        validated, chunk_issues = validate_dates(selected)
        date_issues.update(chunk_issues)

        transformed = add_epidemiological_week_2026(validated)
        issue_parts.append(collect_record_issues(transformed))
        calendar_issues.update(validate_calendar(transformed))

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

    export_result = None

    if args.output is not None:
        exported_rows = export_srag_csv(
            source_path=args.csv_path,
            output_path=args.output,
            uf=args.uf,
            chunk_size=args.chunk_size,
            expected_rows=selected_rows,
        )

        export_result = {
            "status": "completed",
            "output_file": args.output.name,
            "exported_rows": exported_rows,
            "output_size_bytes": args.output.stat().st_size,
            "derived_columns": [
                "DT_SIN_PRI_PARSED",
                "DT_NOTIFIC_PARSED",
                "EPI_YEAR_CALCULATED",
                "EPI_WEEK_CALCULATED",
                "RESIDENCE_UF_NORMALIZED",
            ],
        }

        print(f"CSV salvo: {args.output}")
        print(f"Linhas exportadas: {exported_rows}")

    record_issues = (
        pd.concat(issue_parts, ignore_index=True)
        if issue_parts
        else pd.DataFrame(columns=[
            "source_record_number",
            "field",
            "issue_code",
        ])
    )
    
    issues_result = {
        "occurrences": len(record_issues),
        "affected_records": int(
            record_issues["source_record_number"].nunique()
        ),
        "by_code": {
            str(code): int(quantity)
            for code, quantity in
            record_issues["issue_code"].value_counts().items()
        },
        "output_file": None,
        "records_removed": 0,
    }

    if args.issues_output is not None:
        args.issues_output.parent.mkdir(parents=True, exist_ok=True)

        record_issues.to_csv(
            args.issues_output,
            sep=";",
            index=False,
            encoding="utf-8",
        )

        issues_result["output_file"] = args.issues_output.name
        print(f"Problemas registrados: {args.issues_output}")

    if args.report is not None:
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
            "calendar_validation": dict(calendar_issues),
            "calendar_transformation": {
                "calendar_year": 2026,
                "first_week_start": "2026-01-04",
                "calendar_end_exclusive": "2027-01-03",
                "reference": (
                    "https://portalsinan.saude.gov.br/"
                    "calendario-epidemiologico"
                ),
                "original_sem_pri_preserved": True,
            },
            "record_issues": issues_result,
            "export": export_result,
        }

        args.report.parent.mkdir(parents=True, exist_ok=True)

        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        print(f"Relatório salvo: {args.report}")

if __name__ == "__main__":
    main()
