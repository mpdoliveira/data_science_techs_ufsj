import pandas
import json
from datetime import date

PATH = "PESSOA_2018.TXT"

def df_cols(path=PATH):
    data = pandas.read_csv(
        path,
        delimiter=";",
        nrows=1,
    )

    return data.columns

def sex_race_age(path=PATH, year=date.today().year) :
    data = pandas.read_csv(
        path,
        delimiter=";",
        nrows=10000,
        usecols=[
            "CO_SEXO_PESSOA",
            "CO_RACA_COR_PESSOA",
            "DT_NASC_PESSOA"
        ]
    )

    df = pandas.DataFrame(data)

    df["age"] = year - df["DT_NASC_PESSOA"].dt.year

    sex_race_groups = df.groupby(["CO_SEXO_PESSOA", "CO_RACA_COR_PESSOA"])

    agregation = sex_race_groups["age"].agg(
        ["mean", "median", "std"]
    )
    print(agregation)


def work_type(path=PATH):
    data = pandas.read_csv(
        path,
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

def work_age_group(path=PATH, year=date.today().year):
    data = pandas.read_csv(
        path,
        delimiter=";",
        nrows=1000000,
        usecols=[
            "DT_NASC_PESSOA",
            "VL_REMUNER_EMPREGO_MEMB"
        ]
    )

    df = pandas.DataFrame(data)
    df.dropna(inplace=True)

    with open("label.json", encoding="utf-8") as file:
        config = json.load(file)
        df["DT_NASC_PESSOA"] = pandas.to_datetime(df["DT_NASC_PESSOA"])

    df["age_groups"] = pandas.cut(
        year - df["DT_NASC_PESSOA"].dt.year,
        bins=config["age_groups"]["delimiters"],
        labels=config["age_groups"]["labels"],
        include_lowest=True
    )

    df["works"] = df["VL_REMUNER_EMPREGO_MEMB"] > 0

    print(df.groupby(["age_groups","works"])["age_groups"].value_counts())

    

if __name__ == '__main__':
    #sex_race_age(year=2018)
    #work_type()
    work_age_group(year=2018)