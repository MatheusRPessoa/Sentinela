# Sentinela

Projeto de análise de dados epidemiológicos para acompanhar
registros de Síndrome Respiratória Aguda Grave (SRAG),
inicialmente entre residentes de Minas Gerais.

## Estado atual

O projeto realiza leitura de CSV em blocos, seleção por UF
de residência, validação das datas e exportação dos dados.

Ainda não gera alertas nem confirma surtos.

## Requisitos

- Python 3.12 ou superior.
- Acesso ao CSV público do SIVEP-Gripe.

## Preparação do ambiente

Na raiz do projeto, execute:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

As dependências da aplicação estão declaradas em pyproject.toml.

Para executar o notebook de exploração:

```bash
python3 -m pip install jupyterlab ipykernel
python3 -m jupyterlab
```

Notebook:
notebooks/exploracao_srag_2026.ipynb

## Obtenção dos dados

O download é manual.

1. Acesse a página do recurso:
   https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026/resource/74091efc-3f75-42e8-a6fa-6b79a8d30582
2. Baixe o CSV de 2026.
3. Preserve o nome original do arquivo.
4. Coloque-o em data/raw/.
5. Registre a versão e a data do download em docs/data-sources.md.

A versão avaliada neste projeto é:
INFLUD26-28-09-2026.csv.

Os CSVs locais não são versionados no Git.

## Execução

Para a versão avaliada, execute em uma única linha:

```bash
python3 scripts/import_srag.py data/raw/INFLUD26-28-09-2026.csv --uf MG --expected-rows 220941 --expected-selected-rows 29087 --report data/processed/srag_2026_mg_calendar_report.json --output data/processed/srag_2026_mg_calendar.csv --issues-output data/processed/srag_2026_mg_issues.csv
```

As contagens esperadas são específicas dessa versão.
Para outras versões, avalie as contagens antes de utilizar
esses argumentos.

## Saídas

- CSV dos registros selecionados, com datas convertidas
  e campos de calendário calculados.
- Relatório JSON com contagens, validação das datas e do calendário,
  resumo dos problemas e resultado da exportação, quando solicitada.
- CSV opcional de problemas, definido por `--issues-output`, com
  separador ponto e vírgula e codificação UTF-8.

O CSV de problemas contém uma linha por ocorrência nos registros
selecionados pela UF de residência. Suas colunas são:

- `source_record_number`: posição do registro no CSV original,
  começando em 1 e sem contar o cabeçalho.
- `field`: campo relacionado ao problema.
- `issue_code`: código do problema identificado.

São registrados problemas de datas ausentes ou inválidas,
notificação anterior aos sintomas e início dos sintomas fora
do calendário de 2026. A divergência entre `SEM_PRI` e a semana
calculada é contabilizada no relatório JSON.

Um registro pode ter mais de uma ocorrência. Nenhum registro é
removido por essas verificações. Se não houver problemas, o CSV
contém apenas o cabeçalho. Sem `--issues-output`, o resumo dos
problemas continua disponível no JSON solicitado por `--report`.

Os CSVs de registros e de problemas não podem existir antes da
execução. O caminho de `--issues-output` deve ser diferente da
fonte, do CSV de registros e do relatório JSON. Para repetir o
processamento, escolha novos nomes para os CSVs de saída.

## Verificações da versão avaliada

- 220.941 linhas na base nacional.
- 29.087 linhas de residentes em MG.
- Nenhuma falha de conversão das datas avaliadas.
- Nenhum intervalo negativo entre sintomas e notificação.
- CSV exportado com 13 colunas.
- Datas exportadas conferidas com os campos originais.

## Limitações conhecidas

- SEM_PRI apresenta diferença de +1 em relação ao calendário
  oficial nas linhas de MG avaliadas.
- SEM_PRI é preservado; o calendário calculado utiliza
  uma função específica para 2026.
- Os critérios finais de inclusão permanecem em avaliação.
- Registros recentes estão sujeitos a atualização.
- As condições de uso específicas dos dados aguardam
  esclarecimento do responsável.

## Documentação

- docs/vision.md
- docs/scope.md
- docs/data-sources.md
- docs/data-quality.md
- docs/decisions.md