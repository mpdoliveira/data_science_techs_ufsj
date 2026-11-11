import pandas as pd
import folium as fl
import geopandas as gpd


def nome_comum(valores):
    nomes = [str(nome).strip().split() for nome in valores.dropna().unique()]

    if not nomes:
        return "Local de votação"

    palavras = []

    for grupo in zip(*nomes):
        if len(set(grupo)) != 1:
            break
        palavras.append(grupo[0])

    return " ".join(palavras) or " / ".join(" ".join(nome) for nome in nomes)


def juntar_secoes(valores):
    secoes = valores.dropna().astype(str).str.split(",").explode().str.strip()

    secoes = pd.to_numeric(secoes, errors="coerce").dropna().astype(int)

    return ", ".join(map(str, sorted(secoes.unique())))


municipios = gpd.read_file("MG_Municipios_2025.zip")

sjdr = municipios.loc[municipios["CD_MUN"].astype(str) == "3162500"].to_crs(epsg=4326)

if sjdr.empty:
    raise ValueError("Município de São João del-Rei não encontrado.")

df = pd.read_csv("resultados_presidente_sjdr_coordenadas_manuais.csv")

df = df.dropna(subset=["LATITUDE", "LONGITUDE"])

df = df.groupby(
    ["LONGITUDE", "LATITUDE", "NR_VOTAVEL", "NR_TURNO"], as_index=False
).agg(
    QT_VOTOS=("QT_VOTOS", "sum"),
    NM_LOCAL_VOTACAO=("NM_LOCAL_VOTACAO", nome_comum),
    NR_SECOES=("NR_SECOES", juntar_secoes),
)

df = df.sort_values("QT_VOTOS", ascending=False)

df = df.groupby(["LONGITUDE", "LATITUDE", "NR_TURNO"], sort=False).head(5)

markers = df.loc[
    df.groupby(["LONGITUDE", "LATITUDE", "NR_TURNO"])["QT_VOTOS"].idxmax()
].reset_index(drop=True)

m = fl.Map(
    location=[-21.1365, -44.2619],
    zoom_start=13,
    tiles="https://tile.openstreetmap.de/{z}/{x}/{y}.png",
    attr="&copy; OpenStreetMap contributors",
)

limites = fl.FeatureGroup(name="Limite Municipal", show=True)

fl.GeoJson(
    sjdr,
    name="São João del-Rei",
    style_function=lambda feature: {
        "fillColor": "blue",
        "color": "black",
        "weight": 2,
        "fillOpacity": 0.05,
    },
    tooltip=fl.GeoJsonTooltip(fields=["NM_MUN"], aliases=["Município:"]),
).add_to(limites)

limites.add_to(m)

cores = {13: "red", 22: "blue", 27: "green", 21: "pink"}

layers = {
    1: fl.FeatureGroup(name="1º Turno", show=True),
    2: fl.FeatureGroup(name="2º Turno", show=False),
}

for _, row in markers.iterrows():

    turno = int(row["NR_TURNO"])
    candidato = int(row["NR_VOTAVEL"])

    cor = cores.get(candidato, "gray")

    # Recupera os cinco mais votados do local e turno
    top5 = df.loc[
        (df["LATITUDE"] == row["LATITUDE"])
        & (df["LONGITUDE"] == row["LONGITUDE"])
        & (df["NR_TURNO"] == turno)
    ]

    votos = "<br>".join(
        f"{int(c['NR_VOTAVEL'])}: {int(c['QT_VOTOS'])}" for _, c in top5.iterrows()
    )

    popup = (
        f"<b>{row['NM_LOCAL_VOTACAO']}</b><br>"
        f"Turno: {turno}<br>"
        f"Seções: {row['NR_SECOES']}<br><br>"
        f"<b>Top 5 candidatos:</b><br>"
        f"{votos}"
    )

    fl.Marker(
        location=[row["LATITUDE"], row["LONGITUDE"]],
        tooltip=row["NM_LOCAL_VOTACAO"],
        popup=fl.Popup(popup, max_width=300),
        icon=fl.Icon(color=cor),
    ).add_to(layers[turno])

for layer in layers.values():
    layer.add_to(m)

fl.LayerControl(collapsed=False).add_to(m)

minx, miny, maxx, maxy = sjdr.total_bounds

m.fit_bounds([[miny, minx], [maxy, maxx]])

m.save("test.html")
