
import json
import pandas as pd
import folium as fl
import geopandas as gpd

from branca.element import Element, Figure
from typing import cast
from shapely.geometry import MultiPoint
from shapely.ops import voronoi_diagram


def nome_comum(valores):
    nomes = [
        str(nome).strip().split()
        for nome in valores.dropna().unique()
    ]

    if not nomes:
        return "Local de votação"

    palavras = []

    for grupo in zip(*nomes):
        if len(set(grupo)) != 1:
            break
        palavras.append(grupo[0])

    return " ".join(palavras) or " / ".join(
        " ".join(nome) for nome in nomes
    )


def juntar_secoes(valores):
    secoes = (
        valores.dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
    )

    secoes = pd.to_numeric(
        secoes, errors="coerce"
    ).dropna().astype(int)

    return ", ".join(map(str, sorted(secoes.unique())))


cores = {
    13: "red",
    22: "blue",
    27: "green",
    21: "pink",
}

cores_rgb = {
    13: (220, 35, 35),
    22: (35, 85, 220),
    27: (30, 155, 65),
    21: (230, 90, 165),
}


def cor_por_votos(candidato, proporcao):
    """
    Combina a cor do candidato com branco.

    Uma proporção maior gera uma cor mais intensa.
    Uma proporção menor gera uma cor mais clara.
    """
    rgb = cores_rgb.get(
        int(candidato), (120, 120, 120)
    )

    proporcao = max(0, min(1, float(proporcao)))

    intensidade = 0.25 + 0.75 * proporcao

    resultado = [
        round(255 * (1 - intensidade) + canal * intensidade)
        for canal in rgb
    ]

    return "#{:02x}{:02x}{:02x}".format(*resultado)


municipios = gpd.read_file("MG_Municipios_2025.zip")

sjdr = municipios.loc[
    municipios["CD_MUN"].astype(str) == "3162500"
].to_crs(epsg=4326)

if sjdr.empty:
    raise ValueError(
        "Município de São João del-Rei não encontrado."
    )

municipio_utm = (
    sjdr.to_crs(epsg=31983)
    .geometry.unary_union
)

df = pd.read_csv(
    "resultados_presidente_sjdr_coordenadas_manuais.csv"
)

colunas_numericas = [
    "LATITUDE",
    "LONGITUDE",
    "NR_VOTAVEL",
    "NR_TURNO",
    "QT_VOTOS",
]

for coluna in colunas_numericas:
    df[coluna] = pd.to_numeric(
        df[coluna], errors="coerce"
    )

df = df.dropna(subset=colunas_numericas).copy()

df = df.loc[
    ~df["NR_VOTAVEL"].isin([95, 96])
].copy()

df = df.groupby(
    ["LONGITUDE", "LATITUDE", "NR_VOTAVEL", "NR_TURNO"],
    as_index=False,
).agg(
    QT_VOTOS=("QT_VOTOS", "sum"),
    NM_LOCAL_VOTACAO=("NM_LOCAL_VOTACAO", nome_comum),
    NR_SECOES=("NR_SECOES", juntar_secoes),
)

chaves = ["LONGITUDE", "LATITUDE", "NR_TURNO"]

totais = (
    df.groupby(chaves, as_index=False)
    .agg(TOTAL_VOTOS=("QT_VOTOS", "sum"))
)

top5 = (
    df.sort_values("QT_VOTOS", ascending=False)
    .groupby(chaves, sort=False)
    .head(5)
    .copy()
)

vencedores = (
    top5.groupby(chaves, sort=False)
    .head(1)
    .merge(totais, on=chaves, how="left")
    .reset_index(drop=True)
)

vencedores = vencedores.loc[
    vencedores["TOTAL_VOTOS"] > 0
].copy()

vencedores["FORCA"] = (
    vencedores["QT_VOTOS"]
    / vencedores["TOTAL_VOTOS"]
)


def gerar_poligonos(dados_turno):

    pontos = gpd.GeoDataFrame(
        dados_turno.copy(),
        geometry=gpd.points_from_xy(
            dados_turno["LONGITUDE"],
            dados_turno["LATITUDE"],
        ),
        crs="EPSG:4326",
    ).to_crs(epsg=31983).reset_index(drop=True)

    if pontos.empty:
        raise ValueError("Nenhum local para gerar polígonos.")

    if len(pontos) == 1:
        pares = [(municipio_utm, pontos.iloc[0])]

    else:
        from shapely.geometry import Point

        coordenadas = [
            (float(p.x), float(p.y))
            for p in pontos.geometry
            if isinstance(p, Point)
        ]

        diagrama = voronoi_diagram(
            MultiPoint(coordenadas),
            envelope=municipio_utm.envelope,
        )

        pares = []

        for celula in diagrama.geoms:

            recorte = celula.intersection(municipio_utm)

            if recorte.is_empty or recorte.area == 0:
                continue

            referencia = celula.representative_point()

            distancias = pontos.geometry.distance(
                referencia
            ).to_numpy()

            indice = int(distancias.argmin())

            pares.append((recorte, pontos.iloc[indice]))

    max_votos = float(pontos["TOTAL_VOTOS"].max())

    registros = []

    for geometria, local in pares:

        candidato = int(local["NR_VOTAVEL"])
        forca = float(local["FORCA"])

        registros.append({
            "geometry": geometria,
            "LOCAL": str(local["NM_LOCAL_VOTACAO"]),
            "CANDIDATO": candidato,
            "VOTOS": int(local["QT_VOTOS"]),
            "TOTAL": int(local["TOTAL_VOTOS"]),
            "PERCENTUAL": f"{forca * 100:.1f}%",
            "COR": cor_por_votos(candidato, forca),
            "OPACIDADE": 0.25 + 0.75 * (
                int(local["TOTAL_VOTOS"]) / max_votos
            ),
        })

    regioes = gpd.GeoDataFrame(
        registros,
        geometry="geometry",
        crs="EPSG:31983",
    )

    return regioes.to_crs(epsg=4326)


m = fl.Map(
    location=[-21.1365, -44.2619],
    zoom_start=13,
    tiles=None,
)

fl.TileLayer(
    tiles="https://tile.openstreetmap.de/{z}/{x}/{y}.png",
    attr="&copy; OpenStreetMap contributors",
    name="OpenStreetMap",
    overlay=True,
    control=False,
).add_to(m)

turnos = sorted(
    vencedores["NR_TURNO"].astype(int).unique()
)

if not turnos:
    raise ValueError("Nenhum resultado eleitoral válido.")

layers = {
    turno: fl.FeatureGroup(
        name=f"{turno}º Turno",
        overlay=False,
        show=(turno == turnos[0]),
    )
    for turno in turnos
}

for turno, layer in layers.items():

    dados_turno = vencedores.loc[
        vencedores["NR_TURNO"] == turno
    ]

    regioes = gerar_poligonos(dados_turno)

    fl.GeoJson(
        regioes,
        name=f"Regiões - {turno}º Turno",

        style_function=lambda feature: {
            "fillColor": feature["properties"]["COR"],
            "color": "#FFFFFF",
            "weight": 0.6,
            "fillOpacity": feature["properties"]["OPACIDADE"],
        },

        highlight_function=lambda feature: {
            "color": "#222222",
            "weight": 2,
            "fillOpacity": 1,
        },

        tooltip=fl.GeoJsonTooltip(
            fields=[
                "LOCAL",
                "CANDIDATO",
                "VOTOS",
                "TOTAL",
                "PERCENTUAL",
            ],
            aliases=[
                "Local:",
                "Candidato vencedor:",
                "Votos do vencedor:",
                "Total de votos válidos:",
                "Percentual:",
            ],
            sticky=False,
        ),
    ).add_to(layer)


for _, row in vencedores.iterrows():

    turno = int(row["NR_TURNO"])
    candidato = int(row["NR_VOTAVEL"])

    cor = cores.get(candidato, "gray")

    cinco = top5.loc[
        (top5["LATITUDE"] == row["LATITUDE"])
        & (top5["LONGITUDE"] == row["LONGITUDE"])
        & (top5["NR_TURNO"] == turno)
    ]

    votos = "<br>".join(
        f"{int(c['NR_VOTAVEL'])}: {int(c['QT_VOTOS'])}"
        for _, c in cinco.iterrows()
    )

    popup = (
        f"<b>{row['NM_LOCAL_VOTACAO']}</b><br>"
        f"Turno: {turno}<br>"
        f"Seções: {row['NR_SECOES']}<br>"
        f"Vencedor: {candidato}<br>"
        f"Votos: {int(row['QT_VOTOS'])}<br>"
        f"Total válido: {int(row['TOTAL_VOTOS'])}<br>"
        f"Percentual: {row['FORCA'] * 100:.1f}%<br><br>"
        f"<b>Top 5 candidatos:</b><br>"
        f"{votos}"
    )

    fl.Marker(
        location=[
            row["LATITUDE"],
            row["LONGITUDE"],
        ],
        tooltip=row["NM_LOCAL_VOTACAO"],
        popup=fl.Popup(popup, max_width=300),
        icon=fl.Icon(color=cor),
    ).add_to(layers[turno])


for layer in layers.values():
    layer.add_to(m)


fl.GeoJson(
    sjdr,
    name="Limite Municipal",
    control=False,
    interactive=False,

    style_function=lambda feature: {
        "fillOpacity": 0,
        "color": "#111111",
        "weight": 2.5,
    },
).add_to(m)

fl.LayerControl(collapsed=False).add_to(m)


indicadores_turnos = {}

for turno in turnos:
    dados_turno = vencedores.loc[
        vencedores["NR_TURNO"] == turno
    ]

    indicadores_turnos[str(turno)] = {
        "votos_validos": int(
            dados_turno["TOTAL_VOTOS"].sum()
        ),
        "locais": int(len(dados_turno)),
    }


itens_legenda = "".join(
    f'<div class="legenda-linha">'
    f'<span class="legenda-cor" style="background: rgb{cores_rgb[candidato]};"></span>'
    f'<span>Candidato {candidato}</span>'
    f'</div>'
    for candidato in cores_rgb
)


painel_html = f"""
<style>
    .painel-eleicao, .legenda-eleicao {{
        position: fixed;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.96);
        border: 1px solid #d7dce2;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.16);
        font-family: Arial, sans-serif;
        color: #20252b;
    }}

    .painel-eleicao {{
        top: 85px;
        left: 12px;
        padding: 15px 18px;
        max-width: 280px;
    }}

    .painel-eleicao h3 {{
        font-size: 16px;
        margin: 0 0 8px;
    }}

    .painel-eleicao .subtitulo {{
        font-size: 13px;
        margin-bottom: 10px;
        color: #5b6470;
    }}

    .painel-eleicao .indicador {{
        font-size: 13px;
        margin: 5px 0;
    }}

    .legenda-eleicao {{
        right: 12px;
        bottom: 24px;
        padding: 12px 15px;
        font-size: 13px;
    }}

    .legenda-eleicao strong {{
        display: block;
        margin-bottom: 9px;
    }}

    .legenda-linha {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 6px 0;
    }}

    .legenda-cor {{
        width: 15px;
        height: 15px;
        border: 1px solid rgba(0, 0, 0, 0.15);
        border-radius: 3px;
        display: inline-block;
    }}

    .legenda-nota {{
        max-width: 185px;
        margin-top: 10px;
        font-size: 11px;
        line-height: 1.4;
        color: #5b6470;
    }}
</style>

<div class="painel-eleicao">
    <h3>Eleições presidenciais</h3>
    <div class="subtitulo">
        São João del-Rei · <span id="painel-turno"></span>
    </div>
    <div class="indicador">
        <b>Votos válidos:</b>
        <span id="painel-votos"></span>
    </div>
    <div class="indicador">
        <b>Locais de votação:</b>
        <span id="painel-locais"></span>
    </div>
</div>

<div class="legenda-eleicao">
    <strong>Legenda de cores</strong>
    {itens_legenda}
    <div class="legenda-nota">
        <b>Intensidade da cor:</b><br>
        Tons mais intensos indicam maior percentual
        de votos do candidato vencedor.

        <br><br>

        <b>Transparência:</b><br>
        Representa a quantidade de votos válidos
        em cada local de votação.

        <div style="
            height: 12px;
            margin: 8px 0 5px;
            border-radius: 4px;
            background: linear-gradient(
                to right,
                rgba(100, 100, 100, 0.25),
                rgba(100, 100, 100, 0.75)
            );
        "></div>

        <div style="
            display: flex;
            justify-content: space-between;
            gap: 8px;
            font-size: 10px;
        ">
            <span>Menos votos (25%)</span>
            <span>Mais votos (75%)</span>
        </div>
    </div>
</div>
"""


figura = cast(Figure, m.get_root())
figura.html.add_child(Element(painel_html))


script_painel = """
<script>
document.addEventListener("DOMContentLoaded", function() {

    var indicadoresTurnos = __INDICADORES__;

    function atualizarPainelTurno(turno) {

        var indicadores = indicadoresTurnos[String(turno)];

        if (!indicadores) return;

        document.getElementById("painel-turno").textContent =
            turno + "º turno";

        document.getElementById("painel-votos").textContent =
            indicadores.votos_validos.toLocaleString("pt-BR");

        document.getElementById("painel-locais").textContent =
            indicadores.locais.toLocaleString("pt-BR");
    }

    __MAPA__.on("baselayerchange", function(evento) {

        var turno = parseInt(evento.name, 10);

        if (!isNaN(turno)) {
            atualizarPainelTurno(turno);
        }
    });

    atualizarPainelTurno(__PRIMEIRO_TURNO__);

});
</script>
"""


script_painel = (
    script_painel
    .replace(
        "__INDICADORES__",
        json.dumps(indicadores_turnos)
    )
    .replace("__MAPA__", m.get_name())
    .replace("__PRIMEIRO_TURNO__", str(turnos[0]))
)

figura.html.add_child(Element(script_painel))


minx, miny, maxx, maxy = sjdr.total_bounds

m.fit_bounds([
    [miny, minx],
    [maxy, maxx],
])

m.save("sjdr_election_map.html")

print("Mapa eleitoral gerado com sucesso!")
