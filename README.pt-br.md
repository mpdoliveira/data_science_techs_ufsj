[English](README.md) | [Português](README.pt-BR.md)

# Tecnologias para Ciência de Dados — UFSJ

Este repositório reúne projetos desenvolvidos para a disciplina optativa de **Tecnologias para Ciência de Dados** da Universidade Federal de São João del-Rei (UFSJ), ministrada pela Prof.ª Carolina Xavier.

As atividades exploram diferentes áreas da Ciência de Dados, incluindo clusterização, análise de grafos, análise exploratória de dados, pesquisa científica, análise estatística e processamento distribuído de dados.

## Atividades

### Atividade 1 — K-Means

Implementação do **algoritmo de clusterização K-Means do zero utilizando Python nativo**.

O principal objetivo desta atividade foi compreender a lógica interna do algoritmo, em vez de utilizar bibliotecas prontas de Machine Learning.

Principais conceitos:

- Aprendizado não supervisionado
- Clusterização
- Distância Euclidiana
- Cálculo de centroides
- Algoritmos iterativos
- Critérios de convergência
- Processamento de dados CSV

O algoritmo foi implementado sem o uso de bibliotecas como Scikit-learn, NumPy, Pandas ou SciPy.

Diretório: [`activity_1_kmeans/`](./activity_1_kmeans/)

---

### Atividade 2 — Label Propagation

Implementação de um **algoritmo de detecção de comunidades baseado em Label Propagation**.

O projeto explora estruturas de grafos e detecção de comunidades por meio da propagação iterativa de rótulos entre vértices vizinhos até a convergência.

Principais conceitos:

- Grafos e redes
- Matrizes de adjacência
- Detecção de comunidades
- Label Propagation
- NumPy
- NetworkX
- Ambientes virtuais com Conda
- Fluxo de trabalho com Git e GitHub

O algoritmo de Label Propagation foi implementado manualmente, em vez de utilizar uma implementação pronta de detecção de comunidades.

Diretório: [`activity_2_label_propagation/`](./activity_2_label_propagation/)

---

### Atividade 3 — Análise do Titanic com Pandas

Análise Exploratória de Dados do **dataset do Titanic utilizando Pandas**.

A atividade investiga padrões demográficos e socioeconômicos associados à sobrevivência dos passageiros.

Principais análises:

- Distribuição de idade por sexo e classe dos passageiros
- Média, mediana e desvio padrão
- Taxa de sobrevivência por faixa etária
- Relação entre tarifa da passagem e sobrevivência
- Comparação entre sobreviventes e não sobreviventes
- Visualização de dados

Principais tecnologias:

- Python
- Pandas
- Matplotlib

A atividade é focada em manipulação de dados, agregações, estatística descritiva e visualização.

Diretório: [`activity_3_titanic_pandas/`](./activity_3_titanic_pandas/)

---

### Atividade 4 — Seminário de Ciência de Dados

Seminário técnico baseado em um artigo científico recente nas áreas de **Ciência de Dados, Inteligência Artificial ou Machine Learning**.

A atividade é focada na leitura, compreensão, análise crítica e comunicação de pesquisa científica.

A apresentação aborda:

- Definição e contextualização do problema
- Metodologia
- Arquitetura do modelo ou pipeline de dados
- Resultados experimentais
- Métricas de desempenho
- Limitações
- Conclusões e trabalhos futuros

Diretório: [`activity_4_seminar/`](./activity_4_seminar/)

---

### Atividade 5 — Análise do Cadastro Único com PySpark

Análise exploratória dos **microdados públicos do Cadastro Único de 2018**.

A atividade original foi proposta utilizando Pandas, mas a implementação deste repositório foi adaptada para **PySpark**, com o objetivo de explorar processamento distribuído de dados e trabalhar de forma mais eficiente com o conjunto de dados completo.

A análise inclui:

- Estatísticas de idade agrupadas por sexo e cor/raça
- Análise de trabalho formal e informal
- Taxa de ocupação por faixa etária
- Análise de renda por nível de escolaridade
- Agregação de renda familiar
- Cálculo de renda familiar per capita
- Distribuição de pessoas com deficiência entre faixas de renda
- Tratamento de valores ausentes
- Mapeamento de categorias
- Agrupamento de dados em faixas

Principais tecnologias e conceitos de PySpark:

- Python
- PySpark
- Apache Spark
- Spark SQL
- Spark ML `Bucketizer`
- Window functions
- Transformações e agregações em DataFrames
- Mapeamento de categorias baseado em JSON

Diretório: [`activity_5_pyspark/`](./activity_5_pyspark/)

---

## Tecnologias

Tecnologias e conceitos explorados ao longo do repositório:

- Python
- Pandas
- PySpark
- Apache Spark
- NumPy
- NetworkX
- Matplotlib
- Conda
- Ambientes virtuais Python
- Git
- GitHub
- Análise Exploratória de Dados
- Análise estatística
- Clusterização
- Algoritmos em grafos
- Detecção de comunidades
- Processamento distribuído de dados

## Estrutura do Repositório

```text
data_science_techs_ufsj/
├── activity_1_kmeans/
├── activity_2_label_propagation/
├── activity_3_titanic_pandas/
├── activity_4_seminar/
├── activity_5_pyspark/
├── .gitattributes
├── README.md
└── README.pt-BR.md
```
