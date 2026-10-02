import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('titanic.csv')

# Idade por gênero
idade_sexo = df.groupby('Sex')['Age']

print("- Idade por gênero:")

print(f"\nMédia:\n{idade_sexo.mean()}")
print(f"\nMediana:\n{idade_sexo.median()}")
print(f"\nDesvio padrão:\n{idade_sexo.std()}")

# Interpretação:
# As médias e medianas permitem comparar a idade dos passageiros
# entre homens e mulheres. O desvio padrão mostra a variação das idades.


# Idade por classe social
idade_classe = df.groupby('Pclass')['Age']

print("\n\n- Idade por classe social:")

print(f"\nMédia:\n{idade_classe.mean()}")
print(f"\nMediana:\n{idade_classe.median()}")
print(f"\nDesvio padrão:\n{idade_classe.std()}")

# Interpretação:
# Podemos comparar a idade dos passageiros entre as três classes.
# O desvio padrão mostra o quanto as idades variam em cada classe.


# Idade por gênero e classe social
idade_sexo_classe = df.groupby(['Sex', 'Pclass'])['Age']

print("\n\n- Idade por gênero e classe social:")

print(f"\nMédia:\n{idade_sexo_classe.mean()}")
print(f"\nMediana:\n{idade_sexo_classe.median()}")
print(f"\nDesvio padrão:\n{idade_sexo_classe.std()}")

# Interpretação:
# Essa análise permite observar as diferenças de idade considerando
# gênero e classe social ao mesmo tempo.


# Separação das faixas etárias
crianca = df[df['Age'] <= 15]
jovem = df[(df['Age'] > 15) & (df['Age'] <= 30)]
adulto = df[(df['Age'] > 30) & (df['Age'] <= 60)]
idoso = df[df['Age'] > 60]

# Seleção dos sobreviventes de cada faixa
crianca_viva = crianca[crianca['Survived'] == 1]
jovem_vivo = jovem[jovem['Survived'] == 1]
adulto_vivo = adulto[adulto['Survived'] == 1]
idoso_vivo = idoso[idoso['Survived'] == 1]


# Taxa de sobrevivência por faixa etária
taxa_crianca = len(crianca_viva) / len(crianca)
taxa_jovem = len(jovem_vivo) / len(jovem)
taxa_adulto = len(adulto_vivo) / len(adulto)
taxa_idoso = len(idoso_vivo) / len(idoso)

print("\n\n- Taxa de sobrevivência por faixa etária:")

print(f"\nCrianças: {taxa_crianca:.2%}")
print(f"Jovens: {taxa_jovem:.2%}")
print(f"Adultos: {taxa_adulto:.2%}")
print(f"Idosos: {taxa_idoso:.2%}")

# Interpretação:
# A comparação das taxas mostra quais faixas etárias tiveram
# maior e menor proporção de sobreviventes.


# Separação entre sobreviventes e não sobreviventes
sobreviventes = df[df['Survived'] == 1]
nao_sobreviventes = df[df['Survived'] == 0]


# Tarifa por sobrevivência
print("\n\n- Tarifa por sobrevivência:")

print("\nSobreviventes:")
print(f"Média: {sobreviventes['Fare'].mean():.2f}")
print(f"Variância: {sobreviventes['Fare'].var():.2f}")
print(f"Desvio padrão: {sobreviventes['Fare'].std():.2f}")

print("\nNão sobreviventes:")
print(f"Média: {nao_sobreviventes['Fare'].mean():.2f}")
print(f"Variância: {nao_sobreviventes['Fare'].var():.2f}")
print(f"Desvio padrão: {nao_sobreviventes['Fare'].std():.2f}")

# Interpretação:
# A média permite comparar as tarifas pagas pelos dois grupos.
# A variância e o desvio padrão mostram a dispersão dos valores.


# Correlação entre tarifa e sobrevivência
correlacao = df['Fare'].corr(df['Survived'])

print(f"\nCorrelação entre tarifa e sobrevivência: {correlacao:.2f}")

# Interpretação:
# A correlação indica se existe uma relação entre o valor da tarifa
# e a sobrevivência. Quanto mais próximo de 1 ou -1, mais forte é a relação.


# Gráfico de idade por gênero e classe
df.boxplot(column='Age', by=['Sex', 'Pclass'])

plt.title('Distribuição de Idade por Gênero e Classe Social')
plt.suptitle('')
plt.xlabel('Gênero e Classe Social')
plt.ylabel('Idade')
plt.show()

# O boxplot permite comparar a distribuição das idades dos grupos.


# Gráfico da taxa de sobrevivência
faixas = ['Crianças', 'Jovens', 'Adultos', 'Idosos']

taxas = [
    taxa_crianca,
    taxa_jovem,
    taxa_adulto,
    taxa_idoso
]

plt.bar(faixas, taxas)

plt.title('Taxa de Sobrevivência por Faixa Etária')
plt.xlabel('Faixa Etária')
plt.ylabel('Taxa de Sobrevivência')
plt.ylim(0, 1)

plt.show()

# As barras facilitam a comparação das taxas de sobrevivência.


# Gráfico da tarifa por sobrevivência
plt.boxplot(
    [nao_sobreviventes['Fare'], sobreviventes['Fare']],
    tick_labels=['Não sobreviventes', 'Sobreviventes']
)

plt.title('Distribuição da Tarifa por Sobrevivência')
plt.xlabel('Sobrevivência')
plt.ylabel('Tarifa')
plt.show()

# O boxplot permite comparar a distribuição das tarifas
# entre sobreviventes e não sobreviventes.
