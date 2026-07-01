"""
SteamLens - Dashboard interativo
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
# Design tokens — visual SaaS (cards flutuantes, dark)
# ----------------------------------------------------------------------
PAGE_BG = "#0B0F17"
CARD_BG = "#151B26"
TEXT = "#F1F5F9"
TEXT_MUTED = "#94A3B8"
BLUE = "#60A5FA"
TEAL = "#2DD4BF"
GREEN = "#34D399"
AMBER = "#FBBF24"
PURPLE = "#A78BFA"
ROSE = "#FB7185"
GRID = "#26303D"
SHADOW = "0 4px 24px rgba(0, 0, 0, 0.35)"

CHART_SEQUENCE = [BLUE, TEAL, "#93C5FD", "#5EEAD4", "#A5B4FC", "#FCD34D"]
KPI_ACCENTS = [BLUE, TEAL, GREEN, AMBER]
KPI_ACCENTS_2 = [PURPLE, ROSE, AMBER, TEAL]

# ----------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background-color: {PAGE_BG};
}}

.block-container {{
    padding-top: 2.5rem;
    padding-bottom: 3rem;
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
    margin-top: 2.6rem;
    margin-bottom: 0.2rem;
}}
.slens-section-title {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 700;
    font-size: 1.25rem;
    color: {TEXT};
    margin-bottom: 0.9rem;
}}

/* KPI cards */
.slens-kpi {{
    background: {CARD_BG};
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

/* Insight callout */
.slens-insight {{
    background: linear-gradient(135deg, rgba(96,165,250,0.08), rgba(45,212,191,0.05));
    border: 1px solid rgba(148,163,184,0.14);
    border-radius: 14px;
    padding: 0.85rem 1.1rem;
    margin-top: 0.7rem;
    margin-bottom: 0.4rem;
    font-size: 0.88rem;
    color: {TEXT_MUTED};
    line-height: 1.5;
}}
.slens-insight b {{
    color: {TEXT};
}}
.slens-insight .tag {{
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: {BLUE};
    text-transform: uppercase;
    margin-right: 0.5rem;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: {CARD_BG};
    box-shadow: 4px 0 24px rgba(0,0,0,0.2);
}}
section[data-testid="stSidebar"] h2 {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: {TEXT};
}}
section[data-testid="stSidebar"] h3 {{
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: {TEXT_MUTED};
    margin-top: 1.4rem;
}}

/* Gráficos Plotly como cards flutuantes */
div[data-testid="stPlotlyChart"] {{
    background: {CARD_BG};
    border-radius: 20px;
    box-shadow: {SHADOW};
    padding: 1.3rem 1.3rem 0.6rem 1.3rem;
}}

/* Dataframe como card */
div[data-testid="stDataFrame"] {{
    background: {CARD_BG};
    border-radius: 16px;
    box-shadow: {SHADOW};
    overflow: hidden;
}}

/* Métricas nativas (fallback) */
div[data-testid="stMetric"] {{
    background: {CARD_BG};
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

/* Expander */
div[data-testid="stExpander"] {{
    background: {CARD_BG};
    border-radius: 16px;
    box-shadow: {SHADOW};
    border: none;
}}

hr {{
    border-color: rgba(148,163,184,0.1);
}}
</style>
""", unsafe_allow_html=True)


def chart_theme(fig, title=None):
    """Aplica o tema visual padrão a um gráfico Plotly."""
    fig.update_layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(family="Inter, sans-serif", color=TEXT, size=12),
        title=dict(
            text=title,
            font=dict(family="Plus Jakarta Sans, sans-serif", size=15, color=TEXT),
        ) if title else None,
        margin=dict(t=46 if title else 16, l=8, r=8, b=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_MUTED)),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, tickfont=dict(color=TEXT_MUTED))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, tickfont=dict(color=TEXT_MUTED))
    return fig


def subsection_label(label, title):
    st.markdown(f"""
    <div class="slens-eyebrow-label">{label}</div>
    <div class="slens-section-title">{title}</div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, accent):
    st.markdown(f"""
    <div class="slens-kpi">
        <div class="slens-kpi-label"><span class="slens-kpi-dot" style="background:{accent};"></span>{label}</div>
        <div class="slens-kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def insight_card(tag, html_text):
    st.markdown(f"""
    <div class="slens-insight"><span class="tag">{tag}</span>{html_text}</div>
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

st.sidebar.markdown("### Mais filtros")

dlc_filter = st.sidebar.radio("DLC", ["Todos", "Apenas com DLC", "Apenas sem DLC"])

platform_filter = st.sidebar.multiselect(
    "Plataformas suportadas", ["Windows", "Mac", "Linux"], default=[]
)

min_reviews_filter = st.sidebar.slider(
    "Mínimo de avaliações", 10, 5000, 10, step=10,
    help="Filtra jogos com poucas avaliações para reduzir ruído estatístico"
)

only_metacritic = st.sidebar.checkbox("Somente jogos com nota Metacritic", value=False)

# ----------------------------------------------------------------------
# Aplicação dos filtros
# ----------------------------------------------------------------------
df_filtered = df[
    (df["price"] >= price_filter[0]) & (df["price"] <= price_filter[1]) &
    (df["release_year"] >= year_filter[0]) & (df["release_year"] <= year_filter[1]) &
    (df["total_reviews"] >= min_reviews_filter)
].copy()

if genre_filter:
    df_filtered = df_filtered[df_filtered["genre_primary"].isin(genre_filter)]

if indie_filter == "Apenas Indie":
    df_filtered = df_filtered[df_filtered["is_indie"]]
elif indie_filter == "Apenas Não-Indie":
    df_filtered = df_filtered[~df_filtered["is_indie"]]

if dlc_filter == "Apenas com DLC":
    df_filtered = df_filtered[df_filtered["has_dlc"]]
elif dlc_filter == "Apenas sem DLC":
    df_filtered = df_filtered[~df_filtered["has_dlc"]]

if platform_filter:
    plat_map = {"Windows": "windows", "Mac": "mac", "Linux": "linux"}
    for p in platform_filter:
        df_filtered = df_filtered[df_filtered[plat_map[p]]]

if only_metacritic:
    df_filtered = df_filtered[df_filtered["metacritic_score"] > 0]

st.sidebar.markdown(f"""
<div style="font-size:0.82rem; color:{TEXT_MUTED}; margin-top:1rem;">
    <b style="color:{TEXT};">{df_filtered.shape[0]:,}</b> jogos no filtro atual
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("Nenhum jogo encontrado com esses filtros. Tente ampliar os critérios na barra lateral.")
    st.stop()

# ----------------------------------------------------------------------
# KPIs — linha 1
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
# KPIs — linha 2
# ----------------------------------------------------------------------
st.markdown('<div style="height:0.9rem"></div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Playtime médio", f"{df_filtered['average_playtime_forever'].mean() / 60:.1f}h", KPI_ACCENTS_2[0])
with c2:
    kpi_card("Mediana de reviews", f"{int(df_filtered['num_reviews_total'].median()):,}", KPI_ACCENTS_2[1])
with c3:
    top_genre = df_filtered["genre_primary"].value_counts().idxmax() if not df_filtered["genre_primary"].dropna().empty else "—"
    kpi_card("Gênero líder (volume)", top_genre, KPI_ACCENTS_2[2])
with c4:
    kpi_card("Com DLC", f"{df_filtered['has_dlc'].mean() * 100:.1f}%", KPI_ACCENTS_2[3])

# ----------------------------------------------------------------------
# Monetização e tipo de dev
# ----------------------------------------------------------------------
subsection_label("Seção 01", "Monetização")
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

free_mean = df_filtered.loc[df_filtered["is_free"], "pct_pos_total"].mean()
paid_mean = df_filtered.loc[~df_filtered["is_free"], "pct_pos_total"].mean()
indie_mean = df_filtered.loc[df_filtered["is_indie"], "pct_pos_total"].mean()
nonindie_mean = df_filtered.loc[~df_filtered["is_indie"], "pct_pos_total"].mean()

insight_card(
    "Insight",
    f"No recorte atual, jogos gratuitos avaliam em média <b>{free_mean:.1f}%</b> "
    f"contra <b>{paid_mean:.1f}%</b> dos pagos. Jogos indie avaliam <b>{indie_mean:.1f}%</b> "
    f"vs <b>{nonindie_mean:.1f}%</b> dos não-indie — modelo de monetização sozinho explica pouco da qualidade percebida."
)

# ----------------------------------------------------------------------
# Gêneros
# ----------------------------------------------------------------------
subsection_label("Seção 02", "Gêneros — Quantidade vs qualidade")

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

if not genre_stats.empty:
    maior_volume = genre_stats.index[0]
    melhor_avaliado = genre_stats["media_avaliacao"].idxmax()
    insight_card(
        "Insight",
        f"<b>{maior_volume}</b> é o gênero com mais jogos publicados "
        f"({int(genre_stats.loc[maior_volume, 'qtd_jogos']):,}), mas <b>{melhor_avaliado}</b> lidera em "
        f"qualidade percebida ({genre_stats.loc[melhor_avaliado, 'media_avaliacao']:.1f}% de avaliação média) — "
        f"o gênero mais saturado nem sempre é o mais bem avaliado."
    )

# ----------------------------------------------------------------------
# Lançamentos por ano
# ----------------------------------------------------------------------
subsection_label("Seção 03", "Linha do tempo — Lançamentos vs avaliação média")

yearly = (
    df_filtered.groupby("release_year")
    .agg(qtd_lancamentos=("appid", "count"), media_avaliacao=("pct_pos_total", "mean"))
    .reset_index()
)

fig = go.Figure()
fig.add_bar(x=yearly["release_year"], y=yearly["qtd_lancamentos"], name="Lançamentos", marker_color="#26344A", marker_line_width=0)
fig.add_scatter(
    x=yearly["release_year"], y=yearly["media_avaliacao"], mode="lines+markers",
    name="Avaliação média (%)", yaxis="y2", line=dict(color=TEAL, width=2.5), marker=dict(size=6),
    fill="tozeroy", fillcolor="rgba(45, 212, 191, 0.08)"
)
fig.update_layout(
    yaxis2=dict(overlaying="y", side="right", title="% Avaliação Positiva", gridcolor=GRID),
    yaxis=dict(title="Lançamentos"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(chart_theme(fig), use_container_width=True)

if len(yearly) > 2:
    pico_volume = yearly.loc[yearly["qtd_lancamentos"].idxmax()]
    pior_qualidade = yearly.loc[yearly["media_avaliacao"].idxmin()]
    insight_card(
        "Insight",
        f"O pico de lançamentos foi em <b>{int(pico_volume['release_year'])}</b> "
        f"({int(pico_volume['qtd_lancamentos']):,} jogos), enquanto a menor avaliação média "
        f"ocorreu em <b>{int(pior_qualidade['release_year'])}</b> ({pior_qualidade['media_avaliacao']:.1f}%) — "
        f"volume alto de lançamentos tende a coincidir com queda na qualidade média percebida."
    )

# ----------------------------------------------------------------------
# Preço x Avaliações (scatter)
# ----------------------------------------------------------------------
subsection_label("Seção 04", "Preço x Volume de avaliações")

df_paid_scatter = df_filtered[df_filtered["price"] > 0]
fig = px.scatter(
    df_paid_scatter, x="price", y="num_reviews_total",
    labels={"price": "Preço (USD)", "num_reviews_total": "Nº de avaliações"},
    color_discrete_sequence=[BLUE], opacity=0.35, log_y=True,
)
st.plotly_chart(chart_theme(fig, "Preço x Nº de avaliações (jogos pagos, escala log)"), use_container_width=True)

if len(df_paid_scatter) > 5:
    corr_price_reviews = df_paid_scatter["price"].corr(df_paid_scatter["num_reviews_total"])
    insight_card(
        "Insight",
        f"Correlação entre preço e volume de avaliações: <b>{corr_price_reviews:.2f}</b> — "
        f"praticamente nula. O grosso do volume de avaliações se concentra em jogos de até $20, "
        f"mas isso reflete alcance de vendas, não necessariamente qualidade."
    )

# ----------------------------------------------------------------------
# Preço ideal
# ----------------------------------------------------------------------
subsection_label("Seção 05", "Pricing — Existe um preço ideal?")

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
    color_discrete_sequence=[AMBER],
)
st.plotly_chart(chart_theme(fig), use_container_width=True)

if not price_quality.empty:
    faixa_ideal = price_quality.loc[price_quality["pct_pos_total"].idxmax()]
    insight_card(
        "Insight",
        f"A faixa de preço com melhor avaliação média é <b>${faixa_ideal['price_bucket']}</b> "
        f"({faixa_ideal['pct_pos_total']:.1f}%). Jogos muito baratos ou muito caros tendem a avaliar pior — "
        f"os primeiros por qualidade shovelware, os segundos por expectativa alta não cumprida."
    )

# ----------------------------------------------------------------------
# Crítica especializada vs comunidade
# ----------------------------------------------------------------------
subsection_label("Seção 06", "Metacritic vs Comunidade Steam")

df_meta = df_filtered[df_filtered["metacritic_score"] > 0]

if len(df_meta) > 5:
    fig = px.scatter(
        df_meta, x="metacritic_score", y="pct_pos_total",
        labels={"metacritic_score": "Metacritic Score", "pct_pos_total": "% Avaliação Positiva (Steam)"},
        color_discrete_sequence=[PURPLE], opacity=0.4,
    )
    st.plotly_chart(chart_theme(fig, "Metacritic x Avaliação da comunidade Steam"), use_container_width=True)

    corr_meta = df_meta["metacritic_score"].corr(df_meta["pct_pos_total"])
    insight_card(
        "Insight",
        f"Correlação entre nota Metacritic e avaliação da comunidade: <b>{corr_meta:.2f}</b> — "
        f"geralmente concordam, mas a comunidade Steam tende a ser mais generosa que a crítica especializada, "
        f"especialmente em notas baixas/médias do Metacritic. Base: <b>{len(df_meta):,}</b> jogos com nota Metacritic."
    )
else:
    st.info("Poucos jogos com nota Metacritic no filtro atual para essa análise.")

# ----------------------------------------------------------------------
# Tags mais envolventes (playtime)
# ----------------------------------------------------------------------
subsection_label("Seção 07", "Quais tags prendem mais tempo do jogador?")

top_tags_playtime = (
    df_filtered[df_filtered["top_tag"].notna()]
    .groupby("top_tag")
    .agg(qtd_jogos=("appid", "count"), media_playtime=("average_playtime_forever", "mean"))
    .query("qtd_jogos >= 10")
    .sort_values("media_playtime", ascending=False)
    .head(12)
)
top_tags_playtime["media_playtime_horas"] = top_tags_playtime["media_playtime"] / 60

if not top_tags_playtime.empty:
    fig = px.bar(
        top_tags_playtime, x="media_playtime_horas", y=top_tags_playtime.index, orientation="h",
        labels={"media_playtime_horas": "Tempo médio jogado (horas)", "top_tag": ""},
        color_discrete_sequence=[TEAL],
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(chart_theme(fig, "Top tags por tempo médio de jogo"), use_container_width=True)

    lider_tag = top_tags_playtime.index[0]
    insight_card(
        "Insight",
        f"A tag <b>{lider_tag}</b> lidera em tempo médio de jogo "
        f"({top_tags_playtime.loc[lider_tag, 'media_playtime_horas']:.1f}h). Tags de gêneros passivos ou de "
        f"acúmulo (idle, visual novel, simulação) tendem a dominar aqui — essa métrica mede retenção de tela, "
        f"não necessariamente qualidade."
    )

# ----------------------------------------------------------------------
# Top desenvolvedores
# ----------------------------------------------------------------------
subsection_label("Seção 08", "Desenvolvedores mais bem avaliados")

dev_stats = (
    df_filtered[df_filtered["developer_primary"].notna()]
    .groupby("developer_primary")
    .agg(qtd_jogos=("appid", "count"), media_avaliacao=("pct_pos_total", "mean"))
    .query("qtd_jogos >= 3")
    .sort_values("media_avaliacao", ascending=False)
    .head(12)
)

if not dev_stats.empty:
    fig = px.bar(
        dev_stats, x="media_avaliacao", y=dev_stats.index, orientation="h",
        labels={"media_avaliacao": "% Avaliação Positiva Média", "developer_primary": ""},
        color_discrete_sequence=[GREEN],
        hover_data={"qtd_jogos": True},
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(chart_theme(fig, "Top desenvolvedores (mín. 3 jogos no filtro)"), use_container_width=True)
    insight_card(
        "Insight",
        f"Ranking considera apenas desenvolvedores com pelo menos 3 jogos publicados no recorte atual, "
        f"para evitar que um único lançamento bem avaliado distorça o resultado."
    )
else:
    st.info("Nenhum desenvolvedor com jogos suficientes no filtro atual (mínimo 3 jogos).")

# ----------------------------------------------------------------------
# DLC e plataformas
# ----------------------------------------------------------------------
subsection_label("Seção 09", "Suporte ao jogo — DLC e multiplataforma")
c1, c2 = st.columns(2)

with c1:
    dlc_stats = df_filtered.groupby("has_dlc").agg(
        media_playtime_horas=("average_playtime_forever", lambda x: x.mean() / 60),
        media_avaliacao=("pct_pos_total", "mean"),
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
        media_avaliacao=("pct_pos_total", "mean"),
    ).reset_index()

    fig = px.bar(
        platform_stats, x="num_platforms", y="media_owners",
        labels={"num_platforms": "Nº de plataformas suportadas", "media_owners": "Estimativa média de owners"},
        color_discrete_sequence=[TEAL],
    )
    st.plotly_chart(chart_theme(fig, "Alcance estimado por nº de plataformas"), use_container_width=True)

if len(dlc_stats) == 2 and len(platform_stats) > 1:
    horas_com = dlc_stats.loc[dlc_stats["has_dlc"] == "Com DLC", "media_playtime_horas"].values[0]
    horas_sem = dlc_stats.loc[dlc_stats["has_dlc"] == "Sem DLC", "media_playtime_horas"].values[0]
    owners_1 = platform_stats["media_owners"].iloc[0]
    owners_max = platform_stats["media_owners"].max()
    insight_card(
        "Insight",
        f"Jogos com DLC têm playtime médio <b>{horas_com / max(horas_sem, 0.01):.1f}x maior</b> "
        f"({horas_com:.1f}h vs {horas_sem:.1f}h). Suporte a mais plataformas também amplia alcance: "
        f"a estimativa de owners cresce <b>{owners_max / max(owners_1, 1):.1f}x</b> de 1 para o máximo de plataformas suportadas."
    )

# ----------------------------------------------------------------------
# Estatísticas gerais
# ----------------------------------------------------------------------
subsection_label("Seção 10", "Estatísticas gerais do recorte filtrado")

with st.expander("Ver tabela de estatísticas descritivas", expanded=False):
    stats_cols = [
        "price", "pct_pos_total", "num_reviews_total", "metacritic_score",
        "average_playtime_forever", "peak_ccu", "dlc_count", "num_platforms"
    ]
    desc = df_filtered[stats_cols].describe().T
    desc.columns = ["contagem", "média", "desvio_padrão", "mín", "25%", "mediana", "75%", "máx"]
    st.dataframe(desc.round(2), use_container_width=True)

# ----------------------------------------------------------------------
# Tabela explorável
# ----------------------------------------------------------------------
subsection_label("Seção 11", "Explorar — Tabela de jogos filtrados")

cols_show = [
    "name", "release_year", "price", "genre_primary", "pct_pos_total",
    "num_reviews_total", "metacritic_score", "is_indie", "is_free",
    "has_dlc", "num_platforms"
]
st.dataframe(
    df_filtered[cols_show].sort_values("num_reviews_total", ascending=False),
    use_container_width=True,
    hide_index=True,
)