"""Dashboard eleitoral: Presidente 2026 em São João del-Rei (UFSJ / DCOMP)."""
import json
from pathlib import Path

import branca.colormap as cm
import folium as fl
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

BASE = Path(__file__).parent
CSV = BASE / "data" / "resultados_presidente_sjdr_coordenadas_manuais.csv"
GEOJSON = BASE / "data" / "sjdr_limite.geojson"
BRANCO, NULO = 95, 96

CANDIDATOS = {
    13: {"partido": "PT", "nome": "Lula", "cor": "#d62728"},
    22: {"partido": "PL", "nome": "Flavio Bolsonaro", "cor": "#1f4e9c"},
    70: {"partido": "AVANTE", "nome": "Augusto Cury", "cor": "#9467bd"},
    55: {"partido": "PSD", "nome": "Ronaldo Caiado", "cor": "#17becf"},
    30: {"partido": "NOVO", "nome": "Romeu Zema", "cor": "#ff7f0e"},
    14: {"partido": "MISSAO", "nome": "Renan Santos", "cor": "#ffc222"},
}
COR_PADRAO = "#7f7f7f"


def rotulo(n):
    n = int(n)
    if n == BRANCO:
        return "Branco"
    if n == NULO:
        return "Nulo"
    c = CANDIDATOS.get(n, {})
    if c.get("nome"):
        return f"{c['nome']} ({n})"
    return f"{n} – {c['partido']}" if c.get("partido") else f"Candidato {n}"


def cor(n):
    return CANDIDATOS.get(int(n), {}).get("cor", COR_PADRAO)


def milhar(x):
    return f"{int(x):,}".replace(",", ".")


def nome_comum(valores):
    nomes = [str(n).strip().split() for n in valores.dropna().unique()]
    if not nomes:
        return "Local de votação"
    palavras = []
    for grupo in zip(*nomes):
        if len(set(grupo)) != 1:
            break
        palavras.append(grupo[0])
    return " ".join(palavras) or " / ".join(" ".join(n) for n in nomes)


def juntar_secoes(valores):
    s = valores.dropna().astype(str).str.split(",").explode().str.strip()
    s = pd.to_numeric(s, errors="coerce").dropna().astype(int)
    return ", ".join(map(str, sorted(s.unique())))


@st.cache_data
def carregar():
    raw = pd.read_csv(CSV)
    ok = raw.dropna(subset=["LATITUDE", "LONGITUDE"]).copy()
    ok["LOCAL_ID"] = ok.groupby(["LATITUDE", "LONGITUDE"]).ngroup()
    locais = ok.groupby("LOCAL_ID").agg(
        LATITUDE=("LATITUDE", "first"),
        LONGITUDE=("LONGITUDE", "first"),
        LOCAL=("NM_LOCAL_VOTACAO", nome_comum),
        SECOES=("NR_SECOES", juntar_secoes),
    )
    votos = ok.groupby(["LOCAL_ID", "NR_TURNO", "NR_VOTAVEL"], as_index=False)["QT_VOTOS"].sum()
    return raw, locais, votos


@st.cache_data
def resumo_turno(turno):
    """Resumo por local de votação: votos válidos, brancos/nulos, líder e % por candidato."""
    _, locais, votos = carregar()
    v = votos[votos.NR_TURNO == turno]
    is_bn = v.NR_VOTAVEL.isin([BRANCO, NULO])
    val = v[~is_bn]
    pivot = val.pivot_table(index="LOCAL_ID", columns="NR_VOTAVEL", values="QT_VOTOS", aggfunc="sum", fill_value=0)
    validos = pivot.sum(axis=1).rename("VALIDOS")
    pct = pivot.div(validos, axis=0) * 100
    bn = v[is_bn].groupby("LOCAL_ID")["QT_VOTOS"].sum().rename("BRANCO_NULO")
    res = locais.join(validos, how="inner").join(bn).fillna({"BRANCO_NULO": 0})
    res["LIDER"] = pivot.idxmax(axis=1)
    res["PCT_LIDER"] = pct.max(axis=1)
    return res, pct


def tooltip_html(r, pct_row, extra=""):
    top = pct_row.sort_values(ascending=False).head(3)
    linhas = "".join(
        f"<tr><td style='padding-right:12px'>{rotulo(c)}</td>"
        f"<td style='text-align:right'><b>{p:.1f}%</b></td></tr>"
        for c, p in top.items()
    )
    return (
        "<div style='font-family:sans-serif;font-size:13px;line-height:1.45;min-width:220px'>"
        f"<div style='font-size:14px;font-weight:700'>{r.LOCAL}</div>"
        f"<div style='color:#666'>Seções: {r.SECOES}</div>"
        "<hr style='margin:5px 0'>"
        f"Líder: <b style='color:{cor(r.LIDER)}'>{rotulo(r.LIDER)}</b> ({r.PCT_LIDER:.1f}%)"
        f"{extra}<table style='margin-top:4px'>{linhas}</table>"
        f"<div style='color:#666;margin-top:4px'>Votos válidos: {milhar(r.VALIDOS)}</div></div>"
    )


def construir_mapa(res, pct, modo, a, b):
    m = fl.Map(location=[-21.1365, -44.2619], zoom_start=13, tiles="OpenStreetMap")
    limite = None
    if GEOJSON.exists():
        limite = fl.GeoJson(
            json.loads(GEOJSON.read_text(encoding="utf-8")),
            name="Limite municipal",
            style_function=lambda f: {"fillColor": "#3388ff", "color": "#222", "weight": 2, "fillOpacity": 0.04},
        ).add_to(m)

    cmap = None
    if modo == "pct":
        vmax = float(pct[a].max())
        cmap = cm.LinearColormap(["#f7f7f7", cor(a)], vmin=0, vmax=vmax, caption=f"% de votos válidos – {rotulo(a)}")
    elif modo == "comp":
        lim = float((pct[a] - pct[b]).abs().max()) or 1.0
        cmap = cm.LinearColormap(
            [cor(b), "#f5f5f5", cor(a)], vmin=-lim, vmax=lim,
            caption=f"Diferença (p.p.): ← {rotulo(b)} | {rotulo(a)} →",
        )

    camada = fl.FeatureGroup(name="Locais de votação").add_to(m)
    vmax_votos = res.VALIDOS.max()
    for lid, r in res.iterrows():
        extra = ""
        if modo == "lider":
            fill = cor(r.LIDER)
        elif modo == "pct":
            fill = cmap(pct.loc[lid, a])
            extra = f"<br>{rotulo(a)}: <b>{pct.loc[lid, a]:.1f}%</b>"
        else:
            d = pct.loc[lid, a] - pct.loc[lid, b]
            fill = cmap(d)
            extra = f"<br>Diferença {rotulo(a)} − {rotulo(b)}: <b>{d:+.1f} p.p.</b>"
        fl.CircleMarker(
            location=[r.LATITUDE, r.LONGITUDE],
            radius=6 + 14 * (r.VALIDOS / vmax_votos) ** 0.5,
            color="#333", weight=1, fill=True, fill_color=fill, fill_opacity=0.85,
            tooltip=fl.Tooltip(tooltip_html(r, pct.loc[lid], extra), sticky=True),
        ).add_to(camada)

    if cmap:
        cmap.add_to(m)
    fl.LayerControl(collapsed=False).add_to(m)
    if limite is not None:
        m.fit_bounds(limite.get_bounds())
    else:
        m.fit_bounds([[res.LATITUDE.min(), res.LONGITUDE.min()], [res.LATITUDE.max(), res.LONGITUDE.max()]])
    return m


# interface
st.set_page_config(page_title="Eleição Presidencial – São João del-Rei", page_icon="🗳️", layout="wide")
st.sidebar.caption(f"Rodando: {__file__}")
raw, locais, votos = carregar()

st.title("🗳️ Eleição presidencial em São João del-Rei")
st.caption("Votação por local de votação, 1º e 2º turnos · Dados abertos do TSE · UFSJ – Ferramentas para Data Science")

with st.sidebar:
    st.header("Filtros")
    turno = st.radio("Turno", [1, 2], format_func=lambda t: f"{t}º turno", horizontal=True)
    res, pct = resumo_turno(turno)
    ordem = list(pct.sum().sort_values(ascending=False).index)
    st.subheader("Mapa")
    modo = st.radio(
        "Visualização",
        ["lider", "pct", "comp"],
        format_func={
            "lider": "Candidato líder por local",
            "pct": "% de um candidato (graduado)",
            "comp": "Comparação entre dois candidatos",
        }.get,
    )
    a, b = ordem[0], ordem[1]
    if modo == "pct":
        a = st.selectbox("Candidato", ordem, format_func=rotulo)
    elif modo == "comp":
        a = st.selectbox("Candidato A", ordem, index=0, format_func=rotulo)
        b = st.selectbox("Candidato B", ordem, index=1, format_func=rotulo)

mt = raw[raw.NR_TURNO == turno]
bn_mt = mt[mt.NR_VOTAVEL.isin([BRANCO, NULO])].QT_VOTOS.sum()
val_mt = mt[~mt.NR_VOTAVEL.isin([BRANCO, NULO])].groupby("NR_VOTAVEL").QT_VOTOS.sum().sort_values(ascending=False)
lider_mt, vot_lider = val_mt.index[0], val_mt.iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Votos válidos", milhar(val_mt.sum()))
c2.metric("Brancos e nulos", milhar(bn_mt), f"{bn_mt / (bn_mt + val_mt.sum()) * 100:.1f}% do total", delta_color="off")
c3.metric("Mais votado", rotulo(lider_mt), f"{vot_lider / val_mt.sum() * 100:.1f}% dos válidos", delta_color="off")
c4.metric("Locais de votação", raw.DS_LOCAL_VOTACAO_ENDERECO.nunique())

sem_coord = mt[mt.LATITUDE.isna() | mt.LONGITUDE.isna()].QT_VOTOS.sum()
if sem_coord:
    st.warning(f"{milhar(sem_coord)} votos ({sem_coord / mt.QT_VOTOS.sum() * 100:.1f}%) são de locais sem coordenadas e não aparecem no mapa, mas entram nos totais acima.")

col_mapa, col_graf = st.columns([3, 2], gap="medium")

with col_mapa:
    if modo == "comp" and a == b:
        st.info("Escolha dois candidatos diferentes para comparar.")
    else:
        st_folium(construir_mapa(res, pct, modo, a, b), height=640, use_container_width=True, returned_objects=[], key=f"mapa-{turno}-{modo}-{a}-{b}-{hash(str(CANDIDATOS))}")
        st.caption("O tamanho do círculo é proporcional aos votos válidos do local. Passe o mouse para ver o detalhe.")

with col_graf:
    d = pd.DataFrame({"Candidato": [rotulo(c) for c in val_mt.index], "Votos": val_mt.values, "num": val_mt.index})
    d["% válidos"] = d.Votos / d.Votos.sum() * 100
    fig = px.bar(d, x="% válidos", y="Candidato", orientation="h", text=d["% válidos"].map("{:.1f}%".format),
                 color="Candidato", color_discrete_map={rotulo(n): cor(n) for n in d.num},
                 title=f"Votos válidos por candidato – {turno}º turno")
    fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"}, height=320, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, width="stretch")

    fin = [13, 22]
    t = raw[raw.NR_VOTAVEL.isin(fin)].groupby(["NR_TURNO", "NR_VOTAVEL"], as_index=False).QT_VOTOS.sum()
    t["Candidato"] = t.NR_VOTAVEL.map(rotulo)
    t["Turno"] = t.NR_TURNO.map(lambda x: f"{x}º turno")
    fig2 = px.bar(t, x="Turno", y="QT_VOTOS", color="Candidato", barmode="group", text="QT_VOTOS",
                  color_discrete_map={rotulo(n): cor(n) for n in fin}, title="Finalistas: 1º vs 2º turno")
    fig2.update_layout(yaxis_title="Votos", height=300, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig2, width="stretch")

if len(ordem) >= 2:
    fa, fb = (13, 22) if {13, 22} <= set(pct.columns) else (ordem[0], ordem[1])
    marg = (pct[fa] - pct[fb]).rename("Diferença (p.p.)").to_frame().join(res.LOCAL).sort_values("Diferença (p.p.)")
    marg["Vence"] = marg["Diferença (p.p.)"].map(lambda x: rotulo(fa) if x > 0 else rotulo(fb))
    fig3 = px.bar(marg, x="Diferença (p.p.)", y="LOCAL", orientation="h", color="Vence",
                  color_discrete_map={rotulo(fa): cor(fa), rotulo(fb): cor(fb)},
                  title=f"Margem por local: {rotulo(fa)} vs {rotulo(fb)} ({turno}º turno)", height=max(400, 18 * len(marg)))
    fig3.update_layout(yaxis_title=None)
    st.plotly_chart(fig3, width="stretch")

aba_locais, aba_sobre = st.tabs(["🏫 Locais de votação", "ℹ️ Sobre"])

with aba_locais:
    tab = res.reset_index(drop=True)[["LOCAL", "SECOES", "VALIDOS", "BRANCO_NULO", "LIDER", "PCT_LIDER"]].copy()
    tab["LIDER"] = tab.LIDER.map(rotulo)
    tab.columns = ["Local", "Seções", "Votos válidos", "Brancos/nulos", "Líder", "% do líder"]
    busca = st.text_input("Buscar local")
    if busca:
        tab = tab[tab.Local.str.contains(busca, case=False, na=False)]
    st.dataframe(tab.sort_values("Votos válidos", ascending=False), width="stretch", hide_index=True,
                 column_config={"% do líder": st.column_config.NumberColumn(format="%.1f%%")})
    st.download_button("Baixar CSV", tab.to_csv(index=False).encode("utf-8"), f"locais_{turno}turno.csv", "text/csv")

with aba_sobre:
    st.markdown(
        """
**Fonte:** resultados por seção eleitoral do TSE (dados abertos), filtrados para São João del-Rei e
agregados por local de votação (endereço). Os endereços foram geocodificados com Nominatim/OpenStreetMap
e corrigidos manualmente quando necessário.

**Método**
- Porcentagens e líder usam **votos válidos** (excluem brancos e nulos, códigos 95 e 96 do TSE).
- O mapa usa círculos graduados por local de votação, já que os dados não possuem polígonos por seção.
- Locais sem coordenadas ficam fora do mapa, mas entram nos totais do município.

**Limitações:** a unidade espacial é o local de votação, que pode reunir várias seções;
a leitura espacial é aproximada, pois cada ponto representa o endereço do local.
"""
    )
