import pandas
import json
from datetime import date

def sex_race_age(data=None) :
    if not data:
        data = pandas.read_csv(
            "PESSOA_2018.TXT",
            delimiter=";",
            nrows=10000,
            usecols=[
                "CO_SEXO_PESSOA",
                "CO_RACA_COR_PESSOA",
                "DT_NASC_PESSOA"
            ]
        )

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

    agregation = sex_race_groups["age"].agg(
        ["mean", "median", "std"]
    )
    print(agregation)

    print(sex_race_groups["age_groups"].value_counts())


def work_type(data=None):
    if not data:
        data = pandas.read_csv(
            "PESSOA_2018.TXT",
            delimiter=";",
            nrows=10000,
            usecols=[
                "CO_CONCLUIU_FREQUENTOU_MEMB",
                "CO_CURSO_FREQ_PESSOA_MEMB",
                "VL_RENDA_BRUTA_12_MESES_MEMB"
            ]
        )

    df = pandas.DataFrame(data)

    level_education = df.groupby([
        "CO_CURSO_FREQ_PESSOA_MEMB",
        "CO_CONCLUIU_FREQUENTOU_MEMB"
    ])

    print(level_education["VL_RENDA_BRUTA_12_MESES_MEMB"].mean())

if __name__ == '__main__':
    work_type()