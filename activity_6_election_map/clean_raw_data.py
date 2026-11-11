import pandas as pd

import unicodedata

# Raw data can be found at:
# https://dadosabertos.tse.jus.br/dataset/resultados-2026/resource/01ea4ccd-f443-469c-9f29-c69ff97f7d4c

def nome_comum(valores):
    nomes = [
        nome.strip().split()
        for nome in valores.dropna().unique()
    ]

    if not nomes:
        return None

    palavras = []

    for grupo in zip(*nomes):
        if len(set(grupo)) != 1:
            break
        palavras.append(grupo[0])

    return " ".join(palavras) or " / ".join(
        " ".join(nome) for nome in nomes
    )



df = pd.read_csv("votacao_secao_2026_BR.csv", sep=";", encoding="latin1")
df = df.drop(
    columns=[
        "DT_GERACAO",
        "HH_GERACAO",
        "ANO_ELEICAO",
        "CD_TIPO_ELEICAO",
        "NM_TIPO_ELEICAO",
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

df["DS_LOCAL_VOTACAO_ENDERECO"] = (
    df["DS_LOCAL_VOTACAO_ENDERECO"]
    .str.replace(r"\b(?:S/N|SN)\b", "", regex=True, case=False)
    .str.replace(r"\s*,\s*,", ",", regex=True)
    .str.strip(" ,")
)

df["DS_LOCAL_VOTACAO_ENDERECO"] = (
    df["DS_LOCAL_VOTACAO_ENDERECO"]
    .apply(
        lambda x: "".join(
            c for c in unicodedata.normalize("NFD", x)
            if unicodedata.category(c) != "Mn"
        ) if isinstance(x, str) else x
    )
)

df = df.groupby(
    ["NR_VOTAVEL", "DS_LOCAL_VOTACAO_ENDERECO", "NR_TURNO"],
    as_index=False
).agg(
    QT_VOTOS=("QT_VOTOS", "sum"),

    NM_LOCAL_VOTACAO=("NM_LOCAL_VOTACAO", nome_comum),

    NR_SECOES=(
        "NR_SECAO",
        lambda x: ", ".join(
            map(str, sorted(x.dropna().astype(int).unique()))
        )
    )
)

df.to_csv("resultados_presidente_sjdr.csv", index=False)
