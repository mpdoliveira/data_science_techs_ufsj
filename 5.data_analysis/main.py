import pandas
import json
from datetime import date

data = pandas.read_csv("PESSOA_2018.TXT", delimiter=";", nrows=10000, usecols=["CO_SEXO_PESSOA", "CO_RACA_COR_PESSOA", "DT_NASC_PESSOA"])
df = pandas.DataFrame(data)

with open("label.json", encoding="utf-8") as file:
    config = json.load(file)

    df["DT_NASC_PESSOA"] = pandas.to_datetime(df["DT_NASC_PESSOA"])

year = 2018
df["age"] = year - df["DT_NASC_PESSOA"].dt.year

df["age_groups"] = pandas.cut(
    df["age"],
    bins=config["age_groups"]["delimiters"],
    labels=config["age_groups"]["labels"],
    include_lowest=True
)

sex_race_groups = df.groupby(["CO_SEXO_PESSOA", "CO_RACA_COR_PESSOA"])

print(sex_race_groups["age_groups"].value_counts())
print(sex_race_groups["age"].mean())
print(sex_race_groups["age"].median())
print(sex_race_groups["age"].std())