# Sentinela - Qualidade dos dados

## Exploração inicial

Arquivo: INFLUD26-28-09-2026.csv.
Amostra: primeiras 1.000 linhas, sem seleção aleatória.

## Resultados

Arquivo: INFLUD26-28-09-2026.csv.
Data da avaliação: 30/09/2026.

A leitura foi realizada em blocos de 50.000 linhas,
avaliando SG_UF e DT_SIN_PRI.

### Resultados

- Total de linhas: 220.941.
- Linhas com SG_UF igual a MG: 29.087.
- UF de residência ausente: 93.
- Datas de início dos sintomas ausentes: 0.
- Datas preenchidas não convertidas: 0.
- Menor data nacional de início dos sintomas: 04/01/2026.
- Maior data nacional de início dos sintomas: 26/09/2026.
- Todas as datas convertidas pertencem a 2026.

### Formato temporal

DT_SIN_PRI foi convertido utilizando ISO 8601.
O mesmo formato foi aplicado à amostra e à base completa.

### Limitações

A conversão bem-sucedida verifica a leitura das datas,
mas não comprova sua correção epidemiológica.

Os limites temporais apresentados são da base nacional.
A cobertura semanal específica de MG ainda será avaliada.

As contagens representam linhas, sem avaliação de duplicidades
ou aplicação dos critérios finais de inclusão.

A ausência de registros em um período não deverá ser
interpretada automaticamente como ausência de casos.

### Correspondência entre data e semana epidemiológica

As 29.087 linhas de residentes em MG foram comparadas
com o calendário epidemiológico de 2026 do SINAN.

Resultado:
- 29.087 linhas com SEM_PRI uma semana acima da semana
  correspondente à data de início dos sintomas.
- Nenhuma linha não comparável.

Referência:
https://portalsinan.saude.gov.br/calendario-epidemiologico

A causa da divergência permanece pendente de esclarecimento.
O campo original será preservado.

Para a análise exploratória, será criada uma semana calculada
pela data de início dos sintomas e pelo calendário oficial.
Essa regra é específica para o calendário de 2026.

### Intervalo entre sintomas e notificação — MG

Foram avaliadas 29.087 linhas.

- Nenhuma data de notificação ausente ou não convertida.
- Nenhum intervalo não calculável ou negativo.
- Média: 5,68 dias.
- Mediana: 4 dias.
- Percentil 90: 11 dias.
- Percentil 95: 17 dias.
- Máximo: 160 dias.

Os resultados descrevem apenas notificações presentes
na versão de 28/09/2026.

Esse intervalo não mede todo o atraso até a publicação
nem garante a completude das semanas recentes.

O intervalo máximo será investigado antes de ser tratado
como erro ou excluído.

## Conclusão da exploração inicial

### Base avaliada

- Arquivo: INFLUD26-28-09-2026.csv.
- Versão: 28/09/2026.
- Total nacional: 220.941 linhas.
- Recorte: residentes em Minas Gerais, usando SG_UF = MG.
- Total no recorte: 29.087 linhas.

### Verificações realizadas

- Campos necessários à exploração presentes.
- Datas de início dos sintomas convertidas sem falhas.
- Todas as datas de início dos sintomas pertencem a 2026.
- Nenhum número de notificação ausente ou repetido no recorte.
- Códigos observados em CLASSI_FIN, HOSPITAL e EVOLUCAO
  correspondem às categorias do dicionário consultado.
- Valores ausentes mantidos separados do código “Ignorado”.
- Intervalos entre sintomas e notificação calculáveis
  e não negativos em todas as linhas de MG.

### Divergência temporal

SEM_PRI está uma semana acima da semana correspondente
no calendário oficial de 2026 em todas as linhas de MG.

O campo original foi preservado. Uma semana calculada
a partir de DT_SIN_PRI foi utilizada na exploração.

A causa da divergência ainda precisa ser esclarecida.
A regra utilizada não deverá ser aplicada automaticamente
a outros anos.

### Limitações

- Unicidade de NU_NOTIFIC não garante ausência de notificações
  de um mesmo episódio com números diferentes.
- Datas convertíveis não garantem correção epidemiológica.
- As contagens representam linhas da base, sem aplicação
  dos critérios finais de inclusão.
- Semanas recentes podem receber notificações e revisões.
- O intervalo até a notificação não mede todo o atraso
  até a publicação.
- Um único ano não é suficiente para definir a referência
  histórica do sistema de alertas.

### Avaliação de viabilidade

A base permite continuar o desenvolvimento exploratório
do recorte estadual de SRAG em Minas Gerais.

Essa avaliação não significa que os dados estejam prontos
para gerar alertas epidemiológicos.

### Pendências

- Confirmar condições de uso específicas dos dados.
- Esclarecer a divergência de SEM_PRI.
- Definir critérios de inclusão com documentação oficial.
- Avaliar o intervalo máximo de 160 dias.
- Avaliar compatibilidade e comparabilidade dos anos históricos.

## Validação do calendário no processamento

A rotina reutilizável reproduziu os resultados da exploração:

- 29.087 linhas verificadas.
- Nenhuma semana calculada ausente.
- Nenhuma semana original ausente ou inválida.
- Todas as linhas comparáveis.
- Diferença de +1 em SEM_PRI nas 29.087 linhas.
- Nenhuma outra diferença encontrada.

Os indicadores foram registrados no relatório JSON e conferidos
no notebook exploracao_srag_2026.ipynb.

A divergência permanece documentada, com o campo original preservado.

## Registro de problemas no processamento

O processamento gera um CSV com:
- Posição do registro na fonte.
- Campo relacionado.
- Código do problema identificado.

Regras implementadas:
- Data ausente.
- Data não convertível.
- Notificação anterior ao início dos sintomas.
- Data de início dos sintomas fora do calendário de 2026.

Na versão avaliada, foram verificadas 29.087 linhas de MG,
sem ocorrências nessas regras.

O CSV de problemas foi gerado com cabeçalho e sem registros.
O relatório JSON confirmou zero ocorrências e zero remoções.

Essa verificação não cobre todos os possíveis problemas
de qualidade epidemiológica.