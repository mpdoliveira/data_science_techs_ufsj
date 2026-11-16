from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import cast

from branca.element import Element, Figure

import folium as fl
import pandas as pd
from folium.plugins import Fullscreen

from core import cor, inteiro, percentual, rotulo

DATA = Path(__file__).resolve().parent / "data"


def carregar_geometria(turno: int) -> dict:
    return json.loads((DATA / f"voronoi_turno_{turno}.geojson").read_text(encoding="utf-8"))


def carregar_limite() -> dict:
    return json.loads((DATA / "limite_municipal.geojson").read_text(encoding="utf-8"))


def hex_rgb(hexa: str) -> tuple[int, int, int]:
    codigo = hexa.lstrip("#")
    return tuple(int(codigo[i:i + 2], 16) for i in (0, 2, 4))


def misturar_cor(hexa: str, fracao: float, minimo: float = 0.16) -> str:
    intensidade = minimo + (1 - minimo) * max(0.0, min(1.0, float(fracao)))
    resultado = [round(255 * (1 - intensidade) + canal * intensidade) for canal in hex_rgb(hexa)]
    return "#{:02x}{:02x}{:02x}".format(*resultado)


def formatar_popup(row: pd.Series, candidatos: list[int]) -> str:
    top = sorted(candidatos, key=lambda c: int(row[c]), reverse=True)[:5]
    linhas = "".join(
        "<tr><td style='padding:3px 18px 3px 0'>"
        + escape(rotulo(c))
        + "</td><td style='text-align:right'>"
        + inteiro(row[c])
        + "</td><td style='text-align:right;padding-left:12px'>"
        + percentual(100 * row[c] / row.VALIDOS)
        + "</td></tr>"
        for c in top
    )
    return (
        "<div style='font-family:Arial,sans-serif;width:300px;line-height:1.5;font-size:12px'>"
        f"<b style='font-size:14px'>{escape(str(row.LOCAL))}</b>"
        f"<div style='color:#5b6470'>{escape(str(row.ENDERECO))}</div>"
        f"<div>Seções: {escape(str(row.SECOES))}</div>"
        "<hr style='border:0;border-top:1px solid #ddd'>"
        f"<div>Vencedor: <b>{escape(rotulo(row.VENCEDOR))}</b> ({percentual(row.PCT_VENCEDOR)})</div>"
        f"<div>Votos válidos: <b>{inteiro(row.VALIDOS)}</b></div>"
        f"<div>Brancos / nulos: {inteiro(row.BRANCOS)} / {inteiro(row.NULOS)}</div>"
        "<table style='margin-top:8px;width:100%;border-collapse:collapse'>"
        "<tr><th style='text-align:left'>Mais votados</th><th>Votos</th><th>%</th></tr>"
        + linhas + "</table></div>"
    )


def criar_mapa(
    recorte: pd.DataFrame,
    dados_turno: pd.DataFrame,
    turno: int,
    candidatos: list[int],
    modo: str,
    a: int,
    b: int,
    mostrar_pontos: bool = True,
    foco: str = "Município",
) -> tuple[fl.Map, int]:
    mapa = fl.Map(
        location=[-21.1365, -44.2619],
        zoom_start=12,
        tiles=None,
        prefer_canvas=True,
        control_scale=True,
    )
    fl.TileLayer(
        tiles="https://tile.openstreetmap.de/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors",
        name="OpenStreetMap",
        overlay=False,
        control=False,
    ).add_to(mapa)
    ids = set(recorte.LOCAL_ID.astype(str))
    registros = recorte.set_index("LOCAL_ID", drop=False)
    geo = carregar_geometria(turno)
    vmax = max(1, int(dados_turno.VALIDOS.max()))
    max_diferenca = max(
        1.0,
        float((100 * (dados_turno[a] - dados_turno[b]) / dados_turno.VALIDOS).abs().max()),
    )
    atualizadas = []
    for feature in geo["features"]:
        prop = feature["properties"]
        ident = prop["LOCAL_ID"]
        if ident not in ids:
            continue
        row = registros.loc[ident]
        votos = int(row.VALIDOS)
        alfa = 0.45 + 0.30 * (votos / vmax)
        if modo == "Líder por local":
            preenchimento = str(prop["COR_ORIGINAL"])
        elif modo == "% do candidato":
            preenchimento = misturar_cor(cor(a), float(row[a]) / votos)
        elif modo == "Diferença A − B":
            diferenca = 100 * (int(row[a]) - int(row[b])) / votos
            preenchimento = misturar_cor(cor(a if diferenca >= 0 else b), abs(diferenca) / max_diferenca)
        else:
            preenchimento = misturar_cor("#126c83", votos / vmax)
        item = dict(feature)
        item["properties"] = {
            "LOCAL": str(row.LOCAL),
            "VENCEDOR": rotulo(row.VENCEDOR),
            "VALIDOS": inteiro(votos),
            "VENCEDOR_PCT": percentual(row.PCT_VENCEDOR),
            "CANDIDATO_A": f"{inteiro(row[a])} ({percentual(100 * row[a] / votos)})",
            "CANDIDATO_B": f"{inteiro(row[b])} ({percentual(100 * row[b] / votos)})",
            "MARGEM": percentual(100 * (row[a] - row[b]) / votos),
            "COR": preenchimento,
            "OPACIDADE": round(alfa, 4),
        }
        atualizadas.append(item)

    poligonos = fl.FeatureGroup(name="Regiões originais de Voronoi", show=True)
    if atualizadas:
        campos = ["LOCAL", "VENCEDOR", "VALIDOS", "VENCEDOR_PCT"]
        apelidos = ["Local:", "Líder:", "Votos válidos:", "% do líder:"]
        if modo in ("% do candidato", "Diferença A − B"):
            campos.append("CANDIDATO_A")
            apelidos.append(f"{rotulo(a)}:")
        if modo == "Diferença A − B":
            campos.extend(["CANDIDATO_B", "MARGEM"])
            apelidos.extend([f"{rotulo(b)}:", "Diferença A − B:"])
        fl.GeoJson(
            {"type": "FeatureCollection", "features": atualizadas},
            name="Voronoi",
            style_function=lambda feat: {
                "fillColor": feat["properties"]["COR"],
                "fillOpacity": feat["properties"]["OPACIDADE"],
                "color": "#ffffff",
                "weight": 0.65,
            },
            highlight_function=lambda feat: {
                "fillOpacity": 0.90,
                "color": "#172f47",
                "weight": 2.0,
            },
            tooltip=fl.GeoJsonTooltip(fields=campos, aliases=apelidos, sticky=False, labels=True),
        ).add_to(poligonos)
    poligonos.add_to(mapa)

    if mostrar_pontos:
        pontos = fl.FeatureGroup(name="Locais de votação", show=True)
        for _, row in recorte.iterrows():
            if modo == "% do candidato":
                cor_ponto = cor(a)
            elif modo == "Diferença A − B":
                cor_ponto = cor(a if row[a] >= row[b] else b)
            elif modo == "Volume de votos":
                cor_ponto = "#126c83"
            else:
                cor_ponto = cor(row.VENCEDOR)
            fl.CircleMarker(
                [float(row.LATITUDE), float(row.LONGITUDE)],
                radius=4,
                color="#ffffff",
                weight=1.5,
                fill=True,
                fill_color=cor_ponto,
                fill_opacity=0.95,
                tooltip=fl.Tooltip(str(row.LOCAL), sticky=False),
                popup=fl.Popup(formatar_popup(row, candidatos), max_width=360),
            ).add_to(pontos)
        pontos.add_to(mapa)

    limite = carregar_limite()
    fl.GeoJson(
        limite,
        name="Limite municipal",
        control=False,
        interactive=False,
        style_function=lambda feat: {"fillOpacity": 0, "color": "#263345", "weight": 2.4},
    ).add_to(mapa)
    Fullscreen(position="topright").add_to(mapa)
    fl.LayerControl(collapsed=True).add_to(mapa)
    if modo == "Líder por local":
        lideres = sorted(recorte.VENCEDOR.unique())
        itens = "".join(
            f'<div class="atlas-leg-item"><span class="atlas-leg-swatch" style="background:{cor(int(c))}"></span>'
            f'{escape(rotulo(int(c)))}</div>' for c in lideres
        )
        descricao = "Cor: candidato vencedor e intensidade de sua participação"
    elif modo == "% do candidato":
        itens = (
            f'<div class="atlas-grad" style="background:linear-gradient(90deg,#f3f6fa,{cor(a)})"></div>'
            f'<div class="atlas-grad-edges"><span>0%</span><span>100%</span></div>'
        )
        descricao = f"Percentual de votos de {escape(rotulo(a))}"
    elif modo == "Diferença A − B":
        itens = (
            f'<div class="atlas-grad" style="background:linear-gradient(90deg,{cor(b)},#f3f6fa,{cor(a)})"></div>'
            '<div class="atlas-grad-edges"><span>Favorece B</span><span>Favorece A</span></div>'
        )
        descricao = f"Diferença de participação: {escape(rotulo(a))} − {escape(rotulo(b))}"
    else:
        itens = (
            '<div class="atlas-grad" style="background:linear-gradient(90deg,#e9f1f4,#126c83)"></div>'
            '<div class="atlas-grad-edges"><span>Menos votos</span><span>Mais votos</span></div>'
        )
        descricao = "Cor: volume de votos válidos por local"
    legenda = f"""
    <style>
    .atlas-map-legend{{position:fixed;z-index:1000;bottom:28px;right:15px;width:230px;
    background:rgba(255,255,255,.97);padding:13px 15px;border:1px solid #d6e0e7;
    border-radius:10px;box-shadow:0 3px 16px rgba(20,42,62,.2);font:12px Arial,sans-serif;color:#20364a}}
    .atlas-map-legend b{{font-size:13px;display:block;margin-bottom:8px}}
    .atlas-map-legend .atlas-leg-item{{display:flex;align-items:center;gap:8px;margin:6px 0}}
    .atlas-leg-swatch{{display:inline-block;width:14px;height:14px;border:1px solid #aab5bd;border-radius:3px}}
    .atlas-grad{{height:12px;border-radius:4px;border:1px solid #e0e4e8;margin:8px 0 3px}}
    .atlas-grad-edges{{display:flex;justify-content:space-between;font-size:10px;color:#53687d}}
    .atlas-map-legend small{{display:block;font-size:10px;margin-top:10px;line-height:1.35;color:#526579}}
    </style>
    <div class="atlas-map-legend">
    <b>Legenda · {turno}º turno</b>
    {itens}
    <small>{descricao}</small>
    <small><strong>Opacidade:</strong> 45% (menos votos válidos) a 75% (mais votos válidos).</small>
    </div>
    """
    cast(Figure, mapa.get_root()).html.add_child(Element(legenda))

    if foco == "Locais filtrados" and not recorte.empty:
        if len(recorte) == 1:
            row = recorte.iloc[0]
            mapa.location = [float(row.LATITUDE), float(row.LONGITUDE)]
            mapa.options["zoom"] = 13
        else:
            mapa.fit_bounds([
                [float(recorte.LATITUDE.min()), float(recorte.LONGITUDE.min())],
                [float(recorte.LATITUDE.max()), float(recorte.LONGITUDE.max())],
            ], padding=(30, 30))
    else:
        bbox = limite["bbox"]
        mapa.fit_bounds([[bbox[1], bbox[0]], [bbox[3], bbox[2]]])
    return mapa, len(atualizadas)
