[English](README.md) | [Português](README.pt-BR.md)

# Análise do Cadastro Único 2018 com PySpark

## Visão geral

Este projeto analisa os **microdados públicos do Cadastro Único de 2018** utilizando **PySpark**. Foi desenvolvido como Atividade 5 da disciplina _Tecnologias para Ciência de Dados_ da Universidade Federal de São João del-Rei (UFSJ).

A atividade original especificava o uso de Pandas. Esta implementação utiliza PySpark para processar tanto uma amostra quanto o conjunto de dados completo.

## Análises

O projeto implementa as seguintes análises:

1. Distribuição de idade por sexo e cor/raça.
2. Classificação baseada em renda do trabalho entre indivíduos de 18 a 65 anos.
3. Renda bruta anual por categoria de escolaridade e situação de conclusão.
4. Trabalho remunerado por faixa etária.
5. Proporção de pessoas com deficiência (PCD) por faixa de renda familiar per capita.

## Tecnologias

- Python
- PySpark
- Apache Spark
- Spark SQL
- Spark ML `Bucketizer`
- Spark Window functions
- Mapeamentos categóricos baseados em JSON

## Estrutura do projeto

```text
activity_5_pyspark/
├── main.py
├── labels.json
├── amostra.csv/
└── README.md
```

O arquivo `labels.json` armazena os nomes das colunas do conjunto de dados, os mapeamentos categóricos e as definições de intervalos utilizadas nas análises.

## Execução do projeto

### Amostra

```bash
python main.py
```

Entrada padrão:

```text
amostra.csv/*.csv
```

### Conjunto de dados completo

O arquivo completo `PESSOA_2018.TXT` utiliza `;` como delimitador:

```bash
python main.py "C:\caminho\para\PESSOA_2018.TXT" ";"
```

## Processamento dos dados

### Idade

A idade é aproximada a partir do ano de referência:

```text
idade = 2018 - ano de nascimento
```

Registros com idade calculada fora do intervalo `0–130` são excluídos.

| Faixa etária | Intervalo |
| ------------ | --------: |
| Criança      |      0–12 |
| Adolescente  |     13–19 |
| Jovem        |     20–29 |
| Adulto       |     30–59 |
| Idoso        |    60–130 |

### Variáveis categóricas

Códigos numéricos são convertidos em rótulos descritivos por meio de expressões `map` do Spark e dos mapeamentos armazenados em `labels.json`.

Exemplos:

```text
Sexo
1 → Homem
2 → Mulher
```

```text
Cor/raça
1 → Branca
2 → Preta
3 → Amarela
4 → Parda
5 → Indígena
```

### Renda familiar per capita

A renda anual é agregada pelo identificador da família e convertida em uma estimativa de renda mensal familiar per capita:

```text
renda mensal familiar per capita = renda anual familiar / número de membros / 12
```

Faixas de renda utilizadas:

| Grupo | Renda mensal familiar per capita |
| ----- | -------------------------------: |
| 1     |            R$ 0 ≤ renda < R$ 109 |
| 2     |          R$ 109 ≤ renda < R$ 218 |
| 3     |          R$ 218 ≤ renda < R$ 477 |
| 4     |      R$ 477 ≤ renda < R$ 999.999 |

R$ 477 corresponde à metade do salário mínimo de 2018 utilizado como referência nesta análise.

---

# Resultados

## 1. Distribuição de idade por sexo e cor/raça

| Cor/Raça | Sexo   | Média | Mediana | Desvio padrão |
| -------- | ------ | ----: | ------: | ------------: |
| Branca   | Homem  | 27,59 |   20,00 |         22,12 |
| Branca   | Mulher | 31,29 |   29,00 |         21,45 |
| Preta    | Homem  | 31,71 |   28,00 |         21,01 |
| Preta    | Mulher | 34,76 |   34,00 |         19,09 |
| Amarela  | Homem  | 27,20 |   20,00 |         21,96 |
| Amarela  | Mulher | 30,93 |   29,00 |         20,48 |
| Parda    | Homem  | 25,58 |   19,00 |         20,04 |
| Parda    | Mulher | 28,59 |   26,00 |         19,26 |
| Indígena | Homem  | 20,87 |   16,00 |         17,02 |
| Indígena | Mulher | 23,19 |   20,00 |         16,95 |

### Resultado

As mulheres apresentam média e mediana de idade superiores às dos homens em todos os grupos de cor/raça. Mulheres pretas apresentam a maior média de idade (`34,76`), enquanto homens indígenas apresentam a menor (`20,87`). Os desvios padrão variam entre `16,95` e `22,12`, indicando elevada dispersão etária em todos os grupos.

---

## 2. Classificação baseada em renda do trabalho entre indivíduos de 18 a 65 anos

| Classificação atual | Percentual |
| ------------------- | ---------: |
| Sim                 |     93,69% |
| Não                 |      6,31% |

### Nota metodológica

A implementação atual **não identifica diretamente trabalho formal e informal**. Os registros são classificados como `Não` quando a renda bruta anual é diferente de zero e a renda do trabalho é igual a zero; os demais registros são classificados como `Sim`.

Portanto, os percentuais acima não devem ser interpretados como uma estimativa válida de trabalho formal versus informal. Para responder à questão original, é necessário utilizar uma variável ou regra que represente diretamente a formalidade do vínculo de trabalho.

---

## 3. Renda bruta anual por categoria de escolaridade

As estatísticas de renda são agrupadas pela categoria de curso frequentado anteriormente e pela situação de conclusão correspondente.

| Escolaridade          | Concluiu |     Média |   Mediana | Desvio padrão |
| --------------------- | -------- | --------: | --------: | ------------: |
| Creche                | Sim      |  3.292,17 |  1.820,00 |      3.729,92 |
| Creche                | Não      |  1.405,66 |    900,00 |      1.653,52 |
| Pré-escola            | Sim      |  2.846,55 |  1.300,00 |      3.722,66 |
| Pré-escola            | Não      |  2.154,97 |  1.000,00 |      2.964,04 |
| Alfabetização         | Sim      |  2.461,25 |  1.200,00 |      3.356,18 |
| Alfabetização         | Não      |  2.115,81 |  1.200,00 |      3.110,43 |
| Fundamental I         | Sim      |  4.850,94 |  2.500,00 |      5.716,49 |
| Fundamental I         | Não      |  3.574,90 |  1.800,00 |      4.709,73 |
| Fundamental II        | Sim      |  5.427,11 |  3.012,00 |      6.003,69 |
| Fundamental II        | Não      |  4.560,32 |  2.400,00 |      5.353,12 |
| Fundamental 9 anos    | Sim      |  4.107,99 |  2.000,00 |      5.156,41 |
| Fundamental 9 anos    | Não      |  3.863,26 |  1.800,00 |      5.148,66 |
| Fundamental Especial  | Sim      |  5.433,12 |  2.640,00 |      6.682,64 |
| Fundamental Especial  | Não      |  4.175,99 |  2.000,00 |      5.379,35 |
| Ensino Médio          | Sim      |  6.739,31 |  4.400,00 |      6.989,25 |
| Ensino Médio          | Não      |  5.039,32 |  2.800,00 |      5.699,39 |
| Médio Especial        | Sim      |  6.570,74 |  3.600,00 |      7.509,66 |
| Médio Especial        | Não      |  5.106,39 |  2.400,00 |      6.168,80 |
| EJA Fundamental I     | Sim      |  3.106,75 |  1.455,00 |      4.122,45 |
| EJA Fundamental I     | Não      |  2.622,58 |  1.200,00 |      3.656,59 |
| EJA Fundamental II    | Sim      |  3.807,57 |  2.000,00 |      4.555,03 |
| EJA Fundamental II    | Não      |  3.417,36 |  1.800,00 |      4.530,67 |
| EJA Médio             | Sim      |  5.426,70 |  3.600,00 |      5.603,10 |
| EJA Médio             | Não      |  4.914,21 |  2.880,00 |      5.368,28 |
| Superior              | Sim      | 10.251,42 | 10.307,00 |      8.891,10 |
| Superior              | Não      |  9.326,86 |  9.000,00 |      8.427,37 |
| Alfabetização Adultos | Sim      |  2.952,17 |  1.200,00 |      4.449,89 |
| Alfabetização Adultos | Não      |  2.154,75 |  1.020,00 |      3.187,98 |
| Nenhum                | Sim      |  4.287,55 |  2.400,00 |      4.981,06 |
| Nenhum                | Não      |  2.940,84 |  1.800,00 |      3.351,01 |

### Resultado

A categoria `Superior` apresenta a maior média e mediana de renda bruta anual. Em todas as categorias apresentadas, a renda média é maior entre os registros marcados como concluídos do que entre os não concluídos. Os elevados desvios padrão indicam ampla dispersão de renda dentro das categorias.

---

## 4. Trabalho remunerado por faixa etária

Trabalho remunerado é definido como renda do trabalho maior que zero.

| Faixa etária | Trabalha | Percentual |
| ------------ | -------- | ---------: |
| Criança      | Sim      |      2,02% |
| Criança      | Não      |     97,98% |
| Adolescente  | Sim      |      3,60% |
| Adolescente  | Não      |     96,40% |
| Jovem        | Sim      |     32,62% |
| Jovem        | Não      |     67,38% |
| Adulto       | Sim      |     48,16% |
| Adulto       | Não      |     51,84% |
| Idoso        | Sim      |     10,85% |
| Idoso        | Não      |     89,15% |

### Resultado

Adultos apresentam a maior proporção de registros com renda do trabalho (`48,16%`), seguidos por jovens (`32,62%`). As proporções são de `10,85%` entre idosos, `3,60%` entre adolescentes e `2,02%` entre crianças.

---

## 5. Pessoas com deficiência por renda familiar per capita

| Renda familiar per capita   |   PCD |
| --------------------------- | ----: |
| R$ 0 ≤ renda < R$ 109       | 1,97% |
| R$ 109 ≤ renda < R$ 218     | 2,85% |
| R$ 218 ≤ renda < R$ 477     | 3,19% |
| R$ 477 ≤ renda < R$ 999.999 | 3,75% |

### Resultado

A proporção observada de pessoas com deficiência aumenta entre as quatro faixas de renda, de `1,97%` na faixa mais baixa para `3,75%` na mais alta. Trata-se de uma associação descritiva e não de evidência de causalidade.

---

## Implementação

- `spark_map()` converte valores categóricos codificados em rótulos legíveis por meio de expressões Spark.
- `spark_bucketizer()` aplica o Spark ML `Bucketizer` e associa os índices das faixas aos respectivos rótulos.
- Spark Window functions são utilizadas para calcular percentuais relativos aos grupos sem a necessidade de novas junções após a agregação.
- `labels.json` centraliza os mapeamentos categóricos e as definições de intervalos.

## Limitações metodológicas

- A idade é aproximada a partir do ano de nascimento; o dia e o mês de nascimento não são considerados.
- Registros com idade calculada fora do intervalo `0–130` são excluídos.
- Valores ausentes são excluídos conforme as variáveis exigidas em cada análise.
- A classificação atual de trabalho formal/informal não mede diretamente a formalidade do vínculo e deve ser revisada antes de se tirar conclusões sobre trabalho formal.
- A análise de escolaridade utiliza renda bruta anual (`VL_RENDA_BRUTA_12_MESES_MEMB`), e não renda do trabalho.
- A variável de escolaridade representa o curso frequentado anteriormente e sua situação de conclusão; não deve ser interpretada automaticamente como o maior nível de escolaridade concluído sem confirmação no dicionário da base.
- Na análise de PCD, registros sem informação de deficiência são removidos antes do cálculo do tamanho da família. Consequentemente, a estimativa do número de membros e da renda per capita pode ser afetada quando essa informação está ausente.
- Os resultados descrevem os registros analisados do Cadastro Único e não devem ser generalizados para a população brasileira sem um desenho amostral e procedimento de ponderação apropriados.

## Extensões possíveis

- Adicionar visualizações para as análises apresentadas.
- Definir um schema explícito no Spark em vez de utilizar `inferSchema=True`.
- Validar códigos categóricos e limites dos intervalos com o dicionário oficial da base.
- Refinar o tratamento de valores ausentes.
- Integrar indicadores municipais utilizando o código IBGE do município.
- Exportar os resultados processados para CSV ou Parquet.
- Adicionar testes automatizados para as funções auxiliares e os mapeamentos categóricos.
