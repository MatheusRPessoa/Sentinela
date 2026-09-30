# Sentinela - Fontes de dados

## Situação da seleção

Fontes iniciais identificadas em 30/09/2026.
A seleção definitiva depende da avaliação dos arquivos,
da documentação e das condições de uso.

## 1. SIVEP-Gripe — Dados Abertos do SUS

Responsável: Ministério da Saúde.

link:
https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026

Papel: principal candidata para alimentar as análises do MVP.

A fonte disponibiliza dados públicos de SRAG organizados por ano,
além de dicionário de variáveis e ficha de notificação.

### Pontos e verificar

- Acesso e download dos arquivos.
- Formatos e tamanho dos arquivos.
- Períodos efetivamente disponíveis.
- Condições de uso dos dados.
- Campos necessários para selecionar Minas Gerais.
- Distinção entre local de residência e local de notificação.
- Datas disponíveis para construir a série epidemiológica.
- Critérios para inclusão dos registros de SRAG.
- Atualizações, revisões e compatibilidade entre anos.

## 2. SES-MG — Conexão Viral

Responsável: Secretaria de Estado de Saúde de Minas Gerais.

Link:
https://www.saude.mg.gov.br/conexaoviral/

Papel: documentação e referências estaduais de vigilância
respiratória, incluindo materiais sobre SRAG.

## 3. Fiocruz — InfoGripe

Responsável: Fundação Oswaldo Cruz.

Link:
https://github.com/infogripe/Boletim_InfoGripe

Papel: referência de boletins, análises e metodologia.

As comparações deverão considerar diferenças de filtros,
datas de atualização e métodos utilizados.

## Avaliação inicial de acesso e formato - SIVEP-Gripe

Data de verificação: 30/09/2026.

### Recurso avaliado

- Ano: 2026.
- Versão: 28/09/2026.
- Formato: CSV.
- Separador: ponto e vírgula.
- Tamanho: aproximadamente 247 MB.
- Acesso ao início do arquivo: realizado sem autenticação.
- Download completo e leitura integral: pendentes.

Página do recurso:
https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026/resource/74091efc-3f75-42e8-a6fa-6b79a8d30582

### Documentação

O portal disponibiliza um dicionário identificado como
“2019 a 2025”. Sua compatibilidade com a base de 2026
deverá ser conferida.

### Condições de uso

O portal apresenta uma licença geral para o conteúdo do site.
A licença aplicável especificamente aos arquivos de dados
ainda precisa ser confirmada.

### Decisão inicial

Utilizar CSV na exploração inicial com Python.
O formato definitivo será escolhido após avaliar a leitura,
o consumo de memória e os arquivos disponíveis.

## Cobertura geográfica  e temporal

### Cobertura geográfica

A fonte possui cobertura nacional.

O recorte proposto para o Sentinela será por estado de residência,
selecionado registros em que SG_UF seja igual a "MG".

SG_UF_NOT representa o estado de notificação e não será utilizado
com filtro geográfico principal.

as definições foram conferidas no dicionário de 2019 a 2025.
Os campos foram identificados no cabeçalho do CSV de 2026;
seus valores ainda serão conferidos na exploração dos dados.

### Cobertura temporal

O portal lista arquivos anuais de 2019 a 2026

Essa disponibilidade não garante que todas as semanas estejam
completas ou que os registros sejam comparáveis entre anos.

O arquivo de 2026 corresponde a um ano de andamento.

### Campos temporais candidatos

- DT_SIN_PRI: data dos primeiros sintomas.
- SEM_PRI: semana epidemiológica dos primeiros sintomas.

Esses campos serão avaliados para organizar a série temporal.

### Validações pendentes
- Conferir a presença de registros de residentes em MG.
- Medir valores ausentes nos campos geográficos e temporais.
- Verificar as datas e semanas presentes em cada arquivo.
- Conferir mudanças de estrutura e critérios entre anos.
- Definir quais anos poderão compor a referência histórica.

## Frequência de atualização

O portal informa periodicidade semanal para a publicação dos dados.

O recurso de 2026 consultado está identificado como versão
de 28/09/2026.

A data de publicação não representa garantia de completude:
registros podem ser inseridos ou corrigidos posteriormente.

O Sentinela deverá registrar separadamente:

- Data da versão publicada pela fonte.
- Data e hora da coleta pelo projeto.
- Período efetivamente presente nos dados.

A frequência de coleta do Sentinela será definida durante
a implementação.

## Dicionário dos campos

O portal disponibiliza um dicionário identificado como
“2019 a 2025”.

Link:
https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026/resource/3135ac9c-2019-4989-a893-2ed50ebd8e68

### Campos iniciais para avaliação

| Campo | Significado | Uso proposto |
|---|---|---|
| SG_UF | UF de residência | Selecionar residentes em MG |
| SG_UF_NOT | UF de notificação | Conferir o local de notificação |
| DT_SIN_PRI | Data dos primeiros sintomas | Organizar a série temporal |
| SEM_PRI | Semana epidemiológica dos primeiros sintomas | Conferir o agrupamento semanal |

Esses campos foram identificados no cabeçalho do CSV de 2026.

### Compatibilidade pendente

Antes de utilizar o dicionário como referência para 2026,
será necessário:

- Comparar os campos documentados com as colunas do arquivo.
- Conferir formatos e valores observados.
- Identificar campos novos, removidos ou alterados.
- Verificar se existe documentação específica para 2026.
- Documentar divergências encontradas.

### Cuidados temporais

O agrupamento semanal deverá considerar também o ano
epidemiológico, evitando misturar semanas de anos diferentes.

Dados recentes serão apresentados como sujeitos a revisão.
A forma de identificar períodos incompletos será definida
após explorar os dados.

## Esclarecimentos sobre condições de uso

Em 30/09/2026, a consulta à página do conjunto não permitiu
confirmar uma licença específica para o arquivo de 2026.

Contato indicado pela fonte: dadosabertos@saude.gov.br.

Situação: solicitação preparada, ainda não enviada.

Questões:
- Licença e condições para publicação de resultados derivados.
- Convenção utilizada no campo SEM_PRI.
- Disponibilidade de dicionário específico para 2026.

## Seleção inicial da fonte

O SIVEP-Gripe, disponibilizado pelo Portal de Dados Abertos
do SUS, foi selecionado para continuar o desenvolvimento
exploratório do Sentinela.

### Justificativa

- Disponibiliza arquivos públicos e documentação.
- Permite selecionar residentes em Minas Gerais.
- Oferece campos necessários à análise temporal de SRAG.
- A base de 2026 foi lida e explorada com sucesso.

### Limites da seleção

A seleção permite avançar no desenvolvimento técnico,
mas não encerra as pendências sobre:

- Condições de uso específicas dos dados.
- Divergência do campo SEM_PRI.
- Documentação aplicável a 2026.
- Critérios finais de inclusão.
- Comparabilidade dos anos históricos.

As respostas do responsável poderão exigir ajustes no projeto.

## Registro da coleta inicial

- Fonte: Ministério da Saúde — SIVEP-Gripe.
- Arquivo: INFLUD26-28-09-2026.csv.
- Versão publicada: 28/09/2026.
- Data do download: 30/09/2026.
- Método: download manual pelo Portal de Dados Abertos do SUS.
- Local no projeto: data/raw/INFLUD26-28-09-2026.csv.
- Arquivo original preservado sem alterações.

Página do recurso:
https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026/resource/74091efc-3f75-42e8-a6fa-6b79a8d30582