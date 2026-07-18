"""
Atlantic Recording Corporation - UK Top 50 Structural Analysis Dashboard
Run locally with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import ast
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Atlantic UK Top 50 | Structural Analysis",
    page_icon="🇬🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# DATA LOADING
# ============================================
@st.cache_data
def load_data():
    df = pd.read_csv("atlantic_uk_final.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["artist_list"] = df["artist_list"].apply(ast.literal_eval)

    exploded = pd.read_csv("atlantic_uk_exploded.csv")
    exploded["date"] = pd.to_datetime(exploded["date"])

    artist_summary = pd.read_csv("artist_dominance_summary.csv")
    edges = pd.read_csv("collaboration_network_edges.csv")
    kpi_summary = pd.read_csv("kpi_summary.csv")

    return df, exploded, artist_summary, edges, kpi_summary

df, exploded, artist_summary, edges, kpi_summary = load_data()

RANK_ORDER = ["Top 10", "Top 11-25", "Top 26-50"]
DURATION_ORDER = ["Short-form (<2.5 min)", "Standard (2.5-3.5 min)", "Extended (3.5-4.5 min)", "Long-form (4.5+ min)"]

# ============================================
# COLORED KPI CARD STYLING
# ============================================
st.markdown("""
<style>
.kpi-card {
    border-radius: 12px;
    padding: 18px 16px;
    margin-bottom: 12px;
    color: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.kpi-label {
    font-size: 13px;
    opacity: 0.85;
    margin-bottom: 6px;
    font-weight: 500;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.1;
}
.kpi-help {
    font-size: 11px;
    opacity: 0.75;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)


def kpi_card(label, value, color, help_text=None):
    help_html = f'<div class="kpi-help">{help_text}</div>' if help_text else ""
    st.markdown(
        f"""
        <div class="kpi-card" style="background-color:{color};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {help_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================
# SIDEBAR FILTERS
# ============================================
st.sidebar.title("🎛️ Filters")

min_date, max_date = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

all_artists = sorted(exploded["artist_single"].unique())
artist_filter = st.sidebar.multiselect(
    "Filter by artist(s)",
    options=all_artists,
    default=[]
)

collab_toggle = st.sidebar.radio(
    "Track type",
    options=["All", "Solo only", "Collaboration only"],
    index=0
)

album_type_filter = st.sidebar.multiselect(
    "Album type",
    options=sorted(df["album_type"].unique()),
    default=sorted(df["album_type"].unique())
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Dataset: {df['date'].nunique()} daily snapshots | {len(df):,} total chart entries")

# ---- Apply filters ----
mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
mask &= df["album_type"].isin(album_type_filter)

if collab_toggle == "Solo only":
    mask &= ~df["is_collab"]
elif collab_toggle == "Collaboration only":
    mask &= df["is_collab"]

if artist_filter:
    mask &= df["artist_list"].apply(lambda lst: any(a in artist_filter for a in lst))

fdf = df[mask].copy()

if fdf.empty:
    st.warning("No data matches the current filter selection. Try widening your filters.")
    st.stop()

f_exploded = exploded[
    (exploded["date"].dt.date >= start_date) & (exploded["date"].dt.date <= end_date)
].copy()
if artist_filter:
    f_exploded = f_exploded[f_exploded["artist_single"].isin(artist_filter)]

# ============================================
# HEADER
# ============================================
st.title("🇬🇧 Atlantic UK Top 50 — Structural & Cultural Analysis")
st.markdown(
    "Structural intelligence on artist dominance, collaboration patterns, content composition, "
    "and release strategy in the UK music market — for Atlantic Recording Corporation."
)

# ============================================
# TABS
# ============================================
tab_overview, tab_artists, tab_collab, tab_explicit, tab_albums, tab_duration = st.tabs(
    ["📊 Overview", "🎤 Artist Dominance", "🤝 Collaboration", "🔞 Explicit Content", "💿 Album Structure", "⏱️ Duration"]
)

# ============================================
# TAB 1: OVERVIEW
# ============================================
with tab_overview:
    st.header("Market Structure KPIs")

    hhi_val = kpi_summary.loc[kpi_summary["KPI"] == "Artist Concentration Index (HHI)", "Value"].values[0]
    unique_artists_val = kpi_summary.loc[kpi_summary["KPI"] == "Unique Artist Count", "Value"].values[0]
    top5_val = kpi_summary.loc[kpi_summary["KPI"] == "Playlist Concentration Ratio (Top 5)", "Value"].values[0]
    div_val = kpi_summary.loc[kpi_summary["KPI"] == "Diversity Score", "Value"].values[0]
    collab_val = kpi_summary.loc[kpi_summary["KPI"] == "Collaboration Ratio", "Value"].values[0]
    explicit_val = kpi_summary.loc[kpi_summary["KPI"] == "Explicit Content Share", "Value"].values[0]
    ratio_val = kpi_summary.loc[kpi_summary["KPI"] == "Single vs Album Ratio", "Value"].values[0]
    variety_val = kpi_summary.loc[kpi_summary["KPI"] == "Content Variety Index", "Value"].values[0]

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi_card("Artist Concentration (HHI)", hhi_val, "#1DB954", "Low = competitive market")
    with k2: kpi_card("Unique Artists Charted", unique_artists_val, "#C8102E")
    with k3: kpi_card("Top 5 Artist Share", top5_val, "#012169")
    with k4: kpi_card("Diversity Score", div_val, "#F5A623")

    k5, k6, k7, k8 = st.columns(4)
    with k5: kpi_card("Collaboration Ratio", collab_val, "#9B59B6")
    with k6: kpi_card("Explicit Content Share", explicit_val, "#17A2B8")
    with k7: kpi_card("Single vs Album Ratio", ratio_val, "#E67E22")
    with k8: kpi_card("Content Variety Index", variety_val, "#2ECC71")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Daily Unique Artist Count Over Time")
        daily_unique = f_exploded.groupby("date")["artist_single"].nunique().reset_index()
        fig = px.line(daily_unique, x="date", y="artist_single",
                      labels={"artist_single": "Unique Artists", "date": "Date"})
        fig.update_traces(line_color="#1DB954")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("UK vs International Artist Split")
        origin_counts = f_exploded[f_exploded["origin"] != "Unclassified"]["origin"].value_counts()
        fig = px.pie(values=origin_counts.values, names=origin_counts.index,
                     color=origin_counts.index,
                     color_discrete_map={"UK": "#C8102E", "International": "#012169"})
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Among artists with confirmed origin tags (~75% of chart weight)")

    st.markdown("---")
    st.subheader("Full KPI Reference Table")
    st.dataframe(kpi_summary, use_container_width=True, hide_index=True)

# ============================================
# TAB 2: ARTIST DOMINANCE
# ============================================
with tab_artists:
    st.header("Artist Dominance Leaderboard")

    top_n = st.slider("Show top N artists", 5, 50, 20)

    leaderboard = f_exploded.groupby("artist_single").size().sort_values(ascending=False).head(top_n).reset_index()
    leaderboard.columns = ["Artist", "Chart Appearances"]
    leaderboard = leaderboard.merge(
        artist_summary[["artist", "origin"]], left_on="Artist", right_on="artist", how="left"
    ).drop(columns="artist")
    leaderboard["origin"] = leaderboard["origin"].fillna("Unclassified")

    fig = px.bar(
        leaderboard.sort_values("Chart Appearances"),
        x="Chart Appearances", y="Artist", orientation="h",
        color="origin",
        color_discrete_map={"UK": "#C8102E", "International": "#012169", "Unclassified": "#888888"},
        height=max(400, top_n * 22)
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Explicit Rate by Artist Origin")
        origin_explicit = fdf.copy()
        origin_explicit["origin"] = origin_explicit["primary_artist"].map(
            dict(zip(artist_summary["artist"], artist_summary["origin"]))
        ).fillna("Unclassified")
        origin_explicit = origin_explicit[origin_explicit["origin"] != "Unclassified"]
        rate = origin_explicit.groupby("origin")["is_explicit"].mean().reset_index()
        rate["is_explicit"] = rate["is_explicit"] * 100
        fig2 = px.bar(rate, x="origin", y="is_explicit",
                      labels={"is_explicit": "Explicit %", "origin": "Origin"},
                      color="origin", color_discrete_map={"UK": "#C8102E", "International": "#012169"})
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Unique Artists per Day (Distribution)")
        daily_unique = f_exploded.groupby("date")["artist_single"].nunique()
        fig3 = px.histogram(daily_unique, nbins=20, labels={"value": "Unique Artists per Day"})
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Artist Leaderboard Table")
    st.dataframe(leaderboard, use_container_width=True, hide_index=True)

# ============================================
# TAB 3: COLLABORATION STRUCTURE
# ============================================
with tab_collab:
    st.header("Collaboration Structure Analysis")

    c1, c2, c3 = st.columns(3)
    collab_rate = fdf["is_collab"].mean() * 100
    avg_collab_all = fdf["num_collaborators"].mean()
    avg_collab_only = fdf.loc[fdf["is_collab"], "num_collaborators"].mean() if fdf["is_collab"].any() else 0

    with c1: kpi_card("Collaboration Rate", f"{collab_rate:.1f}%", "#9B59B6")
    with c2: kpi_card("Avg Collaborators (all tracks)", f"{avg_collab_all:.2f}", "#1DB954")
    with c3: kpi_card("Avg Collaborators (collab tracks)", f"{avg_collab_only:.2f}", "#012169")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Collaboration Rate by Rank Group")
        rank_collab = fdf.groupby("rank_group", observed=True)["is_collab"].mean().reindex(RANK_ORDER) * 100
        fig = px.bar(rank_collab.reset_index(), x="rank_group", y="is_collab",
                     labels={"is_collab": "Collaboration %", "rank_group": "Rank Group"})
        fig.update_traces(marker_color="#1DB954")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Collaboration Rate Over Time")
        fdf["month"] = fdf["date"].dt.to_period("M").astype(str)
        month_trend = fdf.groupby("month")["is_collab"].mean().reset_index()
        month_trend["is_collab"] = month_trend["is_collab"] * 100
        fig2 = px.line(month_trend, x="month", y="is_collab",
                       labels={"is_collab": "Collaboration %", "month": "Month"})
        fig2.update_traces(line_color="#C8102E")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("🕸️ Artist Collaboration Network")
    st.caption("Drag nodes to explore. Node size = total collaborations, edge thickness = number of shared tracks.")

    top_edges_n = st.slider("Show top N collaboration pairs", 10, 150, 40)
    display_edges = edges.head(top_edges_n)

    if artist_filter:
        display_edges = edges[
            edges["artist_1"].isin(artist_filter) | edges["artist_2"].isin(artist_filter)
        ]
        if display_edges.empty:
            st.info("No collaboration edges found for the selected artist(s).")

    if not display_edges.empty:
        G = nx.Graph()
        for _, row in display_edges.iterrows():
            G.add_edge(row["artist_1"], row["artist_2"], weight=row["weight"])

        net = Network(height="600px", width="100%", bgcolor="#0e1117", font_color="white", notebook=False)
        net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=120)

        degrees = dict(G.degree(weight="weight"))
        for node in G.nodes():
            size = 10 + (degrees.get(node, 1) * 1.5)
            net.add_node(node, label=node, size=size, color="#1DB954")

        for u, v, d in G.edges(data=True):
            net.add_edge(u, v, value=d["weight"], color="#888888", title=f"{d['weight']} shared tracks")

        net.save_graph("network.html")
        with open("network.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=620)

    st.subheader("Strongest Collaboration Pairs")
    st.dataframe(display_edges, use_container_width=True, hide_index=True)

# ============================================
# TAB 4: EXPLICIT CONTENT
# ============================================
with tab_explicit:
    st.header("Content Explicitness Analysis")

    e1, e2 = st.columns(2)
    explicit_share = fdf["is_explicit"].mean() * 100
    top10_explicit = fdf[fdf["position"] <= 10]["is_explicit"].mean() * 100 if (fdf["position"] <= 10).any() else 0
    with e1: kpi_card("Overall Explicit Share", f"{explicit_share:.1f}%", "#C8102E")
    with e2: kpi_card("Explicit Share (Top 10 only)", f"{top10_explicit:.1f}%", "#17A2B8")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Explicit Content by Rank Group")
        rank_explicit = fdf.groupby("rank_group", observed=True)["is_explicit"].mean().reindex(RANK_ORDER) * 100
        fig = px.bar(rank_explicit.reset_index(), x="rank_group", y="is_explicit",
                     labels={"is_explicit": "Explicit %", "rank_group": "Rank Group"})
        fig.update_traces(marker_color="#C8102E")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Explicit Content Trend Over Time")
        fdf["month"] = fdf["date"].dt.to_period("M").astype(str)
        month_explicit = fdf.groupby("month")["is_explicit"].mean().reset_index()
        month_explicit["is_explicit"] = month_explicit["is_explicit"] * 100
        fig2 = px.line(month_explicit, x="month", y="is_explicit",
                       labels={"is_explicit": "Explicit %", "month": "Month"})
        fig2.update_traces(line_color="#012169")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Explicit Rate by Release Format")
        fmt_explicit = fdf.groupby("album_type")["is_explicit"].mean().reset_index()
        fmt_explicit["is_explicit"] = fmt_explicit["is_explicit"] * 100
        fig3 = px.bar(fmt_explicit, x="album_type", y="is_explicit",
                      labels={"is_explicit": "Explicit %", "album_type": "Release Format"})
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Popularity: Explicit vs Clean")
        pop_explicit = fdf.groupby("is_explicit")["popularity"].mean().reset_index()
        pop_explicit["is_explicit"] = pop_explicit["is_explicit"].map({True: "Explicit", False: "Clean"})
        fig4 = px.bar(pop_explicit, x="is_explicit", y="popularity",
                      labels={"popularity": "Avg Popularity", "is_explicit": ""})
        st.plotly_chart(fig4, use_container_width=True)

# ============================================
# TAB 5: ALBUM STRUCTURE
# ============================================
with tab_albums:
    st.header("Album Structure & Release Strategy")

    a1, a2 = st.columns(2)
    single_count = (fdf["album_type"] == "single").sum()
    album_count = (fdf["album_type"] == "album").sum()
    ratio = single_count / album_count if album_count else 0
    with a1: kpi_card("Single vs Album Ratio", f"{ratio:.2f}", "#E67E22")
    with a2: kpi_card("Total Compilation Entries", int((fdf["album_type"] == "compilation").sum()), "#9B59B6")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Release Format Distribution")
        fmt_counts = fdf["album_type"].value_counts().reset_index()
        fmt_counts.columns = ["album_type", "count"]
        fig = px.pie(fmt_counts, values="count", names="album_type")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Release Format by Rank Group")
        fmt_by_rank = pd.crosstab(fdf["rank_group"], fdf["album_type"], normalize="index").reindex(RANK_ORDER) * 100
        fig2 = px.bar(fmt_by_rank.reset_index().melt(id_vars="rank_group"),
                      x="rank_group", y="value", color="album_type", barmode="stack",
                      labels={"value": "%", "rank_group": "Rank Group", "album_type": "Format"})
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Album Size (Total Tracks) vs Average Chart Position")
    album_only = fdf[fdf["album_type"] == "album"]
    if not album_only.empty:
        size_pos = album_only.groupby("album_size_bucket", observed=True)["position"].mean().reset_index()
        fig3 = px.bar(size_pos, x="album_size_bucket", y="position",
                      labels={"position": "Avg Position (lower=better)", "album_size_bucket": "Album Size"})
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No album-type tracks in the current filter selection.")

# ============================================
# TAB 6: DURATION
# ============================================
with tab_duration:
    st.header("Track Duration & Format Analysis")

    d1, d2 = st.columns(2)
    with d1: kpi_card("Avg Duration", f"{fdf['duration_min'].mean():.2f} min", "#1DB954")
    with d2: kpi_card("Median Duration", f"{fdf['duration_min'].median():.2f} min", "#012169")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Duration Distribution")
        fig = px.histogram(fdf, x="duration_min", nbins=40,
                           labels={"duration_min": "Duration (minutes)"})
        fig.update_traces(marker_color="#1DB954")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Duration by Rank Group")
        rank_dur = fdf.groupby("rank_group", observed=True)["duration_min"].mean().reindex(RANK_ORDER).reset_index()
        fig2 = px.bar(rank_dur, x="rank_group", y="duration_min",
                      labels={"duration_min": "Avg Duration (min)", "rank_group": "Rank Group"})
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Duration vs Popularity Bucket")
        pop_dur = fdf.groupby("popularity_bucket", observed=True)["duration_min"].mean().reset_index()
        fig3 = px.bar(pop_dur, x="popularity_bucket", y="duration_min",
                      labels={"duration_min": "Avg Duration (min)", "popularity_bucket": "Popularity Bucket"})
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Duration by Release Format")
        fmt_dur = fdf.groupby("album_type")["duration_min"].mean().reset_index()
        fig4 = px.bar(fmt_dur, x="album_type", y="duration_min",
                      labels={"duration_min": "Avg Duration (min)", "album_type": "Format"})
        st.plotly_chart(fig4, use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption(
    "Atlantic Recording Corporation | UK Top 50 Structural Analysis | "
    f"Data: {df['date'].min().date()} to {df['date'].max().date()} ({df['date'].nunique()} daily snapshots)"
)
