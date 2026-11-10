import pandas as pd

# Raw data can be found at:
# https://dadosabertos.tse.jus.br/dataset/resultados-2026/resource/01ea4ccd-f443-469c-9f29-c69ff97f7d4c

df = pd.read_csv("votacao_secao_2026_BR.csv", sep=";", encoding="latin1")
df = df.drop(
    columns=[
        "DT_GERACAO",
        "HH_GERACAO",
        "ANO_ELEICAO",
        "CD_TIPO_ELEICAO",
        "NM_TIPO_ELEICAO",
        "NR_TURNO",
        "CD_ELEICAO",
        "DS_ELEICAO",
        "DT_ELEICAO",
        "TP_ABRANGENCIA",
        "SG_UF",
        "SG_UE",
        "NM_UE",
        "CD_MUNICIPIO",
        "NR_ZONA",
        "CD_CARGO",
        "DS_CARGO"
    ]
)

df = df[df["NM_MUNICIPIO"] == "SÃO JOÃO DEL REI"]

df = df.drop(columns=["NM_MUNICIPIO"])

df.to_csv("resultados_presidente_sjdr_1_turno.csv", index=False, encoding="UTF-8")
