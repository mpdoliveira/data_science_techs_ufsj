# Análise de dados das IFES

Neste trabalho, analisei dados de investimento e de vagas nas Instituições Federais de Ensino Superior (IFES), de 1996 a 2026. Organizei a análise em quatro atividades, usando Pandas para trabalhar com os dados e Matplotlib e Seaborn para os gráficos.

## 1. Carregamento e exploração dos dados

Comecei verificando as colunas, os tipos de valores e os mínimos e máximos de cada variável. Também consultei as primeiras linhas para entender como os dados estavam organizados. Nesta etapa, não usei gráficos porque o objetivo era conhecer a estrutura da base antes de fazer comparações ou procurar tendências.

## 2. Evolução temporal e escala

Escolhi gráficos de linhas para mostrar a evolução do investimento total e das vagas de estudantes. Como os dados são anuais, ligar os pontos ajuda a enxergar os períodos de crescimento, queda e estabilidade.

Fiz um gráfico para cada variável porque elas têm unidades e escalas diferentes: investimento em bilhões de reais e vagas em quantidade de estudantes. Assim, a leitura fica mais clara e uma escala não atrapalha a outra.

## 3. Proporção da força de trabalho

Usei um gráfico de linhas com duas séries: vagas de estudantes por vaga docente e vagas de estudantes por vaga de TAE. As duas proporções têm a mesma unidade, então faz sentido colocá-las no mesmo gráfico e comparar como mudaram ao longo dos anos.

Mantive cores diferentes apenas para distinguir as duas linhas. Dessa forma, consigo observar quando as proporções se aproximam, se afastam ou seguem tendências parecidas.

## 4. Correlação entre assistência estudantil e vagas

Agrupei os dados em períodos presidenciais de quatro anos e usei `agg()` para calcular média, mediana e soma do investimento em assistência estudantil e das vagas de estudantes. Como a base começa em 1996, o primeiro período tem apenas três anos disponíveis.

Escolhi um gráfico de dispersão com bolhas porque queria observar a relação entre duas variáveis: o investimento médio anual em assistência estudantil e a média anual de vagas. Cada ponto representa um período, e o tamanho da bolha mostra a assistência calculada por vaga. Assim, essa terceira informação tem uma função no gráfico, em vez de ser apenas um efeito visual.

Mantive todos os pontos na mesma cor e identifiquei os períodos por rótulos, já que cores diferentes não eram necessárias. Preferi esse gráfico ao mapa de calor porque ele permite observar diretamente a distribuição dos períodos e possíveis diferenças entre eles. Ainda assim, a associação visual não prova, por si só, que um aumento no investimento causou um aumento nas vagas ou que ambos cresceram na mesma proporção.

## 5. Filtragem condicional de anos críticos

Calculei a variação percentual anual da assistência estudantil e das vagas de estudantes e usei `groupby('ano').filter()` para manter apenas os anos em que a assistência caiu ou ficou praticamente parada (variação de até +1%) enquanto as vagas aumentaram. O limite de 1% para "estagnação" é uma escolha minha. Foram identificados 11 anos: 1997, 1999, 2001, 2015 a 2020, 2022 e 2026. O ano de 2021 ficou de fora porque as vagas também recuaram. Em 1997, 1999 e 2001 os valores são muito pequenos e parte da estagnação pode ser arredondamento.

Para destacar esses anos, usei a linha do tempo da assistência estudantil com três recursos: marcadores em X vermelhos nos anos críticos (a mudança de forma, além da cor, ajuda quem tem daltonismo), sombreamento de fundo nas faixas de anos consecutivos (como 2015-2020) e setas anotando o pico de 2014 e a exceção de 2021. O eixo y começa em zero para que a queda seja lida na proporção correta.

## 6. Métricas customizadas com `apply` e paleta de cores

Criei uma função e a apliquei com `apply()` para classificar cada ano pela variação do investimento total em relação ao ano anterior: Retração Orçamentária (menor que 0%), Média Expansão (de 0% até 5%) e Alta Expansão (a partir de 5%). Os limites são escolhas analíticas, e o CSV não informa se os valores são correntes ou deflacionados. O primeiro ano (1996) fica sem categoria por não ter ano anterior.

Usei um gráfico de barras por ano com uma paleta divergente do seaborn (`sb.diverging_palette`): o vermelho indica retração e o azul indica expansão, com o tom mais escuro para a Alta Expansão. Como as categorias têm um ponto de virada natural (o zero), uma paleta divergente deixa a direção do fenômeno visível sem depender da legenda. Uma paleta qualitativa trataria as categorias como equivalentes, e uma sequencial esconderia a diferença entre crescer e encolher.

## 7. Relatório visual

O notebook `7_relatorio_visual.ipynb` reúne todos os gráficos. Cada um vem acompanhado de duas partes: "O fato" (o que os dados mostram) e "O design" (por que aquele tipo de gráfico, paleta, limites de eixo e legenda foram a melhor escolha)