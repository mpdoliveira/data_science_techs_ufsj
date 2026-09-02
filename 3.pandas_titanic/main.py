import pandas as pd

df = pd.read_csv('titanic.csv')

idade_sexo = df.groupby('Sex')['Age']

print("Idade por gênero:")
print(f"\nMédia:\n{idade_sexo.mean()}")
print(f"\nMediana:\n{idade_sexo.median()}")
print(f"\nDesvio padrão:\n{idade_sexo.std()}")


idade_classe = df.groupby('Pclass')['Age']

print("\n\nIdade por classe social:")
print(f"\nMédia:\n{idade_classe.mean()}")
print(f"\nMediana:\n{idade_classe.median()}")
print(f"\nDesvio padrão:\n{idade_classe.std()}")


idade_sexo_classe = df.groupby(['Sex', 'Pclass'])['Age']

print("\n\nIdade por gênero e classe social:")
print(f"\nMédia:\n{idade_sexo_classe.mean()}")
print(f"\nMediana:\n{idade_sexo_classe.median()}")
print(f"\nDesvio padrão:\n{idade_sexo_classe.std()}")


crianca = df[df['Age'] <= 15]
jovem = df[(df['Age'] > 15) & (df['Age'] <= 30)]
adulto = df[(df['Age'] > 30) & (df['Age'] <= 60)]
idoso = df[df['Age'] > 60]

crianca_viva = df[(df['Age'] <= 15) & (df['Survived'] == 1)]
jovem_vivo = df[(df['Age'] > 15) & (df['Age'] <= 30) & (df['Survived'] == 1)]
adulto_vivo = df[(df['Age'] > 30) & (df['Age'] <= 60) & (df['Survived'] == 1)]
idoso_vivo = df[(df['Age'] > 60) & (df['Survived'] == 1)]

