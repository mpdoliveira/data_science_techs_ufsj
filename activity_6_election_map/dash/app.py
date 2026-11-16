from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from charts import distribuicao, evolucao, margem, ranking
from core import CSV, carregar_base, cor, filtrar_locais, inteiro, percentual, rotulo, totais_municipais
from maps import carregar_geometria, criar_mapa
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent.parent
MAPA_ORIGINAL = ROOT / "sjdr_election_map.html"

st.set_page_config(
    page_title="Atlas eleitoral | São João del-Rei",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container {max-width: 1550px; padding-top: 1.45rem; padding-bottom: 2.8rem;}
    [data-testid="stMetric"] {background: #f6f9fc; border: 1px solid #e0e9f0; border-radius: 13px; padding: 16px 18px;}
    [data-testid="stMetricValue"] {font-size: clamp(1.2rem, 2vw, 2rem); color: #18364e;}
    [data-testid="stMetricLabel"] {color: #526579; font-weight: 600;}
    div[data-testid="stTabs"] button {font-weight: 600;}
    .atlas-hero {background: linear-gradient(115deg, #102a43 0%, #1b5671 100%); padding: 24px 28px;
                 border-radius: 15px; margin-bottom: 16px; color: #fff;}
    .atlas-kicker {font-size: 11px; letter-spacing: 2.2px; text-transform: uppercase; opacity: .78; font-weight: 800;}
    .atlas-hero h1 {color: #fff; font-size: clamp(1.45rem, 3vw, 2.2rem); margin: 7px 0 6px; line-height: 1.2;}
    .atlas-hero p {margin: 0; font-size: 13px; color: #dcecf5;}
    .atlas-muted {font-size: 12px; color: #5d7288; margin-bottom: 12px;}
    [data-testid="stSidebar"] {background-color: #f8fafc;}
    [data-testid="stSidebar"] h2 {font-size: 1.08rem;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Carregando resultados eleitorais...")
def obter_dados():
    return carregar_base(CSV)


@st.cache_data(show_spinner=False)
def obter_geometria(turno: int):
    return carregar_geometria(turno)


try:
    raw, locais, candidatos = obter_dados()
except (OSError, ValueError, KeyError) as erro:
    st.error(f"Não foi possível carregar a base eleitoral: {erro}")
    st.stop()

turnos = sorted(int(t) for t in raw.NR_TURNO.unique())

with st.sidebar:
    st.markdown("### 🗳️ Explorar eleições")
    st.caption("São João del-Rei · Dados por local de votação")
    turno = st.radio("Turno", turnos, horizontal=True, format_func=lambda t: f"{t}º turno")
    dados_turno = locais.loc[locais.NR_TURNO == turno].copy()
    municipio = totais_municipais(raw, turno)
    ordenados = sorted(candidatos, key=lambda c: -int(dados_turno[c].sum()))
    vencedores_opcoes = sorted(dados_turno.VENCEDOR.unique().astype(int), key=lambda c: -int((dados_turno.VENCEDOR == c).sum()))
    st.divider()
    st.markdown("**Filtros dos locais**")
    vencedores = st.multiselect(
        "Candidato vencedor", vencedores_opcoes, default=vencedores_opcoes,
        format_func=rotulo, key=f"vencedores_{turno}",
        help="Mostra apenas os locais vencidos por um ou mais candidatos selecionados.",
    )
    busca = st.text_input("Buscar local, endereço ou seção", placeholder="Ex.: UFSJ, 135, Centro", key="busca_local")
    votos_minimos = st.number_input(
        "Mínimo de votos válidos por local", min_value=0,
        max_value=int(dados_turno.VALIDOS.max()), value=0, step=100,
        key=f"min_votos_{turno}",
    )
    forca_minima = st.slider("Força mínima do vencedor (%)", 0, 100, 0, 5, key="forca_lider")
    st.divider()
    st.markdown("**Análise por candidato**")
    a = st.selectbox(
        "Candidato A", ordenados, index=ordenados.index(13) if 13 in ordenados else 0,
        format_func=rotulo, key="cand_a",
    )
    candidatos_b = [c for c in ordenados if c != a]
    b = st.selectbox(
        "Candidato B (comparação)", candidatos_b,
        index=candidatos_b.index(22) if 22 in candidatos_b else 0,
        format_func=rotulo, key="cand_b",
    )
    pct_minima = st.slider(
        f"Participação mínima de {rotulo(a)} (%)", 0, 100, 0, 5,
        key=f"min_pct_{a}",
        help="Filtra locais onde o candidato A recebeu menos que o percentual indicado.",
    )
    st.divider()
    st.markdown("**Exibição cartográfica**")
    modo = st.selectbox(
        "Cor dos polígonos",
        ["Líder por local", "% do candidato", "Diferença A − B", "Volume de votos"],
        help="As áreas dos polígonos são as mesmas do mapa original; só a cor muda.",
    )
    mostrar_pontos = st.checkbox("Mostrar pontos dos locais", value=True)
    foco = st.selectbox("Enquadramento", ["Município", "Locais filtrados"], index=0)
    st.caption("Transparência dos polígonos: 45%–75% de opacidade, proporcional aos votos válidos.")
    def limpar_filtros():
        for chave in [f"vencedores_{turno}", "busca_local", f"min_votos_{turno}", "forca_lider", f"min_pct_{a}"]:
            st.session_state.pop(chave, None)

    st.button("Limpar filtros", use_container_width=True, on_click=limpar_filtros)

recorte = filtrar_locais(
    locais, turno, vencedores, busca, int(votos_minimos), float(forca_minima), a, float(pct_minima)
)
selecionados = set(recorte.LOCAL_ID)
votos_recorte = int(recorte.VALIDOS.sum())
locais_recorte = len(recorte)
quantia_bn = int(recorte.BRANCO_NULO.sum())
contagem = {c: int(recorte[c].sum()) for c in candidatos}
mais_votado = max(contagem, key=lambda codigo: contagem[codigo]) if votos_recorte else None

st.markdown(
    '<section class="atlas-hero"><div class="atlas-kicker">Atlas eleitoral interativo</div>'
    '<h1>São João del-Rei · Eleição presidencial</h1>'
    '<p>Geometrias originais de Voronoi · Resultados por local de votação · Filtros sincronizados</p></section>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Votos válidos no recorte", inteiro(votos_recorte))
k2.metric("Locais selecionados", inteiro(locais_recorte), f"de {len(dados_turno)} georreferenciados", delta_color="off")
k3.metric("Líder no recorte", rotulo(mais_votado) if mais_votado is not None else "—")
k4.metric("Cobertura do voto válido municipal", percentual(100 * votos_recorte / municipio["validos"]) if municipio["validos"] else "—")

with st.expander("Conferir totais municipais, dados sem coordenadas e critérios", expanded=False):
    x1, x2, x3, x4 = st.columns(4)
    x1.metric("Votos válidos no município", inteiro(municipio["validos"]))
    x2.metric("Brancos", inteiro(municipio["brancos"]))
    x3.metric("Nulos", inteiro(municipio["nulos"]))
    x4.metric("Votos sem coordenadas", inteiro(municipio["sem_coordenadas"]))
    st.caption(
        "Os indicadores principais são calculados somente para os locais georreferenciados que passam nos filtros. "
        "Os totais municipais utilizam todas as linhas do CSV, incluindo locais sem coordenadas. "
        "A diferença entre ambos é esperada mesmo quando não há filtros ativos."
    )

if recorte.empty:
    st.warning("Nenhum local corresponde aos filtros selecionados. Ajuste os critérios na barra lateral.")
    st.stop()

aba_mapa, aba_ranking, aba_local, aba_margem, aba_turnos, aba_tabela, aba_sobre = st.tabs([
    "🗺️ Mapa", "📊 Ranking", "📈 Por local", "⚖️ Margem", "🔄 Turnos", "🏫 Tabela", "ℹ️ Método",
])

with aba_mapa:
    titulo, detalhe = st.columns([3, 1])
    with titulo:
        st.subheader("Mapa das regiões de Voronoi")
        st.caption(f"{turno}º turno · {modo} · {locais_recorte} locais correspondem aos filtros")
    with detalhe:
        st.download_button(
            "Baixar HTML original", MAPA_ORIGINAL.read_bytes(),
            file_name="sjdr_election_map_original.html", mime="text/html", use_container_width=True,
        )
    try:
        mapa, geometrias = criar_mapa(
            recorte, dados_turno, turno, candidatos, modo, a, b,
            mostrar_pontos=mostrar_pontos, foco=foco,
        )
        components.html(mapa.get_root().render(), height=710, scrolling=False)
        st.caption(
            f"{geometrias} regiões do mapa original visíveis. As cores representam: {modo.lower()}. "
            "Opacidade entre 45% (menos votos válidos) e 75% (mais votos válidos). "
            "Clique nos pontos para consultar o top 5 e os votos por local."
        )
        sem_poligono = locais_recorte - geometrias
        if sem_poligono > 0:
            st.info(
                f"{sem_poligono} local(is) selecionado(s) não possui(em) polígono no HTML original "
                "(coordenadas fora da área municipal). Seus votos continuam incluídos nos indicadores, "
                "gráficos e tabela."
            )
        camada = obter_geometria(turno)
        feicoes = [f for f in camada["features"] if f["properties"]["LOCAL_ID"] in selecionados]
        st.download_button(
            "Exportar GeoJSON filtrado",
            json.dumps({"type": "FeatureCollection", "features": feicoes}, ensure_ascii=False),
            file_name=f"voronoi_filtrado_turno_{turno}.geojson", mime="application/geo+json",
        )
    except (OSError, ValueError, KeyError) as erro:
        st.error(f"Falha ao carregar o mapa original: {erro}")

with aba_ranking:
    st.subheader("Distribuição dos votos válidos por candidato")
    st.caption("Participação calculada somente nos locais selecionados no filtro lateral.")
    st.plotly_chart(ranking(recorte, candidatos, turno), width="stretch")
    st.download_button(
        "Exportar totais por candidato (CSV)",
        pd.DataFrame({"Candidato": [rotulo(c) for c in candidatos], "Votos": [contagem[c] for c in candidatos]})
        .sort_values("Votos", ascending=False).to_csv(index=False).encode("utf-8-sig"),
        file_name=f"ranking_turno_{turno}.csv", mime="text/csv",
    )

with aba_local:
    c1, c2 = st.columns([3, 1])
    c1.subheader(f"Participação de {rotulo(a)} por local")
    qtd_local = c2.select_slider("Mostrar até", options=[10, 15, 20, 30, 50], value=20, key="topn_local")
    st.plotly_chart(distribuicao(recorte, a, turno, qtd_local), width="stretch")
    st.caption("Ordenação pela participação percentual do candidato A, e não pelo número absoluto de votos.")

with aba_margem:
    c1, c2 = st.columns([3, 1])
    c1.subheader(f"Diferença entre {rotulo(a)} e {rotulo(b)}")
    qtd_margem = c2.select_slider("Mostrar até", options=[10, 15, 20, 30, 50], value=20, key="topn_margem")
    st.plotly_chart(margem(recorte, a, b, turno, qtd_margem), width="stretch")
    st.caption("Diferença em pontos percentuais (A − B); valores negativos favorecem o candidato B. "
               "São exibidos os locais com as maiores diferenças absolutas.")

with aba_turnos:
    st.subheader("Comparação dos dois turnos")
    st.caption(
        "Compara os votos dos candidatos A e B somente nos mesmos endereços/localizações "
        "que passaram pelos filtros no turno atual. Não representa todos os locais do município "
        "quando há filtros ativos."
    )
    st.plotly_chart(evolucao(locais, selecionados, a, b), width="stretch")
    subtabela = locais.loc[locais.LOCAL_ID.isin(selecionados)].groupby("NR_TURNO").agg(
        locais=("LOCAL_ID", "nunique"), validos=("VALIDOS", "sum")
    ).reset_index()
    subtabela.columns = ["Turno", "Locais presentes", "Votos válidos"]
    st.dataframe(subtabela, width="stretch", hide_index=True)

with aba_tabela:
    st.subheader("Resultados por local de votação")
    exibir_candidatos = st.toggle("Exibir votos de todos os candidatos", value=False)
    colunas = [
        "LOCAL", "ENDERECO", "SECOES", "VALIDOS", "BRANCOS", "NULOS", "VENCEDOR", "PCT_VENCEDOR",
        "MARGEM_PP", a, b,
    ]
    if exibir_candidatos:
        colunas.extend(candidatos)
    colunas = list(dict.fromkeys(colunas))
    tabela = recorte[colunas].copy().sort_values("VALIDOS", ascending=False)
    nomes: dict[str | int, str] = {
        "LOCAL": "Local", "ENDERECO": "Endereço", "SECOES": "Seções",
        "VALIDOS": "Votos válidos", "BRANCOS": "Brancos", "NULOS": "Nulos",
        "VENCEDOR": "Candidato vencedor", "PCT_VENCEDOR": "% do vencedor", "MARGEM_PP": "Margem top 2 (p.p.)",
    }
    nomes.update({c: f"Votos: {rotulo(c)}" for c in candidatos})
    tabela["VENCEDOR"] = tabela.VENCEDOR.map(rotulo)
    tabela = tabela.rename(columns=nomes)
    st.dataframe(
        tabela, width="stretch", height=570, hide_index=True,
        column_config={
            "% do vencedor": st.column_config.NumberColumn(format="%.1f%%"),
            "Margem top 2 (p.p.)": st.column_config.NumberColumn(format="%.1f"),
        },
    )
    st.download_button(
        "Baixar tabela filtrada (CSV)",
        tabela.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"locais_filtrados_turno_{turno}.csv", mime="text/csv",
    )

with aba_sobre:
    st.subheader("Fontes, método e interpretação")
    st.markdown("""
**Fontes de dados.** Resultados agregados por local e coordenadas disponibilizados com o projeto.
O painel não faz consultas externas para obter os votos. O mapa base e os limites municipais
foram extraídos do arquivo `sjdr_election_map.html` fornecido no projeto.

**Geometrias originais.** Os polígonos são os do mapa original de Voronoi, extraídos uma única vez,
sem realizar novo cálculo de Voronoi no dashboard. Eles indicam proximidade ao local de votação,
**não** equivalem a distritos eleitorais oficiais, bairros ou limites de seções.

**Filtros sincronizados.** Turno, vencedor, busca por local, votos válidos mínimos, força mínima do
vencedor e participação mínima do candidato A afetam mapa, indicadores, ranking, gráficos e tabela.
O gráfico de comparação usa os mesmos locais filtrados em ambos os turnos.

**Cores.** A visualização “Líder por local” conserva a cor já codificada no mapa original.
Os demais modos reinterpretam somente o preenchimento: força do candidato A,
diferença de participação A − B ou volume de votos válidos. A opacidade varia de **45% a 75%**,
proporcional ao volume relativo de votos válidos do local no turno.

**Cobertura.** Os totais municipais incluem registros sem coordenadas. Locais com coordenadas
fora do limite municipal podem ter votos, mas não possuem um polígono no mapa de origem.
O dashboard exibe avisos e mantém esses votos nos indicadores dos locais selecionados.

**Limites analíticos.** Dados agregados por local não permitem concluir como votou cada indivíduo.
Qualquer interpretação espacial requer cautela porque as áreas do Voronoi são aproximações geométricas.
""")
    st.code("python -m streamlit run dash/app.py", language="powershell")
