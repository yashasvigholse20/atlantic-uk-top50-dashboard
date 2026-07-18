# 🇬🇧 Atlantic UK Top 50 — Structural & Cultural Analysis

**Live Dashboard:** [atlantic-uk-top50-dashboard.streamlit.app](https://atlantic-uk-top50-dashboard.streamlit.app/)

![Dashboard Preview](assets/dashboard_preview.png)

A structural and cultural analysis of the UK Top 50 music chart, built for **Atlantic Recording Corporation** as part of an Industrial Internship Program (Unified Mentor). The project analyzes 555 daily Top 50 snapshots to uncover artist dominance patterns, collaboration dynamics, content composition, and release strategy — informing UK-specific signing, marketing, and release decisions rather than assuming US market behavior applies.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## 📊 Project Overview

The UK music market is culturally distinct from the US in ways that matter for label strategy:
- Strong domestic artist representation (or lack thereof)
- High prevalence of collaborations
- Listener sensitivity to explicit content
- Different album vs. single consumption behavior

This project analyzes daily UK Top 50 playlist snapshots to answer:
- How is artist dominance distributed in the UK market?
- Do UK charts favor domestic or international artists?
- How do collaborations influence chart presence?
- Does explicit content perform differently in the UK?
- How does album structure affect chart success?

---

## 🗂️ Dataset

| Field | Description |
|---|---|
| `date` | Date of playlist snapshot |
| `position` | Chart rank (1–50) |
| `song` | Song title |
| `artist` | Artist(s), `&`-delimited for collaborations |
| `popularity` | Popularity score |
| `duration_ms` | Track duration (milliseconds) |
| `album_type` | Single / Album / Compilation |
| `total_tracks` | Number of tracks on the parent album |
| `is_explicit` | Explicit content flag |
| `album_cover_url` | Album artwork URL |

**Scale:** 555 daily snapshots · 27,750 validated chart entries · 361 unique artists

---

## 🔍 Methodology

1. **Data Validation & Standardization** — deduplication, date parsing, artist name normalization, collaboration splitting on `&`, with correction for band names containing `&` (e.g. *Chase & Status*, *Richy Mitch & The Coal Miners*) that were incorrectly split by the naive delimiter rule
2. **Artist Dominance & Diversity** — appearance counts, Artist Concentration Index (HHI), UK vs. International origin tagging
3. **Collaboration Structure** — solo vs. collaborative split, average collaborators per track, collaboration rate by rank tier, artist collaboration network
4. **Content Explicitness** — explicit content share by rank tier, format, and artist origin
5. **Album Structure & Release Strategy** — single vs. album presence, album size vs. chart performance
6. **Track Duration & Format** — duration distribution, duration vs. popularity/position correlation
7. **Market Structure Metrics** — composite KPI roll-up (concentration, diversity, variety indices)

---

## 📈 Key Findings

| KPI | Value | Interpretation |
|---|---|---|
| Artist Concentration Index (HHI) | 0.0116 (115.9/10,000) | Low concentration — highly competitive market, no single dominant artist |
| Unique Artist Count | 361 | Across 555 daily snapshots |
| Top 5 Artist Share | 15.3% | Top artists hold a modest share of total chart weight |
| Diversity Score | 0.0130 | Unique artists relative to total chart entries |
| Collaboration Ratio | 17.8% | Most UK Top 50 tracks are solo (82.2%) |
| Explicit Content Share | 32.0% | Rises to 40.4% within the Top 10 specifically |
| Single vs. Album Ratio | 0.66 | Albums outnumber singles in raw presence, but singles dominate the Top 10 (54% vs. 32% in Top 26–50) |
| Content Variety Index | 51.5 / 100 | Composite of artist, format, and content variety |

**Standout insights:**
- **International artists outnumber UK artists ~66% to 34%** among chart weight — the UK Top 50 leans international despite being a domestic chart
- **Explicit content is *more* common at the top of the chart, not less** (40.4% in Top 10 vs. 28.0% in Top 26–50), driven primarily by international artists (36.4% explicit) rather than UK acts (27.0% explicit)
- **Singles punch above their weight at the top of the chart**; albums dominate lower-chart presence — release strategy should differ depending on whether the goal is Top 10 penetration or catalog depth
- **Track duration has no meaningful relationship with chart success** (correlation ≈ 0.07) — a legitimate null result worth stating plainly

---

## 🖥️ Dashboard

Interactive Streamlit dashboard with 6 modules:

- **Overview** — market-wide KPI cards, unique artist trend, UK vs. International split
- **Artist Dominance** — leaderboard, explicit rate by origin, appearance distribution
- **Collaboration** — rank-tier collaboration rates, monthly trend, draggable artist collaboration network graph
- **Explicit Content** — rank-tier and format breakdowns, popularity comparison
- **Album Structure** — format distribution, album size vs. chart position
- **Duration** — duration distribution, correlation with popularity and position

**Filters:** date range · artist multiselect · solo/collaboration toggle · album type

### Run locally

```bash
git clone https://github.com/yashasvigholse20/atlantic-uk-top50-dashboard.git
cd atlantic-uk-top50-dashboard
pip install -r requirements.txt
streamlit run app.py
```

---

## 🛠️ Tech Stack

- **Analysis:** Python, Pandas, NumPy (Google Colab)
- **Dashboard:** Streamlit, Plotly, NetworkX, PyVis
- **Deployment:** Streamlit Community Cloud

---

## 📁 Repository Structure
