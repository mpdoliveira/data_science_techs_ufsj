import pandas as pd
import matplotlib.pyplot as plt

# Idade média por sexo e cor/raça
idade = pd.DataFrame(
    {
        "Cor/raça": ["Branca", "Preta", "Amarela", "Parda", "Indígena"],
        "Homem": [27.59, 31.71, 27.20, 25.58, 20.87],
        "Mulher": [31.29, 34.76, 30.93, 28.59, 23.19],
    }
).set_index("Cor/raça")
ax = idade.plot(kind="bar")
ax.set_title("Idade média por sexo e cor/raça — Cadastro Único 2018")
ax.set_xlabel("Cor/raça")
ax.set_ylabel("Idade média (anos)")
ax.legend(title="Sexo")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# Renda bruta anual média por faixa etária
trabalho = pd.DataFrame(
    {
        "Faixa etária": ["Criança", "Adolescente", "Jovem", "Adulto", "Idoso"],
        "Com renda do trabalho (%)": [2.02, 3.60, 32.62, 48.16, 10.85],
    }
)
plt.figure()
plt.bar(trabalho["Faixa etária"], trabalho["Com renda do trabalho (%)"])
plt.title("Pessoas com renda do trabalho por faixa etária")
plt.xlabel("Faixa etária")
plt.ylabel("Pessoas com renda do trabalho (%)")
plt.tight_layout()
plt.show()

# PCD por faixa de renda familiar per capita
pcd = pd.DataFrame(
    {
        "Faixa de renda (R$)": ["0–109", "109–218", "218–477", "477 ou mais"],
        "PCD (%)": [1.97, 2.85, 3.19, 3.75],
    }
)
plt.figure()
plt.bar(pcd["Faixa de renda (R$)"], pcd["PCD (%)"])
plt.title("Proporção registrada de PCD por faixa de renda familiar")
plt.xlabel("Renda familiar per capita (R$)")
plt.ylabel("PCD (%)")
plt.tight_layout()
plt.show()
