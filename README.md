# Sentinela

Projeto de análise de dados epidemiológicos para acompanhar registros de
Síndrome Respiratória Aguda Grave (SRAG) do SIVEP-Gripe. Reúne tratamento
de dados em Python, uma API FastAPI e um painel em React para consultar
séries semanais, referências históricas e sinais de aumento incomum.

## Estado atual

O projeto está em desenvolvimento e inclui:

- Importação de CSV em blocos, seleção por UF de residência, validação
  de datas e exportação de registros e problemas de qualidade.
- Painel com filtros de região e ano, evolução semanal, mediana e quartis
  históricos, cobertura dos dados e explicação dos sinais identificados.
- Consulta de estimativas por nowcasting e dos estados operacionais
  `NORMAL`, `SIGNAL`, `ALERT` e `PENDING`, quando os arquivos estão disponíveis.
- Análises em notebooks de atraso de notificação, avaliação histórica,
  validação em São Paulo e desempenho do detector de mudanças SHIFT.

O painel oferece Minas Gerais e São Paulo, com anos entre 2019 e 2026
conforme os arquivos de cobertura presentes em `data/processed/`.
A API lê resultados previamente processados; os cálculos analíticos
permanecem nos notebooks. A pesquisa do SHIFT V5.1 está documentada
separadamente e não é executada pelas rotas do painel.

Os sinais estatísticos e estados de alerta não confirmam surtos.
Não há coleta automática nem envio de notificações.

## Estrutura

```text
backend/       API FastAPI, serviços, leitura dos CSVs e testes
frontend/      Painel React + TypeScript, Vite, React Query e Recharts
src/sentinela/ Importação, transformação, validação e exportação
scripts/       CLI de importação de SRAG
notebooks/     Processamento analítico e avaliações experimentais
data/raw/      Arquivos originais locais (não versionados)
data/processed/ Resultados locais consumidos pela API (não versionados)
docs/          Escopo, decisões, qualidade, protocolos e resultados
reports/       Figuras e artefatos de análise e recuperação
```

## Requisitos

- Python 3.12 ou superior.
- Node.js 22.13+ na linha 22, ou 24+, e npm para o frontend.
- CSVs do SIVEP-Gripe para processamento e arquivos derivados para o painel.

## Preparação do ambiente

Na raiz do projeto, execute:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
python3 -m pip install fastapi 'uvicorn[standard]'
```

O pacote de tratamento de dados e sua dependência de pandas estão
declarados em [`pyproject.toml`](pyproject.toml). FastAPI e Uvicorn são
necessários para executar a API.

[`backend/requirements.txt`](backend/requirements.txt) registra um ambiente
mais amplo, incluindo Jupyter e uma instalação editável do Sentinela
apontando para um commit remoto. Para trabalhar neste checkout, use a
instalação local acima.

Para executar o notebook de exploração:

```bash
python3 -m pip install jupyterlab ipykernel matplotlib scipy statsmodels
python3 -m jupyterlab
```

Os notebooks podem exigir dependências adicionais conforme o experimento.

## Execução do painel

### Backend

Com o ambiente virtual ativo, na raiz do projeto:

```bash
python3 -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

- Verificação da API: <http://127.0.0.1:8000/health>.
- Documentação interativa: <http://127.0.0.1:8000/docs>.

O endpoint de saúde funciona sem os CSVs. As consultas analíticas precisam
dos arquivos descritos em [Dados necessários para o painel](#dados-necessários-para-o-painel).

### Frontend

Em outro terminal:

```bash
cd frontend
npm ci
cp -n .env.example .env
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Confira se `frontend/.env` contém `VITE_API_URL=http://127.0.0.1:8000`
e abra <http://127.0.0.1:5173>. Reinicie o Vite após alterar essa variável.
A API permite as origens `http://localhost:5173` e `http://127.0.0.1:5173`;
outras origens exigem ajuste em `backend/app/main.py`.

### Rotas da API

Todas as rotas abaixo usam `GET`. Exceto `/health` e `/api/options`,
recebem os parâmetros `region` e `year`, por exemplo
`/api/trends?region=MG&year=2026`.

| Rota | Conteúdo |
| --- | --- |
| `/health` | Estado do serviço |
| `/api/options` | Regiões e anos com arquivos de cobertura disponíveis |
| `/api/trends` | Série semanal e referência histórica |
| `/api/signals` | Sinais e valores que sustentam a classificação |
| `/api/metadata` | Fonte, período observado e limitações |
| `/api/coverage` | Cobertura e situação das semanas |
| `/api/nowcast` | Estimativas considerando o atraso de notificação |
| `/api/status` | Estados operacionais por semana |

## Obtenção dos dados

O download é manual.

1. Consulte a fonte e o recurso registrados em
   [`docs/data-sources.md`](docs/data-sources.md).
2. Baixe o CSV de 2026.
3. Preserve o nome original do arquivo.
4. Coloque-o em data/raw/.
5. Registre a versão e a data do download em docs/data-sources.md.

A versão avaliada neste projeto é:
INFLUD26-28-09-2026.csv.

Os CSVs locais não são versionados no Git.

## Importação e validação do CSV de 2026

Para a versão avaliada, execute na raiz do projeto:

```bash
python3 scripts/import_srag.py data/raw/INFLUD26-28-09-2026.csv \
  --uf MG \
  --expected-rows 220941 \
  --expected-selected-rows 29087 \
  --report data/processed/srag_2026_mg_calendar_report.json \
  --output data/processed/srag_2026_mg_calendar.csv \
  --issues-output data/processed/srag_2026_mg_issues.csv
```

As contagens esperadas são específicas dessa versão.
Para outras versões, avalie as contagens antes de utilizar
esses argumentos.

O calendário calculado por esse script é específico de 2026. O comando
exporta registros individuais; a geração das séries semanais e demais
arquivos do painel é feita nos notebooks.

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

Resultados registrados na avaliação inicial do arquivo de 28/09/2026:

- 220.941 linhas na base nacional.
- 29.087 linhas de residentes em MG.
- Nenhuma falha de conversão das datas avaliadas.
- Nenhum intervalo negativo entre sintomas e notificação.
- CSV exportado com 13 colunas.
- Datas exportadas conferidas com os campos originais.

## Dados necessários para o painel

Os CSVs brutos e processados são ignorados pelo Git. Um clone novo não
inclui os dados necessários para preencher o painel. A API procura os
arquivos em `data/processed/`, com separador `;` e UF em minúsculas no nome.

Para MG em 2026, os arquivos são:

| Arquivo | Finalidade |
| --- | --- |
| `srag_2026_mg_weekly.csv` | Contagens semanais |
| `srag_mg_historical_reference_2019_2025.csv` | Mediana e quartis históricos |
| `srag_2026_mg_signal_evaluation.csv` | Avaliação dos sinais |
| `srag_2026_mg_weekly_coverage.csv` | Calendário e cobertura |
| `srag_2026_mg_nowcast.csv` | Resultados de nowcasting |
| `srag_2026_mg_operational_status.csv` | Estados operacionais |

Para outro recorte, substitua o ano e a UF; a referência histórica termina
no ano anterior ao consultado. A presença de cobertura habilita a opção
no painel, mas não garante que os demais arquivos necessários existam.

Os principais notebooks de preparação e análise são:

| Notebook | Responsabilidade |
| --- | --- |
| [Exploração de SRAG](notebooks/exploracao_srag_2026.ipynb) | Inspeção inicial, calendário, série semanal e cobertura de MG em 2026 |
| [Referência histórica](notebooks/historical_baseline_analysis.ipynb) | Séries históricas e referências de comparação |
| [Sinais de aumento incomum](notebooks/unusual_increase_signals.ipynb) | Avaliação dos sinais de MG em 2026 |
| [Avaliação histórica](notebooks/historical_alert_evaluation.ipynb) | Avaliação retrospectiva dos sinais |
| [Atraso de notificação](notebooks/reporting_delay_analysis.ipynb) | Nowcasting e estados operacionais de MG |
| [Validação em São Paulo](notebooks/multiregion_validation_sp.ipynb) | Preparação e avaliação do recorte de SP |
| [Desempenho do modelo](notebooks/model_performance_evaluation.ipynb) | Experimentos e validação do SHIFT |

O processamento ainda depende da execução e configuração dos notebooks,
incluindo os caminhos e versões dos arquivos de entrada; não existe um
comando único que reconstrua todos os artefatos. Preserve os resultados
experimentais congelados conforme os protocolos em `docs/`.

## Verificações de desenvolvimento

Para executar os testes do backend, na raiz e com o ambiente virtual ativo:

```bash
python3 -m pip install pytest httpx
python3 -m pytest backend/tests
```

Parte dos testes depende dos CSVs locais de MG (2025 e 2026) e SP (2026),
inclusive alguns testes em `backend/tests/unit/`. Sem esses artefatos,
a suíte completa não é independente dos dados.

Para verificar o frontend:

```bash
cd frontend
npm run lint
npm run build
```

O build gera os arquivos em `frontend/dist/`.

## Limitações conhecidas

- SEM_PRI apresenta diferença de +1 em relação ao calendário
  oficial nas linhas de MG avaliadas.
- SEM_PRI é preservado; o calendário calculado utiliza
  uma função específica para 2026.
- Os critérios finais de inclusão permanecem em avaliação.
- Registros recentes estão sujeitos a atualização.
- Semanas sem cobertura confirmada não devem ser interpretadas como zero.
- A data da fonte apresentada pela API está fixa em `SOURCE_UPDATED_AT`,
  em `backend/app/services/metadata.py`; substituir os CSVs não a atualiza.
- O painel depende de resultados pré-calculados, sem reprocessamento automático.
- As condições de uso específicas dos dados aguardam
  esclarecimento do responsável.

## Documentação

- [Visão do projeto](docs/vision.md)
- [Escopo do MVP](docs/scope.md)
- [Fontes e registro da coleta](docs/data-sources.md)
- [Qualidade dos dados](docs/data-quality.md)
- [Decisões do projeto](docs/decisions.md)
- [Resultados de validação do SHIFT](docs/results.md)
- [Encerramento experimental V4/V5](docs/v4_v5_closure.md)
- [Especificação do SHIFT V5.1](docs/v5.1_specification.md)
- [Protocolo V5.1](docs/v5.1_PROTOCOL.md)
- [Protocolo de validação V5.1](docs/V5.1_VALIDATION_PROTOCOL.md)
- [Protocolo prospectivo V5.1](docs/V5.1_PROSPECTIVE_PROTOCOL.md)
