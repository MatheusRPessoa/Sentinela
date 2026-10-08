# Recuperação do notebook

Execução de `notebooks/model_performance_evaluation.ipynb`, excluindo a última célula.
Consulte `execution.json` para o resultado da execução.

Para restaurar as variáveis e funções no kernel da IDE, execute:

```python
%run -i /home/matheuspessoa/Sentinela/reports/model_performance_recovery_2026-10-07/restore.py
```

- `variables.pkl`: variáveis serializáveis, incluindo DataFrames, séries e resultados.
- `functions.py`: definições de funções extraídas das células anteriores à última.
- `restore.py`: restaura o estado no namespace atual, sem executar os cálculos do notebook.
- `execution.json`: contagem de células executadas e erros, se houver.

O arquivo `variables.pkl` é um snapshot local e não é versionado no Git.
O script `restore.py` depende desse arquivo na mesma pasta; clonar o
repositório não inclui o estado salvo do kernel.

As saídas foram salvas no notebook original. A execução usou um kernel separado da IDE.
A última célula permaneceu intacta e não foi executada. A variável temporária `episode` (namedtuple de iteração) não é serializada.

Foram corrigidas duas dependências da execução sequencial: normalização do fuso nas
datas de MG/2025 (célula 163) e definição das datas da SE 18 a partir do calendário
existente (célula 170). A cópia anterior a qualquer alteração está em
`/tmp/sentinela-notebook-y7wkiti4/model_performance_evaluation.ipynb`.

A célula 241 passou a consultar a probabilidade uma vez por idade distinta.
O cálculo foi comparado com a implementação anterior em oito combinações de atraso
e coluna de completude usando dados reais, com resultados exatamente iguais.

A célula 304, antes vazia, recebeu a chamada de `evaluate_early_signal_case`
para PR/2024, necessária para criar `timeline_pr_2024_v3` e
`evaluation_pr_2024_v3`, usadas pelas células seguintes.

A série completa de SP/2026 (667 linhas e 12 colunas) também foi comparada
com o resultado anterior à otimização, sem qualquer diferença.

Resultado final: 335 células de código executadas com sucesso, zero erros e
315 variáveis salvas. A última célula (357) permaneceu integralmente intacta.
O carregamento pelo script de restauração foi verificado com sucesso.
