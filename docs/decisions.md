# Decisões técnicas

## Semana epidemiológica calculada — 2026

Data: 30/09/2026.

### Problema observado

Nas 29.087 linhas de residentes em MG da versão
INFLUD26-28-09-2026.csv, SEM_PRI está uma semana acima
da semana correspondente no calendário oficial de 2026.

### Decisão

Preservar SEM_PRI e acrescentar:

- EPI_YEAR_CALCULATED.
- EPI_WEEK_CALCULATED.

Os campos são calculados a partir de DT_SIN_PRI_PARSED,
utilizando o calendário oficial de 2026.

Referência:
https://portalsinan.saude.gov.br/calendario-epidemiologico

### Limites

- A função é específica para 2026.
- Datas fora do calendário recebem campos calculados ausentes.
- Nenhuma linha é removida pela transformação.
- A causa da divergência permanece pendente de esclarecimento.

### Verificação

- 29.087 linhas exportadas.
- Semanas calculadas entre 1 e 38.
- Diferença de +1 no campo original em todas as linhas.