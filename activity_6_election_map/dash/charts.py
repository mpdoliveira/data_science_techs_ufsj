from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core import cor, inteiro, rotulo

FONTE = "Arial, sans-serif"


def acabamento(fig: go.Figure, altura: int = 510) -> go.Figure:
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=18, t=60, b=15),
        font=dict(family=FONTE, size=12, color="#223347"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e9edf3", zerolinecolor="#8a96a3")
    fig.update_yaxes(showgrid=False)
    return fig


def ranking(recorte: pd.DataFrame, candidatos: list[int], turno: int) -> go.Figure:
    totais = pd.Series({c: int(recorte[c].sum()) for c in candidatos}).sort_values(ascending=False)
    validos = max(1, int(totais.sum()))
    tabela = pd.DataFrame({
        "Candidato": [rotulo(c) for c in totais.index],
        "Votos": totais.values,
        "Percentual": 100 * totais.values / validos,
        "Cor": [cor(c) for c in totais.index],
    })
    tabela = tabela.sort_values("Votos", ascending=True)
    fig = go.Figure(go.Bar(
        x=tabela["Percentual"], y=tabela["Candidato"], orientation="h",
        marker_color=tabela["Cor"],
        text=[f"{p:.1f}%" for p in tabela["Percentual"]],
        textposition="outside", cliponaxis=False,
        customdata=tabela[["Votos"]].to_numpy(),
        hovertemplate="%{y}<br>Votos: %{customdata[0]:,.0f}<br>Participação: %{x:.2f}%<extra></extra>",
    ))
    fig.update_layout(title=f"Participação por candidato · {turno}º turno", showlegend=False,
                      xaxis_title="% dos votos válidos no recorte", yaxis_title="", xaxis_range=[0, max(5, float(tabela.Percentual.max()) * 1.17)])
    return acabamento(fig, max(410, len(tabela) * 37 + 110))


def distribuicao(recorte: pd.DataFrame, a: int, turno: int, top_n: int) -> go.Figure:
    tabela = recorte.copy()
    tabela["PARTICIPACAO"] = 100 * tabela[a] / tabela.VALIDOS
    tabela = tabela.sort_values("PARTICIPACAO", ascending=False).head(top_n).sort_values("PARTICIPACAO")
    fig = go.Figure(go.Bar(
        x=tabela.PARTICIPACAO, y=tabela.LOCAL, orientation="h", marker_color=cor(a),
        customdata=tabela[[a, "VALIDOS"]].to_numpy(),
        hovertemplate="%{y}<br>Votos no candidato: %{customdata[0]:,.0f}<br>Votos válidos: %{customdata[1]:,.0f}<br>Participação: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(title=f"Locais com maior percentual para {rotulo(a)} · {turno}º turno",
                      xaxis_title="% dos votos válidos do local", yaxis_title="", xaxis_range=[0, 105], showlegend=False)
    return acabamento(fig, max(450, len(tabela) * 29 + 100))


def margem(recorte: pd.DataFrame, a: int, b: int, turno: int, top_n: int) -> go.Figure:
    tabela = recorte.copy()
    tabela["DIFERENCA"] = 100 * (tabela[a] - tabela[b]) / tabela.VALIDOS
    tabela = tabela.reindex(tabela.DIFERENCA.abs().sort_values(ascending=False).index).head(top_n)
    tabela = tabela.sort_values("DIFERENCA")
    vencedora = [cor(a) if x >= 0 else cor(b) for x in tabela.DIFERENCA]
    fig = go.Figure(go.Bar(
        x=tabela.DIFERENCA, y=tabela.LOCAL, orientation="h", marker_color=vencedora,
        text=[f"{v:+.1f}" for v in tabela.DIFERENCA], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br>Diferença: %{x:+.1f} p.p.<extra></extra>",
    ))
    maior = max(10, float(tabela.DIFERENCA.abs().max()) * 1.25)
    fig.update_layout(title=f"Margem {rotulo(a)} − {rotulo(b)} · {turno}º turno",
                      xaxis_title="Diferença de participação (pontos percentuais)",
                      yaxis_title="", xaxis_range=[-maior, maior], showlegend=False)
    return acabamento(fig, max(450, len(tabela) * 29 + 100))


def evolucao(locais: pd.DataFrame, ids: set[str], a: int, b: int) -> go.Figure:
    dados = locais.loc[locais.LOCAL_ID.isin(ids)]
    linhas = []
    for turno in sorted(dados.NR_TURNO.unique()):
        trecho = dados.loc[dados.NR_TURNO == turno]
        validos = max(1, int(trecho.VALIDOS.sum()))
        for candidato in (a, b):
            linhas.append({
                "Turno": f"{int(turno)}º turno", "Candidato": rotulo(candidato),
                "Votos": int(trecho[candidato].sum()),
                "Percentual": 100 * int(trecho[candidato].sum()) / validos,
                "Cor": cor(candidato),
            })
    tabela = pd.DataFrame(linhas)
    fig = px.bar(
        tabela, x="Turno", y="Percentual", color="Candidato", barmode="group", text="Percentual",
        color_discrete_map={rotulo(a): cor(a), rotulo(b): cor(b)},
        custom_data=["Votos"], title="Evolução do apoio entre turnos · mesmos locais selecionados",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False,
                      hovertemplate="%{x}<br>%{fullData.name}: %{y:.1f}%<br>Votos: %{customdata[0]:,.0f}<extra></extra>")
    fig.update_layout(yaxis_title="% dos votos válidos", xaxis_title="", bargap=0.3,
                      yaxis_range=[0, max(5.0, float(tabela.Percentual.max()) * 1.24)])
    return acabamento(fig, 520)
