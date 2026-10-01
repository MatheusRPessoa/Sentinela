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

## Avaliação do método de referência histórica

Como os anos históricos apresentam diferenças substanciais de magnitude
e padrão sazonal, uma média simples pode ser fortemente influenciada por
anos atípicos.

Como método inicial, será avaliada uma referência semanal baseada na
mediana histórica, acompanhada pelos percentis 25 e 75.

A referência é calculada separadamente para cada semana epidemiológica,
preservando a sazonalidade observada nos dados.

O ano de 2026 não participa do cálculo da referência histórica.


## Referência histórica para comparação semanal de SRAG

**Status:** Aceita  
**Data:** 2026-10-01

### Contexto

O Sentinela necessita de uma referência histórica para contextualizar a
evolução semanal dos registros de SRAG em residentes de Minas Gerais.

Foram avaliados dados de 2019 a 2025. O histórico apresenta diferenças
substanciais de magnitude e padrão sazonal entre os anos, incluindo
comportamentos particularmente distintos no período de 2020 a 2022.

Por esse motivo, uma média simples de todo o histórico seria sensível a
anos com volumes excepcionalmente elevados.

### Decisão

A referência inicial será calculada por **semana epidemiológica**, utilizando
a **mediana das contagens semanais dos anos históricos de 2019 a 2025**.

Como medidas descritivas de dispersão, serão calculados também:

- percentil 25 (Q25);
- percentil 75 (Q75).

A série corrente de 2026 será comparada com a mesma semana epidemiológica
dos anos históricos e não participará do cálculo de sua própria referência.

A região será definida pela **UF de residência (`SG_UF`)**.

A referência temporal será a **data de início dos sintomas (`DT_SIN_PRI`)**.
A semana epidemiológica será calculada a partir dessa data utilizando a
mesma regra de calendário aplicada à série corrente.

O campo `SEM_PRI` da fonte não será utilizado diretamente para construir
a referência, pois sua numeração não corresponde à convenção adotada na
série validada de 2026.

### Requisitos mínimos

- pelo menos 3 anos históricos válidos para uma semana;
- data de início dos sintomas válida;
- região definida pela UF de residência;
- mesma regra de calendário para histórico e série corrente;
- somente anos anteriores ao ano corrente na referência;
- semanas 1 a 52 na referência principal;
- ausência de cobertura preservada como valor ausente, e não zero.

Na base atualmente disponível, as semanas 1 a 52 possuem dados dos
sete anos históricos de 2019 a 2025.

### Justificativa

A mediana foi escolhida como método inicial por ser menos sensível a
valores extremos do que a média, característica relevante diante da
heterogeneidade observada entre 2019 e 2025.

O cálculo por semana epidemiológica preserva a componente sazonal da série
e permite comparar a semana corrente com o mesmo período dos anos
anteriores.

Q25 e Q75 complementam a mediana mostrando a dispersão central dos valores
históricos sem serem tratados como limites de alerta.

### Limitações

O histórico contém apenas sete anos e inclui períodos com comportamentos
epidemiológicos muito distintos, especialmente entre 2020 e 2022.

Mudanças na vigilância, diagnóstico, notificação e definição de casos podem
afetar a comparabilidade entre anos.

A semana 53 não faz parte da referência principal por não estar presente
em todos os anos.

A referência definida nesta decisão é **descritiva**. Q25 e Q75 não
representam limites validados de alerta, surto ou anomalia. A definição de
critérios de alerta deverá ser tratada e validada separadamente.

### Alternativas consideradas

**Média histórica semanal:** não adotada inicialmente por ser mais sensível
aos valores extremos observados no histórico.

**Uso direto de `SEM_PRI`:** não adotado porque a numeração encontrada na
fonte não corresponde à convenção de semana utilizada pela série validada.

**Restrição imediata a anos recentes:** não adotada nesta primeira versão.
Os sete anos são preservados e a mediana é utilizada para reduzir a
influência de valores extremos. A composição do período histórico poderá
ser reavaliada posteriormente.