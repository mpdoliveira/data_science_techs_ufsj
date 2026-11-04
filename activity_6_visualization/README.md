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
