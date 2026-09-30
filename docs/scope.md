# Sentinela - Escopo do MVP

## Região inicial

O MVP terá como região inicial o estado de Minas Gerais.

A primeira análise acompanhará os registros no nível estadual.
O detalhamento por município ou região de saúde será avaliado
conforme a disponibilidade e a qualidade dos dados.

## Foco epidemiologico

O foco inicial será Síndrome Respiratória Aguda Grave (SRAG).

O projeto acompanhará a evolução temporal dos registros e buscará
identificar aumentos incomuns em relação ao histórico disponível.

SRAG será tratada como uma síndrome. A análise por agente causador
dependerá das informações disponíveis na fonte selecionada.

## Condição para implementação

O recorte será confirmado após verificar se a fonte oferece
histórico, datas e informações geográficas suficientes para
as análises propostas.

## Perguntas que o painel deverá responder

## Evolução dos registros

1. Quantos registros de SRAG ocorreram em Minas Gerais em cada
   semana epidemiológica do período selecionado?

2. Como esses registros evoluíram nas últimas semanas?

3. Como o período selecionado se compara ao mesmo período
   de anos anteriores?

### Identificação de aumentos incomuns

4. O número de registros está acima do padrão histórico esperado
   para essa época do ano?

5. Em quais semanas foram identificados aumentos incomuns?

6. Por que cada sinal foi gerado e quais valores sustentam
   essa indicação?

### Qualidade e atualização dos dados

7. Qual é a fonte dos dados e quando ocorreu a última atualização?

8. Quais semanas apresentam dados potencialmente incompletos
   ou sujeitos a revisão?

9. Existem dados ausentes ou problemas de qualidade que limitem
   a interpretação dos resultados?

## Definições necessárias para a análise

A etapa de avaliação da fonte deverá definir:

- Quais registros serão incluídos na contagem de SRAG
- Qual data será usada para atribuir a semana epidemiológica,
  priorizando a data de início dos sintomas quando adequada.
- Qual período histórico será utilizado nas comparações.
- Como serão identificadas e apresentadas semanas incompletas.

## Pergunta para uma expansão futura

- Quais municípios ou regiões de saúde apresentam aumentos
  incomuns de registros de SRAG?

Essa análise dependerá da disponibilidade, da qualidade e do
volume de dados de cada localidade.

## Funcionalidades incluídas no MVP

### Importação e tratamento dos dados

- Importar dados de SRAG de fonte pública oficial.
- Selecionar registros referentes a Minas Gerais, conforme
  o critério geográfico definido durante a avaliação da fonte.
- Padronizar campos necessários à análise.
- Registrar a origem e a data da coleta.
- Identificar dados ausentes, registros inválidos e possíveis
  duplicidades.

### Análise histórica

- Agrupar os registros por semana epidemiológica.
- Exibir a evolução dos registros no nível estadual.
- Permitir a seleção do período de análise.
- Comparar períodos equivalentes de anos anteriores.
- Apresentar períodos potencialmente incompletos ou sujeitos
  a revisão.

### Sinais de aumento incomum

- Comparar os registros com uma referência histórica.
- Identificar semanas com valores acima do esperado,
  conforme o método selecionado e documentado.
- Explicar cada sinal, mostrando o valor observado,
  a referência utilizada e a regra aplicada.
- Informar quando os dados forem insuficientes para a análise.

### Painel

- Exibir indicadores e gráficos de evolução temporal.
- Apresentar os sinais de aumento incomum.
- Mostrar a fonte, a data de atualização e as limitações.
- Tratar situações de carregamento, erro e ausência de dados.

### Documentação e avaliação

- Documentar instalação, execução e atualização dos dados.
- Documentar o cálculo dos indicadores e a regra dos sinais.
- Avaliar os sinais em dados históricos.
- Registrar resultados e limitações da avaliação.

## Funcionalidade fora do MVP

- Análise detalhada por município ou região de saúde.
- Análise específica por agente causador.
- Previsão de casos, internações ou demanda por leitos.
- Monitoramento de outras doenças ou síndromes.
- Integração com sistemas internos de hospitais.
- Atualização em tempo real.
- Envio automático de alertas por e-mail, SMS ou aplicativos.
- Cadastro de usuários e controle de permissões.
- Diagnóstico individual ou recomendação de tratamento.
- Confirmação automática de surtos.

## Limites de interpretação

Os sinais do Sentinela indicarão alterações estatísticas que
merecem avaliação. Eles não serão apresentados como confirmação
de surtos.

As análises representarão os registros disponíveis na fonte,
sem assumir que correspondem à totalidade dos casos ocorridos.

## Critério de conclusão do MVP

O MVP estará concluído quando for possível executar a importação,
consultar a série histórica de SRAG em Minas Gerais e visualizar
sinais explicáveis, com resultados avaliados e limitações
documentadas.

Caso os dados não sejam suficientes para gerar sinais confiáveis
essa limitação deverá ser registrada e o escopo revisado.