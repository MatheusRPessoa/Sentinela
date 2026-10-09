# Encerramento Experimental — SHIFT V4 / V5

## Status

Fase V4/V5 encerrada e congelada.

Nenhum resultado desta fase deve ser recalculado, reclassificado ou utilizado para retunar retrospectivamente a V4.

## Algoritmo

- Versão base: `V4_FROZEN`
- Protocolo pseudo-prospectivo: `V5_PROTOCOL_1`
- Ano pseudo-prospectivo principal: 2026

## Evidência acumulada

### V4

A V4 apresentou resultados iniciais fortes em:

- validação externa histórica;
- holdout cego;
- janelas negativas pré-definidas;
- replay pseudo-prospectivo de 2024–2025.

Esses experimentos motivaram o congelamento da V4 antes da avaliação nacional de 2026.

### V5 — 2026

Foram congelados:

- 42 regimes inicialmente detectados;
- 40 eventos após consolidação;
- 17 eventos externamente avaliáveis;
- 23 eventos não resolvidos externamente.

Entre os 17 avaliáveis:

- 8 `CONFIRMED`;
- 5 `TEMPORAL_MISMATCH`;
- 4 `DIRECTION_MISMATCH`;
- 0 `NOT_CONFIRMED`.

Taxa de confirmação completa:

- 8 / 17 = 47,1%.

Acurácia direcional:

- 13 / 17 = 76,5%.

## Sinais STRONG

Entre os 15 eventos STRONG avaliáveis:

- 8 foram completamente confirmados;
- 13 tiveram direção correta;
- 2 apresentaram erro de direção;
- 5 apresentaram erro temporal.

Acurácia direcional STRONG:

- 13 / 15 = 86,7%.

Confirmação completa STRONG:

- 8 / 15 = 53,3%.

## Precisão temporal

Após exclusão de eventos temporalmente não avaliáveis por censura à esquerda:

- 12 eventos permaneceram temporalmente avaliáveis;
- 8 ficaram dentro de ±2 semanas;
- acurácia temporal ±2 semanas = 66,7%;
- erro absoluto mediano = 1,5 semana;
- erro absoluto médio = 2,75 semanas.

## Censura à esquerda

Eventos externos anteriores à primeira semana matematicamente estimável pelo protocolo não devem ser classificados como falhas temporais.

Com:

- `week_start = 8`;
- `min_weeks_each_side = 3`;

a primeira semana de mudança estimável é aproximadamente SE11.

## Hipótese rejeitada

Foi testado um estimador alternativo baseado em tendência persistente.

Resultado:

- LLR original dentro de ±2 semanas: 8 / 12;
- onset persistente dentro de ±2 semanas: 4 / 12.

Conclusão:

`REJECT_AS_UNIVERSAL_ONSET_ESTIMATOR`.

## Achado sobre fase da temporada

Desempenho temporal exploratório:

- EARLY: 6 / 7 dentro de ±2 semanas;
- MID/LATE: 2 / 5 dentro de ±2 semanas.

Teste exato de Fisher:

- odds ratio = 0,111;
- p = 0,222.

Correlação de Spearman entre semana externa e erro temporal absoluto:

- rho = 0,322;
- p = 0,308.

Conclusão:

há sinal exploratório de pior localização temporal em eventos mais tardios, mas a evidência ainda não é conclusiva.

## Interpretação do LLR

LLR elevado não deve ser interpretado como probabilidade de correção epidemiológica.

O LLR representa evidência estatística de diferença entre segmentos da série.

Foram observados eventos com LLR elevado e:

- direção externa incorreta;
- localização temporal incorreta.

## Principal conclusão

A V4/V5 apresentou desempenho mais consistente para:

1. detectar a existência de uma mudança;
2. identificar sua direção.

A localização temporal exata do onset mostrou maior variabilidade.

A arquitetura futura deve tratar separadamente:

- existência do evento;
- direção;
- onset estimado;
- momento do alerta;
- força estatística;
- observabilidade.

## Regra de congelamento

A partir deste documento:

- V4 não deve ser retunada com resultados de 2026;
- V5_PROTOCOL_1 não deve ser reinterpretado para melhorar métricas;
- todos os experimentos futuros devem usar outro protocolo e ser identificados como V5.1 ou posterior;
- os dados de 2026 podem ser usados para geração de hipóteses, mas não para validação independente das regras derivadas deles.