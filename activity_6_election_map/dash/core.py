from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

BASE = Path(__file__).resolve().parent
CSV = BASE / "data" / "resultados_presidente_sjdr_coordenadas_manuais.csv"
BRANCO, NULO = 95, 96


CANDIDATOS = {
    13: ("Lula", "PT", "#dc2323"),
    14: ("Renan Santos", "MISSÃO", "#d6a326"),
    16: ("Hertz Dias", "PSTU", "#8c564b"),
    21: ("Edmilson Costa", "PCB", "#e65aa5"),
    22: ("Flávio Bolsonaro", "PL", "#2355dc"),
    27: ("Clariana Barão", "DC", "#1e9b41"),
    29: ("Rui Costa Pimenta", "PCO", "#7a5195"),
    30: ("Romeu Zema", "NOVO", "#ff7f0e"),
    35: ("Wilson Grassi", "DEMOCRATA", "#4d908e"),
    55: ("Ronaldo Caiado", "PSD", "#17becf"),
    70: ("Augusto Cury", "AVANTE", "#9467bd"),
    80: ("Samara Martins", "UP", "#e76f51"),
}

COR_PADRAO = "#808995"
COLUNAS = ["NR_TURNO", "NR_VOTAVEL", "QT_VOTOS", "LATITUDE", "LONGITUDE"]


def rotulo(codigo: int) -> str:
    codigo = int(codigo)
    if codigo == BRANCO:
        return "Brancos"
    if codigo == NULO:
        return "Nulos"
    info = CANDIDATOS.get(codigo)
    if info is None:
        return f"Candidato {codigo}"
    return f"{info[0]} ({codigo})" if info[0] != f"Candidato {codigo}" else info[0]


def cor(codigo: int) -> str:
    return CANDIDATOS.get(int(codigo), ("", "", COR_PADRAO))[2]


def inteiro(valor: int | float) -> str:
    return f"{int(valor):,}".replace(",", ".")


def percentual(valor: float, casas: int = 1) -> str:
    return f"{valor:.{casas}f}".replace(".", ",") + "%"


def local_id(latitude: float, longitude: float) -> str:
    return f"{float(latitude):.7f}|{float(longitude):.7f}"


def nome_comum(valores: pd.Series) -> str:
    nomes = [str(nome).strip().split() for nome in valores.dropna().unique() if str(nome).strip()]
    if not nomes:
        return "Local de votação"
    prefixo = []
    for grupo in zip(*nomes):
        if len(set(grupo)) != 1:
            break
        prefixo.append(grupo[0])
    return " ".join(prefixo) or " / ".join(" ".join(p) for p in nomes)


def juntar_secoes(valores: pd.Series) -> str:
    series = valores.dropna().astype(str).str.split(",").explode().str.strip()
    numeros = pd.to_numeric(series, errors="coerce").dropna().astype(int)
    return ", ".join(map(str, sorted(numeros.unique())))


def carregar_base(caminho: Path = CSV) -> tuple[pd.DataFrame, pd.DataFrame, list[int]]:
    raw = pd.read_csv(caminho)
    obrigatorias = COLUNAS + ["NM_LOCAL_VOTACAO", "NR_SECOES", "DS_LOCAL_VOTACAO_ENDERECO"]
    ausentes = set(obrigatorias) - set(raw.columns)
    if ausentes:
        raise ValueError(f"Colunas ausentes no CSV: {', '.join(sorted(ausentes))}")
    for coluna in COLUNAS:
        raw[coluna] = pd.to_numeric(raw[coluna], errors="coerce")
    raw = raw.dropna(subset=["NR_TURNO", "NR_VOTAVEL", "QT_VOTOS"]).copy()
    raw["NR_TURNO"] = raw["NR_TURNO"].astype(int)
    raw["NR_VOTAVEL"] = raw["NR_VOTAVEL"].astype(int)
    raw["QT_VOTOS"] = raw["QT_VOTOS"].astype(int)
    raw["LOCAL_ID"] = None
    coordenadas = raw.LATITUDE.notna() & raw.LONGITUDE.notna()
    raw.loc[coordenadas, "LOCAL_ID"] = [
        local_id(lat, lon)
        for lat, lon in zip(raw.loc[coordenadas, "LATITUDE"], raw.loc[coordenadas, "LONGITUDE"])
    ]
    candidatos = sorted(int(c) for c in raw.NR_VOTAVEL.unique() if c not in (BRANCO, NULO))
    geo = raw.loc[coordenadas].copy()
    locais = geo.groupby("LOCAL_ID", sort=False).agg(
        LATITUDE=("LATITUDE", "first"),
        LONGITUDE=("LONGITUDE", "first"),
        LOCAL=("NM_LOCAL_VOTACAO", nome_comum),
        ENDERECO=("DS_LOCAL_VOTACAO_ENDERECO", "first"),
        SECOES=("NR_SECOES", juntar_secoes),
    )
    votos = geo.groupby(["NR_TURNO", "LOCAL_ID", "NR_VOTAVEL"], as_index=False)["QT_VOTOS"].sum()
    pivot = votos.pivot_table(
        index=["NR_TURNO", "LOCAL_ID"], columns="NR_VOTAVEL", values="QT_VOTOS", aggfunc="sum", fill_value=0
    ).astype(int)
    for codigo in candidatos + [BRANCO, NULO]:
        if codigo not in pivot.columns:
            pivot[codigo] = 0
    validos = pivot[candidatos]
    total = validos.sum(axis=1)
    ranking = validos.apply(lambda x: sorted(x.to_list(), reverse=True)[:2], axis=1)
    resumo = pivot.join(locais, on="LOCAL_ID")
    resumo["VALIDOS"] = total
    resumo["BRANCOS"] = pivot[BRANCO]
    resumo["NULOS"] = pivot[NULO]
    resumo["BRANCO_NULO"] = pivot[BRANCO] + pivot[NULO]
    resumo["TOTAL_GERAL"] = resumo["VALIDOS"] + resumo["BRANCO_NULO"]
    resumo["VENCEDOR"] = validos.idxmax(axis=1).astype(int)
    resumo["VOTOS_VENCEDOR"] = validos.max(axis=1).astype(int)
    resumo["PCT_VENCEDOR"] = (100 * resumo["VOTOS_VENCEDOR"] / resumo["VALIDOS"].replace(0, float("nan"))).fillna(0)
    resumo["MARGEM_PP"] = [
        100 * (v[0] - v[1]) / total_local if total_local > 0 and len(v) >= 2 else 0.0
        for v, total_local in zip(ranking, resumo["VALIDOS"])
    ]
    resumo["EMPATE_LIDER"] = [len(v) >= 2 and v[0] == v[1] for v in ranking]
    resumo = resumo.reset_index()
    resumo = resumo.loc[resumo.VALIDOS > 0].copy()
    for turno in sorted(resumo.NR_TURNO.unique()):
        arquivo_geo = BASE / "data" / f"voronoi_turno_{int(turno)}.geojson"
        if arquivo_geo.exists():
            geojson = json.loads(arquivo_geo.read_text(encoding="utf-8"))
            originais = {f["properties"]["LOCAL_ID"]: int(f["properties"]["CANDIDATO"]) for f in geojson["features"]}
            mascara = (resumo.NR_TURNO == turno) & resumo.LOCAL_ID.isin(originais)
            resumo.loc[mascara, "VENCEDOR"] = resumo.loc[mascara, "LOCAL_ID"].map(originais).astype(int)
    resumo["VOTOS_VENCEDOR"] = [int(row[c]) for _, row in resumo.iterrows() for c in [int(row.VENCEDOR)]]
    return raw, resumo, candidatos


def filtrar_locais(
    dados: pd.DataFrame,
    turno: int,
    vencedores: list[int] | None = None,
    busca: str = "",
    min_votos: int = 0,
    min_forca: float = 0.0,
    candidato: int | None = None,
    min_pct_candidato: float = 0.0,
) -> pd.DataFrame:
    recorte = dados.loc[dados.NR_TURNO == turno].copy()
    if vencedores is not None:
        recorte = recorte.loc[recorte.VENCEDOR.isin(vencedores)]
    if busca.strip():
        termo = busca.strip()
        mask = (
            recorte.LOCAL.str.contains(termo, case=False, regex=False, na=False)
            | recorte.ENDERECO.str.contains(termo, case=False, regex=False, na=False)
            | recorte.SECOES.str.contains(termo, case=False, regex=False, na=False)
        )
        recorte = recorte.loc[mask]
    recorte = recorte.loc[(recorte.VALIDOS >= min_votos) & (recorte.PCT_VENCEDOR >= min_forca)]
    if candidato is not None and min_pct_candidato > 0 and candidato in recorte.columns:
        porcentagem = 100 * recorte[candidato] / recorte.VALIDOS
        recorte = recorte.loc[porcentagem >= min_pct_candidato]
    return recorte


def totais_municipais(raw: pd.DataFrame, turno: int) -> dict:
    dados = raw.loc[raw.NR_TURNO == turno]
    candidatos = dados.loc[~dados.NR_VOTAVEL.isin([BRANCO, NULO])]
    validos = int(candidatos.QT_VOTOS.sum())
    brancos = int(dados.loc[dados.NR_VOTAVEL == BRANCO, "QT_VOTOS"].sum())
    nulos = int(dados.loc[dados.NR_VOTAVEL == NULO, "QT_VOTOS"].sum())
    faltantes = dados.loc[dados.LOCAL_ID.isna()]
    return {
        "validos": validos,
        "brancos": brancos,
        "nulos": nulos,
        "sem_coordenadas": int(faltantes.QT_VOTOS.sum()),
        "locais_georreferenciados": int(dados.LOCAL_ID.nunique()),
        "por_candidato": candidatos.groupby("NR_VOTAVEL").QT_VOTOS.sum().sort_values(ascending=False),
    }
