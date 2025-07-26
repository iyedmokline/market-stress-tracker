<h1 align="center">📈 Market Stress Tracker</h1>

<p align="center">
  <b>Composite Financial Stress Dashboard</b><br>
  Built during a front-office trading internship at <b>BIAT</b> (Banque Internationale Arabe de Tunisie) – Summer 2025
</p>

<p align="center">
  <a href="https://github.com/mmokline/market-stress-tracker/stargazers">
  </a>
  <a href="https://github.com/mmokline/market-stress-tracker/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/mmokline/market-stress-tracker" alt="MIT License"/>
  </a>
</p>

---

## 🔍 Overview

The **Market Stress Tracker** is a real-time financial dashboard designed to measure cross-asset volatility and risk sentiment.  
It aggregates normalized volatility signals from **8 macroeconomic and risk-sensitive assets** into a single interpretable stress index (0–100 scale), with visual insights via radar and gauge charts.

Developed during a **front-office internship at BIAT**, this project integrates practical knowledge from FX, Options, and Commodities desks to design and weight each component.

---

## ⚙️ Tech Stack

- 🐍 Python 3.12
- 📊 Streamlit
- 📉 Plotly (Gauge + Radar)
- 📈 yFinance API
- 🧠 Numpy · Pandas · Matplotlib

---

## 📊 What the Index Represents

- 🧮 Each asset's 10-day rolling volatility is compared to its 3-year history and converted to a normalized **stress score (0–100)** using a Gaussian CDF.
- 🧭 Final score = **Weighted Average of All 8 Scores**.
- 📌 Asset weights reflect **real trader feedback** on their relevance during market stress.

---

## 🧮 Components & Weights

| Asset                | Role                          | Weight |
|---------------------|-------------------------------|--------|
| EUR/USD             | FX risk proxy                 | 0.07   |
| Gold                | Safe-haven asset              | 0.10   |
| Crude Oil           | Geopolitical sensitivity      | 0.10   |
| DXY Index           | USD strength, risk-off flows  | 0.05   |
| BCOM Index          | Commodity sentiment (broad)   | 0.10   |
| S&P GSCI            | Oil-heavy commodity basket    | 0.10   |
| VIX                 | US equity volatility          | 0.23   |
| GVZ                 | Gold volatility               | 0.25   |

✅ Chosen after interviewing FX, Options, and Commodities desks  
📊 VIX and GVZ dominate to reflect systemic risk sensitivity

---

## 🖥️ Features

- 📆 Select any date → automatic retrieval of 3 years of historical data
- 📈 Live composite stress score (0–100)
- 🌪️ Radar chart of component scores
- 🎯 Gauge chart with delta vs previous day
- 💾 Export results to CSV
- 🧮 Offline CLI mode for scripting or batch analysis
- 📉 Bonus line chart of historical index values (`graphe.py`)

---

## 🚀 Usage

### ▶️ Run with Streamlit:

```bash
pip install -r requirements.txt
streamlit run market_stress_dashboard.py

market-stress-tracker/
├── src/
│   ├── market_stress_engine.py   # Core logic (data, indicators, plots)
│   ├── dashboard_app.py          # Streamlit interface
│   ├── stress_index_plot.py      # Historical line plot
│   └── __init__.py               # Package marker
├── requirements.txt              # Dependencies
└── README.md                     # You're here



