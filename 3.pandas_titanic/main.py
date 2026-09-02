import pandas as pd

df = pd.read_csv('titanic.csv')

idade_sexo = df.groupby('Sex')['Age']

print("- Idade por gênero:")
print(f"\nMédia:\n{idade_sexo.mean()}")
print(f"\nMediana:\n{idade_sexo.median()}")
print(f"\nDesvio padrão:\n{idade_sexo.std()}")

idade_classe = df.groupby('Pclass')['Age']

print("\n\n- Idade por classe social:")
print(f"\nMédia:\n{idade_classe.mean()}")
print(f"\nMediana:\n{idade_classe.median()}")
print(f"\nDesvio padrão:\n{idade_classe.std()}")

idade_sexo_classe = df.groupby(['Sex', 'Pclass'])['Age']

print("\n\n- Idade por gênero e classe social:")
print(f"\nMédia:\n{idade_sexo_classe.mean()}")
print(f"\nMediana:\n{idade_sexo_classe.median()}")
print(f"\nDesvio padrão:\n{idade_sexo_classe.std()}")

crianca = df[df['Age'] <= 15]
jovem = df[(df['Age'] > 15) & (df['Age'] <= 30)]
adulto = df[(df['Age'] > 30) & (df['Age'] <= 60)]
idoso = df[df['Age'] > 60]

crianca_viva = crianca[crianca['Survived'] == 1]
jovem_vivo = jovem[jovem['Survived'] == 1]
adulto_vivo = adulto[adulto['Survived'] == 1]
idoso_vivo = idoso[idoso['Survived'] == 1]

print("\n\n- Taxa de sobrevivência por faixa etária:")
print(f"\nCrianças: {len(crianca_viva) / len(crianca):.2%}")
print(f"Jovens: {len(jovem_vivo) / len(jovem):.2%}")
print(f"Adultos: {len(adulto_vivo) / len(adulto):.2%}")
print(f"Idosos: {len(idoso_vivo) / len(idoso):.2%}")

sobreviventes = df[df['Survived'] == 1]
nao_sobreviventes = df[df['Survived'] == 0]

print("\n\n- Tarifa por sobrevivência:")

print(f"\nSobreviventes:")
print(f"Média: {sobreviventes['Fare'].mean():.2f}")
print(f"Variância: {sobreviventes['Fare'].var():.2f}")
print(f"Desvio padrão: {sobreviventes['Fare'].std():.2f}")

print(f"\nNão sobreviventes:")
print(f"Média: {nao_sobreviventes['Fare'].mean():.2f}")
print(f"Variância: {nao_sobreviventes['Fare'].var():.2f}")
print(f"Desvio padrão: {nao_sobreviventes['Fare'].std():.2f}")

correlacao = df['Fare'].corr(df['Survived'])

print(f"\nCorrelação entre tarifa e sobrevivência: {correlacao:.2f}")
