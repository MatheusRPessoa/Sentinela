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


## Avaliação histórica da regra V1

A regra V1 foi avaliada retrospectivamente utilizando 2024 e 2025,
sempre construindo a referência histórica apenas com anos anteriores
ao ano avaliado.

Os eventos de referência foram definidos a partir de evidências externas
do InfoGripe, independentemente dos sinais produzidos pelo Sentinela.

### Avaliação por evento

Foram avaliados dois eventos externos:

- 2024: evento iniciado na SE 15; não detectado pela V1;
- 2025: evento iniciado na SE 14; primeiro sinal na SE 17.

O evento de 2025 apresentou atraso de três semanas em relação ao início
externo documentado.

Um dos dois eventos foi detectado. Essa proporção é apenas descritiva
do pequeno conjunto avaliado e não constitui estimativa robusta de
sensibilidade.

### Avaliação por pontos externos

Foram utilizados oito pontos com classificação externa explícita:

- 5 `EVENT`;
- 3 `NO_EVENT`.

Resultados:

- verdadeiro positivo: 1;
- falso positivo: 0;
- verdadeiro negativo: 3;
- falso negativo: 4.

Não houve falso alerta nos três pontos negativos avaliados.

Esse resultado não implica taxa geral de falsos alertas igual a zero,
pois o número de pontos negativos é pequeno e semanas sem evidência
externa suficiente foram excluídas.

### Limitações

Os pontos externos não representam eventos epidemiológicos independentes:
várias semanas podem pertencer ao mesmo episódio.

Por esse motivo, a avaliação por evento é utilizada para analisar
detecção e atraso, enquanto a avaliação por pontos é complementar.

Os eventos e pontos de referência representam evidências externas de
atividade/crescimento de SRAG segundo o critério adotado. Um `SIGNAL`
do Sentinela é um sinal estatístico e não constitui confirmação de surto.

Os resultados de 2024 e 2025 não devem ser utilizados para reajustar
a regra V1 e simultaneamente continuar sendo tratados como avaliação
independente.

## Validação retrospectiva — evento respiratório de abril/maio de 2025

### Objetivo

Avaliar se a regra de sinal do Sentinela identifica períodos que coincidem com eventos epidemiológicos relevantes documentados por fontes oficiais.

Esta análise é retrospectiva. Portanto, não demonstra que o sistema teria antecipado o evento em tempo real, pois isso também dependeria da disponibilidade e do atraso de notificação dos dados em cada semana.

### Resultado do Sentinela

Para Minas Gerais em 2025, utilizando como referência histórica os anos de 2019 a 2024, o Sentinela identificou seis semanas consecutivas com sinal de aumento incomum:

| Semana epidemiológica | Observado | Mediana histórica | Q75 | Razão para mediana |
|---|---:|---:|---:|---:|
| SE 17 | 1.087 | 695,0 | 1.063,5 | 1,56× |
| SE 18 | 1.586 | 744,5 | 1.178,0 | 2,13× |
| SE 19 | 1.941 | 847,0 | 1.285,25 | 2,29× |
| SE 20 | 2.201 | 986,0 | 1.487,75 | 2,23× |
| SE 21 | 2.404 | 1.029,5 | 1.558,0 | 2,34× |
| SE 22 | 2.148 | 1.145,0 | 1.777,75 | 1,88× |

A regra utilizada considera sinal quando o número observado está:

1. acima do terceiro quartil histórico (`Q75`); e
2. em pelo menos `1,5×` a mediana histórica.

As seis semanas satisfizeram simultaneamente os dois critérios.

### Evidências externas

Em 2 de maio de 2025, o Governo de Minas Gerais decretou situação de emergência em saúde pública em razão do aumento dos casos de Síndrome Respiratória Aguda Grave (SRAG). O decreto cita aumento da circulação de vírus respiratórios, crescimento da demanda por leitos pediátricos e de UTI e incremento expressivo dos casos de SRAG.

Em 6 de maio de 2025, a Prefeitura de Uberlândia também declarou situação de emergência. Segundo o município, houve aumento aproximado de 90% nas internações por SRAG causada por vírus respiratórios não relacionados à Covid-19 durante abril, com tendência de crescimento a partir da segunda quinzena do mês.

Em 7 de maio ocorreu a primeira reunião do Centro de Operações de Emergências em Saúde por Síndrome Respiratória Aguda Grave (COE-Minas-SRAG), formalizada pelo Governo de Minas para coordenar e monitorar as ações de enfrentamento.

Em 21 de maio, Uberlândia anunciou um plano municipal de enfrentamento das síndromes respiratórias, incluindo abertura de novos leitos, reforço de equipes e criação de comissão específica para SRAG.

### Relação temporal

A sequência identificada pelo Sentinela começa na SE 17 de 2025 e permanece até a SE 22.

Esse período coincide com o aumento de internações e com as medidas de resposta adotadas pelo poder público durante o fim de abril e o mês de maio.

Em termos retrospectivos, há concordância temporal entre:

- o início da sequência de sinais estatísticos;
- o aumento documentado de internações por SRAG;
- a declaração estadual de situação de emergência;
- a mobilização de estruturas de resposta;
- e a ampliação de capacidade assistencial.

### Interpretação

O resultado sugere que a regra do Sentinela é capaz de identificar alterações epidemiológicas relevantes em uma série histórica real.

Entretanto, essa concordância não deve ser interpretada como evidência de causalidade ou como prova de antecipação do evento.

Para afirmar capacidade de alerta precoce, seria necessário reconstruir o cenário de disponibilidade dos dados em cada semana, considerando atrasos de notificação, revisão de registros e data efetiva de atualização da base.

### Conclusão

O episódio de abril/maio de 2025 constitui um caso de validação retrospectiva favorável ao Sentinela.

A sequência de seis sinais consecutivos nas SE 17–22 coincide temporalmente com um período oficialmente reconhecido de aumento de SRAG em Minas Gerais.

Esse resultado apoia a utilidade do método como ferramenta de monitoramento epidemiológico e justifica análises adicionais em outros anos e eventos conhecidos.

### Fontes externas

- Governo de Minas Gerais. **Estado decreta situação de emergência em saúde pública diante do aumento de doenças respiratórias**, 02/05/2025.
- Assembleia Legislativa de Minas Gerais. **Decreto com Numeração Especial nº 411, de 02/05/2025**.
- Prefeitura de Uberlândia. **Prefeitura decreta situação de emergência devido ao aumento de casos de Síndrome Respiratória Aguda Grave**, 06/05/2025.
- Governo de Minas Gerais. **Governo de Minas implementa Centro de Operações de Emergência em Saúde por Síndrome Respiratória Aguda Grave**, 08/05/2025.
- Prefeitura de Uberlândia. **Prefeitura apresenta Plano de Ação para o enfrentamento das síndromes respiratórias**, 21/05/2025.


### Estado operacional

- `NORMAL`: nenhuma sequência ativa de sinais.
- `SIGNAL`: uma semana madura acima dos limiares.
- `ALERT`: duas semanas consecutivas com `SIGNAL`.
- O `ALERT` permanece ativo até ocorrerem duas semanas consecutivas sem sinal.
- `PENDING`: semana observada, porém ainda sem maturidade mínima para classificação operacional.
- Maturidade mínima atual: 80% de completude histórica esperada.
- O nowcast utiliza apenas anos anteriores ao ano avaliado.



## SHIFT V4 — Frozen validation milestone

A versão V4 do detector SHIFT foi congelada antes da validação externa.

Resultados do holdout:

- TP: 4
- FN: 0
- TN: 12
- FP: 0
- Sensibilidade observada: 100%
- Especificidade observada: 100%
- FPR observado: 0%

Nenhum parâmetro foi alterado após o congelamento.

Os resultados devem ser interpretados considerando o tamanho amostral limitado
e a necessidade de validação prospectiva independente.