# Análise do Cadastro Único 2018 com PySpark

## Sobre o projeto

Este trabalho usa microdados públicos do Cadastro Único de 2018 para observar características das pessoas e famílias registradas, como idade, renda, escolaridade, trabalho e deficiência. Também relaciona os dados municipais aos resultados eleitorais de 2018 do Tribunal Superior Eleitoral (TSE).

Os resultados descrevem os registros do Cadastro Único, e não necessariamente toda a população brasileira. Nas análises eleitorais, a comparação é entre municípios: ela não permite descobrir como uma pessoa ou grupo específico votou, nem comprova uma relação de causa e efeito.

## Etapa 1 — Perfil demográfico e mercado de trabalho

### 1.1 Idade por sexo e cor/raça

| Cor/raça | Sexo | Média (anos) | Mediana | Desvio padrão |
|---|---|---:|---:|---:|
| Branca | Homem | 27,59 | 20,00 | 22,12 |
| Branca | Mulher | 31,29 | 29,00 | 21,45 |
| Preta | Homem | 31,71 | 28,00 | 21,01 |
| Preta | Mulher | 34,76 | 34,00 | 19,09 |
| Amarela | Homem | 27,20 | 20,00 | 21,96 |
| Amarela | Mulher | 30,93 | 29,00 | 20,48 |
| Parda | Homem | 25,58 | 19,00 | 20,04 |
| Parda | Mulher | 28,59 | 26,00 | 19,26 |
| Indígena | Homem | 20,87 | 16,00 | 17,02 |
| Indígena | Mulher | 23,19 | 20,00 | 16,95 |

Em todos os grupos, as mulheres têm média e mediana de idade maiores que os homens. A maior média aparece entre mulheres pretas (34,76 anos), e a menor, entre homens indígenas (20,87 anos). Os desvios padrão mostram que há pessoas de diferentes idades em todos os grupos.

### 1.2 Classificação de trabalho entre pessoas de 18 a 65 anos

| Classificação usada no código | Percentual |
|---|---:|
| Sim | 93,69% |
| Não | 6,31% |

**Atenção:** essa classificação não mede, por si só, trabalho formal e informal. A regra usada combina renda bruta e renda de trabalho; ela não confirma se a pessoa tem carteira assinada. Por isso, esses percentuais não devem ser descritos como taxas de formalidade sem validar a variável e a regra usadas.

### 1.3 Renda bruta anual por curso frequentado e conclusão

A tabela resume a média da renda bruta anual por curso frequentado anteriormente e situação de conclusão. São valores de renda bruta anual, não necessariamente apenas renda do trabalho.

| Curso/escolaridade | Concluiu: Sim (R$) | Concluiu: Não (R$) |
|---|---:|---:|
| Creche | 3.292,17 | 1.405,66 |
| Pré-escola | 2.846,55 | 2.154,97 |
| Alfabetização | 2.461,25 | 2.115,81 |
| Fundamental I | 4.850,94 | 3.574,90 |
| Fundamental II | 5.427,11 | 4.560,32 |
| Fundamental 9 anos | 4.107,99 | 3.863,26 |
| Fundamental Especial | 5.433,12 | 4.175,99 |
| Ensino Médio | 6.739,31 | 5.039,32 |
| Médio Especial | 6.570,74 | 5.106,39 |
| EJA Fundamental I | 3.106,75 | 2.622,58 |
| EJA Fundamental II | 3.807,57 | 3.417,36 |
| EJA Médio | 5.426,70 | 4.914,21 |
| Superior | 10.251,42 | 9.326,86 |
| Alfabetização de adultos | 2.952,17 | 2.154,75 |
| Nenhum | 4.287,55 | 2.940,84 |

A maior média entre as categorias apresentadas é a de Superior. Em todas as linhas, a média dos registros marcados como concluídos é maior que a dos não concluídos. Como a renda apresenta grande variação entre pessoas, a média deve ser interpretada junto com outras medidas, como a mediana.

## Etapa 2 — Trabalho, idade e vulnerabilidade

### 2.1 Pessoas com renda do trabalho por faixa etária

Neste cálculo, considera-se que a pessoa tem trabalho remunerado quando a renda do trabalho é maior que zero.

| Faixa etária | Com renda do trabalho | Sem renda do trabalho |
|---|---:|---:|
| Criança | 2,02% | 97,98% |
| Adolescente | 3,60% | 96,40% |
| Jovem | 32,62% | 67,38% |
| Adulto | 48,16% | 51,84% |
| Idoso | 10,85% | 89,15% |

A maior proporção está entre adultos (48,16%), seguida pelos jovens (32,62%). Entre crianças e adolescentes, os percentuais são menores. Esses valores refletem a renda do trabalho registrada na base e dependem da definição adotada no código.

### 2.2 Pessoas com deficiência por faixa de renda familiar per capita

| Renda familiar per capita | PCD (%) |
|---|---:|
| R$ 0 a menos de R$ 109 | 1,97% |
| R$ 109 a menos de R$ 218 | 2,85% |
| R$ 218 a menos de R$ 477 | 3,19% |
| R$ 477 a menos de R$ 999.999 | 3,75% |

A proporção registrada de PCD cresce entre as faixas mostradas, de 1,97% na menor para 3,75% na maior. É uma associação descritiva: esses números não indicam que a renda cause deficiência ou o contrário. Também é importante confirmar que cada percentual foi calculado usando como denominador as pessoas daquela faixa de renda.

## Etapa 3 — Enriquecimento com resultados eleitorais do TSE

### 3.1 Por que usar essa base?

Os resultados eleitorais acrescentam uma dimensão política aos dados socioeconômicos do Cadastro Único. Ao juntar as bases por município, é possível investigar se características socioeconômicas municipais estão associadas à participação de votos dos partidos. A análise não identifica o voto individual das pessoas cadastradas.

### 3.2 Como as bases foram conectadas

1. O Cadastro Único usa o código de município do IBGE (`CD_IBGE_CADASTRO`), enquanto o arquivo eleitoral usa o código do TSE (`CD_MUNICIPIO`).
2. A tabela `municipio_tse_ibge.csv` permite relacionar `CD_MUNICIPIO_TSE` a `CD_MUNICIPIO_IBGE`.
3. Os códigos são padronizados para cinco dígitos no TSE e sete no IBGE, preservando zeros à esquerda.
4. Um `inner join` mantém apenas os registros eleitorais com correspondência na tabela de códigos.
5. Os votos são agregados por município e partido. Para as análises a seguir, são considerados os resultados para presidente.

### 3.3 Pergunta 1 — Pobreza e participação dos votos

**Pergunta:** Municípios com maior proporção de famílias em situação de pobreza apresentam maior participação de votos de determinados partidos?

A análise usa a proporção de famílias com renda mensal per capita estimada de até R$ 178 e compara esse indicador à participação de votos de cada partido nos municípios.

| Partido | Número | Correlação | Associação observada |
|---|---:|---:|---|
| Partido dos Trabalhadores (PT) | 13 | 0,672 | Positiva forte |
| Partido Democrático Trabalhista (PDT) | 12 | 0,175 | Positiva fraca |
| Patriota | 51 | 0,153 | Positiva fraca |
| Partido Socialista Brasileiro (PSB) | 45 | -0,334 | Negativa moderada |
| Partido Novo | 30 | -0,511 | Negativa relativamente forte |
| Partido Social Liberal (PSL) | 17 | -0,678 | Negativa forte |

**Municípios analisados:** 5.570.

O PT tem correlação positiva (0,672): sua participação nos votos tendia a ser maior em municípios com maior proporção de famílias abaixo do limite de renda usado. O PSL apresenta o padrão oposto (-0,678), assim como o Partido Novo (-0,511). As associações de PDT e Patriota são positivas, mas fracas.

### 3.4 Pergunta 2 — Renda média e participação dos votos

**Pergunta:** A renda mensal per capita média das famílias cadastradas está associada à porcentagem de votos recebida por cada partido na eleição presidencial?

| Partido | Número | Correlação | Associação observada |
|---|---:|---:|---|
| Partido Social Liberal (PSL) | 17 | 0,616 | Positiva forte |
| Partido Novo | 30 | 0,467 | Positiva moderada |
| Podemos | 19 | 0,305 | Positiva moderada a fraca |
| Patriota | 51 | -0,168 | Negativa fraca |
| Partido Democrático Trabalhista (PDT) | 12 | -0,170 | Negativa fraca |
| Partido dos Trabalhadores (PT) | 13 | -0,614 | Negativa forte |

**Municípios analisados:** 5.570.

O PSL apresenta associação positiva (0,616): sua participação nos votos tendia a ser maior em municípios com renda média mais alta entre as famílias cadastradas. Novo e Podemos também apresentam correlações positivas. O PT tem associação negativa (-0,614), indicando uma tendência municipal inversa.

As duas análises apresentam padrões compatíveis: o PT está positivamente associado à proporção de famílias em situação de pobreza e negativamente à renda média; para o PSL, observa-se o contrário. Isso não prova causalidade e não permite afirmar como pessoas pobres ou de maior renda votaram individualmente.

## Etapa 4 — Gráficos

Os gráficos de graphs.py ilustram alguns resultados das Etapas 1 e 2 usando `matplotlib`. Os títulos e os eixos identificam o que está sendo comparado.

## Perguntas específicas do exercício

### 1. Diferença de renda do trabalho por sexo e cor/raça

**Pergunta:** Qual é a diferença na média e na mediana da renda individual do trabalho entre homens e mulheres, agrupados por cor/raça?

| Cor/raça | Sexo | Valor informado em “Diferença” |
|---|---|---:|
| Branca | Homem | 298,05 |
| Branca | Mulher | 178,02 |
| Preta | Homem | 227,67 |
| Preta | Mulher | 162,36 |
| Amarela | Homem | 220,57 |
| Amarela | Mulher | 160,22 |
| Parda | Homem | 191,40 |
| Parda | Mulher | 133,23 |
| Indígena | Homem | 128,70 |
| Indígena | Mulher | 84,28 |

Os valores informados são maiores para homens do que para mulheres em cada categoria. Porém, como a saída apresenta apenas uma coluna chamada “Diferença”, não dá para saber se ela corresponde à diferença entre média e mediana ou à diferença salarial entre os sexos. Para responder completamente à pergunta, é necessário confirmar o cálculo e apresentar as médias e medianas separadamente. A unidade também deve ser identificada como reais, se for o caso.

### 2. Trabalho informal por escolaridade

| Escolaridade | Trabalho informal (%) |
|---|---:|
| Nenhum | 5,51% |
| Fundamental | 6,20% |
| Médio | 7,03% |
| Superior | 6,90% |

A maior taxa reportada é a do ensino médio (7,03%), seguida pelo ensino superior (6,90%). A menor aparece entre pessoas sem instrução (5,51%). A interpretação como informalidade depende da regra utilizada: a classificação baseada apenas em rendas não comprova, por si só, a ausência de carteira assinada.

### 3. Pessoas com deficiência e extrema pobreza por faixa etária

| Faixa etária | Distribuição das PCD (%) | Em extrema pobreza (%) |
|---|---:|---:|
| Crianças e adolescentes (0–17) | 17,09% | 34,42% |
| Jovens (18–29) | 13,97% | 28,23% |
| Adultos (30–59) | 43,09% | 28,99% |
| Idosos (60+) | 25,85% | 28,93% |

Adultos representam a maior parcela das PCD registradas (43,09%). Já crianças e adolescentes apresentam o maior percentual em extrema pobreza: 34,42%, considerando renda familiar per capita de até R$ 89 mensais. A primeira coluna de percentuais descreve a distribuição etária entre as PCD; a segunda descreve a proporção em extrema pobreza dentro de cada faixa.

### 4. Trabalho remunerado de mulheres responsáveis por famílias com crianças pequenas

**Pergunta:** A taxa de trabalho remunerado varia entre mulheres responsáveis por famílias com crianças de 0 a 6 anos e aquelas sem crianças nessa faixa?

| Criança de 0 a 6 anos na família? | Trabalha | Percentual |
|---|---|---:|
| Sim | Sim | 91,51% |
| Sim | Não | 8,49% |
| Não | Sim | 93,21% |
| Não | Não | 6,79% |

A taxa reportada é de 91,51% entre mulheres responsáveis em famílias com crianças pequenas e de 93,21% entre aquelas sem crianças nessa faixa, uma diferença de 1,70 ponto percentual. É uma diferença descritiva e não prova que ter crianças pequenas cause redução na ocupação. O resultado também depende da definição de trabalho remunerado usada no código.

## Conclusão

Os dados mostram diferenças de idade, renda e trabalho entre grupos do Cadastro Único. Adultos têm a maior proporção de registros com renda do trabalho, a renda bruta anual média mais alta aparece na categoria de curso superior, e crianças e adolescentes com deficiência apresentam o maior percentual de extrema pobreza entre as faixas analisadas.

No cruzamento eleitoral, a participação de votos do PT esteve mais associada a municípios com maior pobreza e menor renda média entre as famílias cadastradas; para o PSL, observou-se o padrão oposto. Esses resultados ajudam a descrever diferenças entre municípios, mas não explicam, sozinhos, por que as pessoas votaram de determinada maneira. As conclusões também dependem da qualidade das variáveis e das regras usadas para classificar renda, trabalho e escolaridade.
