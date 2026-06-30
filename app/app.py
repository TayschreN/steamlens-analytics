"""
SteamLens - Dashboard interativo (Tema Escuro)
O que faz um jogo ter sucesso na Steam?
"""

import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------
# Configuração da página
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="SteamLens",
    page_icon="🎮",
    layout="wide",
)

# ----------------------------------------------------------------------
# Design tokens — visual SaaS dark (cards flutuantes)
# ----------------------------------------------------------------------
PAGE_BG = "#0B0F17"
CARD_BG = "#151B26"
CARD_BORDER = "rgba(255, 255, 255, 0.06)"
TEXT = "#FFFFFF"
TEXT_MUTED = "#FFFFFF"
BLUE = "#60A5FA"
TEAL = "#2DD4BF"
GREEN = "#34D399"
AMBER = "#FBBF24"
SHADOW = "0 4px 24px rgba(0, 0, 0, 0.45)"

CHART_SEQUENCE = [BLUE, TEAL, "#93C5FD", "#5EEAD4", "#A5B4FC", "#FCD34D"]
KPI_ACCENTS = [BLUE, TEAL, GREEN, AMBER]

# ----------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {{
    background-color: {PAGE_BG} !important;
}}

.block-container {{
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}}

/* Texto geral / labels nativos do streamlit */
p, span, label, .stMarkdown, h1, h2, h3, h4, h5, h6, div {{
    color: {TEXT};
}}

/* Cabeçalho hero */
.slens-hero {{
    margin-bottom: 2rem;
}}
.slens-eyebrow {{
    font-size: 0.8rem;
    font-weight: 600;
    color: {TEXT_MUTED};
    margin-bottom: 0.3rem;
}}
.slens-title {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 2.3rem;
    color: {TEXT};
    margin: 0;
    line-height: 1.15;
}}
.slens-subtitle {{
    color: {TEXT_MUTED};
    font-size: 0.98rem;
    margin-top: 0.5rem;
    max-width: 640px;
}}

/* Rótulo de subseção */
.slens-eyebrow-label {{
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    margin-top: 2.4rem;
    margin-bottom: 0.8rem;
}}

/* KPI cards */
.slens-kpi {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 20px;
    box-shadow: {SHADOW};
    padding: 1.25rem 1.4rem;
}}
.slens-kpi-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 0.4rem;
}}
.slens-kpi-label {{
    font-size: 0.8rem;
    font-weight: 500;
    color: {TEXT_MUTED};
    display: flex;
    align-items: center;
}}
.slens-kpi-value {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.9rem;
    color: {TEXT};
    margin-top: 0.3rem;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: {CARD_BG};
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.35);
    border-right: 1px solid {CARD_BORDER};
}}
section[data-testid="stSidebar"] h2 {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: {TEXT};
}}
section[data-testid="stSidebar"] * {{
    color: {TEXT};
}}

/* Inputs (sliders, multiselect, radio) no dark */
div[data-baseweb="select"] > div {{
    background-color: {PAGE_BG} !important;
    border-color: {CARD_BORDER} !important;
    color: {TEXT} !important;
}}
div[data-baseweb="tag"] {{
    background-color: {BLUE} !important;
}}

/* Gráficos Plotly como cards flutuantes */
div[data-testid="stPlotlyChart"] {{
    background: {CARD_BG} !important;
    border: 1px solid {CARD_BORDER};
    border-radius: 20px;
    box-shadow: {SHADOW};
    padding: 1.3rem 1.3rem 0.6rem 1.3rem;
}}
div[data-testid="stPlotlyChart"] > div {{
    background: {CARD_BG} !important;
}}
.js-plotly-plot, .plot-container {{
    background: {CARD_BG} !important;
}}

/* Dataframe como card */
div[data-testid="stDataFrame"] {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 16px;
    box-shadow: {SHADOW};
    overflow: hidden;
}}

/* Métricas nativas (fallback) */
div[data-testid="stMetric"] {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 20px;
    box-shadow: {SHADOW};
    padding: 1rem 1.2rem;
}}
div[data-testid="stMetricLabel"] {{
    color: {TEXT_MUTED} !important;
}}
div[data-testid="stMetricValue"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {TEXT} !important;
}}

hr {{
    border-color: {CARD_BORDER};
}}
</style>
""", unsafe_allow_html=True)


def chart_theme(fig, title=None):
    """Aplica o tema visual escuro padrão a um gráfico Plotly."""
    fig.update_layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(family="Inter, sans-serif", color=TEXT, size=12),
        title=dict(
            text=title,
            font=dict(family="Plus Jakarta Sans, sans-serif", size=15, color=TEXT),
        ) if title else None,
        margin=dict(t=46 if title else 16, l=8, r=8, b=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.15)", color=TEXT, tickfont=dict(color=TEXT_MUTED))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.15)", color=TEXT, tickfont=dict(color=TEXT_MUTED))
    return fig


def subsection_label(text):
    st.markdown(f'<div class="slens-eyebrow-label">{text}</div>', unsafe_allow_html=True)


def kpi_card(label, value, accent):
    st.markdown(f"""
    <div class="slens-kpi">
        <div class="slens-kpi-label"><span class="slens-kpi-dot" style="background:{accent};"></span>{label}</div>
        <div class="slens-kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Carregamento de dados
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_parquet("data/games_clean.parquet")
    for col in ["developers", "publishers", "categories", "genres", "tags"]:
        df[col] = df[col].apply(json.loads)
    df["has_dlc"] = df["dlc_count"] > 0
    df["num_platforms"] = df[["windows", "mac", "linux"]].sum(axis=1)
    return df


df = load_data()

# ----------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------
st.markdown(f"""
<div class="slens-hero">
    <div class="slens-eyebrow">Steam Games Dataset · 2025</div>
    <p class="slens-title">SteamLens</p>
    <p class="slens-subtitle">O que faz um jogo ter sucesso na Steam? Análise de {df.shape[0]:,} jogos publicados na plataforma.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Sidebar - Filtros
# ----------------------------------------------------------------------
st.sidebar.markdown("## Filtros")

genres_list = sorted(df["genre_primary"].dropna().unique())
genre_filter = st.sidebar.multiselect("Gênero principal", genres_list, default=[])

price_max = float(df["price"].max())
price_filter = st.sidebar.slider("Faixa de preço (USD)", 0.0, price_max, (0.0, price_max))

year_min, year_max = int(df["release_year"].min()), int(df["release_year"].max())
year_filter = st.sidebar.slider("Ano de lançamento", year_min, year_max, (2010, year_max))

indie_filter = st.sidebar.radio("Tipo de desenvolvedor", ["Todos", "Apenas Indie", "Apenas Não-Indie"])

df_filtered = df[
    (df["price"] >= price_filter[0]) & (df["price"] <= price_filter[1]) &
    (df["release_year"] >= year_filter[0]) & (df["release_year"] <= year_filter[1])
].copy()

if genre_filter:
    df_filtered = df_filtered[df_filtered["genre_primary"].isin(genre_filter)]

if indie_filter == "Apenas Indie":
    df_filtered = df_filtered[df_filtered["is_indie"]]
elif indie_filter == "Apenas Não-Indie":
    df_filtered = df_filtered[~df_filtered["is_indie"]]

st.sidebar.markdown(f"""
<div style="font-size:0.82rem; color:{TEXT_MUTED}; margin-top:0.8rem;">
    {df_filtered.shape[0]:,} jogos no filtro atual
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Total de jogos", f"{df_filtered.shape[0]:,}", KPI_ACCENTS[0])
with c2:
    kpi_card("Avaliação média", f"{df_filtered['pct_pos_total'].mean():.1f}%", KPI_ACCENTS[1])
with c3:
    kpi_card("Preço médio", f"${df_filtered['price'].mean():.2f}", KPI_ACCENTS[2])
with c4:
    kpi_card("Gratuitos", f"{df_filtered['is_free'].mean() * 100:.1f}%", KPI_ACCENTS[3])

# ----------------------------------------------------------------------
# Monetização e tipo de dev
# ----------------------------------------------------------------------
subsection_label("Monetização")
c1, c2 = st.columns(2)

with c1:
    fig = px.box(
        df_filtered, x="is_free", y="pct_pos_total",
        labels={"is_free": "", "pct_pos_total": "% Avaliação Positiva"},
        color_discrete_sequence=[BLUE],
    )
    fig.update_xaxes(ticktext=["Pago", "Gratuito"], tickvals=[False, True])
    st.plotly_chart(chart_theme(fig, "Pago vs Gratuito"), use_container_width=True)

with c2:
    fig = px.box(
        df_filtered, x="is_indie", y="pct_pos_total",
        labels={"is_indie": "", "pct_pos_total": "% Avaliação Positiva"},
        color_discrete_sequence=[TEAL],
    )
    fig.update_xaxes(ticktext=["Não-Indie", "Indie"], tickvals=[False, True])
    st.plotly_chart(chart_theme(fig, "Indie vs Não-Indie"), use_container_width=True)

# ----------------------------------------------------------------------
# Gêneros
# ----------------------------------------------------------------------
subsection_label("Gêneros — Quantidade vs qualidade")

genre_stats = (
    df_filtered.groupby("genre_primary")
    .agg(qtd_jogos=("appid", "count"), media_avaliacao=("pct_pos_total", "mean"))
    .query("qtd_jogos >= 10")
    .sort_values("qtd_jogos", ascending=False)
)

c1, c2 = st.columns(2)
with c1:
    top_qtd = genre_stats.head(15)
    fig = px.bar(
        top_qtd, x="qtd_jogos", y=top_qtd.index, orientation="h",
        labels={"qtd_jogos": "Quantidade", "genre_primary": ""},
        color_discrete_sequence=[BLUE],
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(chart_theme(fig, "Quantidade de jogos por gênero"), use_container_width=True)

with c2:
    top_quality = genre_stats.sort_values("media_avaliacao", ascending=False).head(15)
    fig = px.bar(
        top_quality, x="media_avaliacao", y=top_quality.index, orientation="h",
        labels={"media_avaliacao": "% Avaliação Positiva", "genre_primary": ""},
        color_discrete_sequence=[TEAL],
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(chart_theme(fig, "Avaliação média por gênero"), use_container_width=True)

# ----------------------------------------------------------------------
# Lançamentos por ano
# ----------------------------------------------------------------------
subsection_label("Linha do tempo — Lançamentos vs avaliação média")

yearly = (
    df_filtered.groupby("release_year")
    .agg(qtd_lancamentos=("appid", "count"), media_avaliacao=("pct_pos_total", "mean"))
    .reset_index()
)

fig = go.Figure()
fig.add_bar(x=yearly["release_year"], y=yearly["qtd_lancamentos"], name="Lançamentos", marker_color="#26314A", marker_line_width=0)
fig.add_scatter(
    x=yearly["release_year"], y=yearly["media_avaliacao"], mode="lines+markers",
    name="Avaliação média (%)", yaxis="y2", line=dict(color=TEAL, width=2.5), marker=dict(size=6),
    fill="tozeroy", fillcolor="rgba(45, 212, 191, 0.10)"
)
fig.update_layout(
    yaxis2=dict(overlaying="y", side="right", title="% Avaliação Positiva", gridcolor="rgba(255,255,255,0.07)"),
    yaxis=dict(title="Lançamentos"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(chart_theme(fig), use_container_width=True)

# ----------------------------------------------------------------------
# Preço ideal
# ----------------------------------------------------------------------
subsection_label("Pricing — Existe um preço ideal?")

df_paid_view = df_filtered[df_filtered["price"] > 0].copy()
df_paid_view["price_bucket"] = pd.cut(
    df_paid_view["price"],
    bins=[0, 5, 10, 15, 20, 30, 40, 60, 100, 1000],
    labels=["0-5", "5-10", "10-15", "15-20", "20-30", "30-40", "40-60", "60-100", "100+"]
)
price_quality = df_paid_view.groupby("price_bucket", observed=True)["pct_pos_total"].mean().reset_index()

fig = px.bar(
    price_quality, x="price_bucket", y="pct_pos_total",
    labels={"price_bucket": "Faixa de preço (USD)", "pct_pos_total": "% Avaliação Positiva Média"},
    color_discrete_sequence=[BLUE],
)
st.plotly_chart(chart_theme(fig), use_container_width=True)

# ----------------------------------------------------------------------
# DLC e plataformas
# ----------------------------------------------------------------------
subsection_label("Suporte ao jogo — DLC e multiplataforma")
c1, c2 = st.columns(2)

with c1:
    dlc_stats = df_filtered.groupby("has_dlc").agg(
        media_playtime_horas=("average_playtime_forever", lambda x: x.mean() / 60),
    ).reset_index()
    dlc_stats["has_dlc"] = dlc_stats["has_dlc"].map({True: "Com DLC", False: "Sem DLC"})

    fig = px.bar(
        dlc_stats, x="has_dlc", y="media_playtime_horas",
        labels={"has_dlc": "", "media_playtime_horas": "Playtime médio (horas)"},
        color_discrete_sequence=[BLUE],
    )
    st.plotly_chart(chart_theme(fig, "Tempo médio jogado: Com vs Sem DLC"), use_container_width=True)

with c2:
    platform_stats = df_filtered.groupby("num_platforms").agg(
        media_owners=("estimated_owners_avg", "mean"),
    ).reset_index()

    fig = px.bar(
        platform_stats, x="num_platforms", y="media_owners",
        labels={"num_platforms": "Nº de plataformas suportadas", "media_owners": "Estimativa média de owners"},
        color_discrete_sequence=[TEAL],
    )
    st.plotly_chart(chart_theme(fig, "Alcance estimado por nº de plataformas"), use_container_width=True)

# ----------------------------------------------------------------------
# Tabela explorável
# ----------------------------------------------------------------------
subsection_label("Explorar — Tabela de jogos filtrados")

cols_show = [
    "name", "release_year", "price", "genre_primary", "pct_pos_total",
    "num_reviews_total", "metacritic_score", "is_indie", "is_free"
]
st.dataframe(
    df_filtered[cols_show].sort_values("num_reviews_total", ascending=False),
    use_container_width=True,
    hide_index=True,
)
