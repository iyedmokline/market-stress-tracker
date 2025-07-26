
"""
Market Stress Tracker
---------------------
This project was developed as part of my internship on the front-office trading floor at BIAT (Banque Internationale Arabe de Tunisie) in Summer 2025.

The tool tracks composite financial stress by aggregating volatility measures across 8 financial assets selected after interviewing FX, Options, and Commodities desks.

Main Components:
- Real-time dashboard with Streamlit
- Composite index with dynamic weighting
- Volatility normalization via Z-score
- Visuals: Radar, Gauge

Author: Mohamed Iyed Mokline – ENSAE Paris
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objects as go
from plotly.graph_objects import Indicator, Figure

from src.market_stress_engine import (
    DataManager,
    CompositeStress,
    TICKERS,
    WEIGHTS,
    radar_plot
)

st.markdown("Developed during a front-office trading internship at BIAT (Summer 2025).")

# -----------------------------
# Streamlit Page Configuration
# -----------------------------
st.set_page_config(page_title="Market Stress Tracker", layout="wide")
st.title("📊 Market Stress Dashboard")
st.markdown("Interactive market stress analysis based on weighted multi-asset indicators.")

# -----------------------------
# 1. Date Selection
# -----------------------------
end_date = st.date_input("📅 Today Date", value=date.today() - timedelta(days=1))
start_date = end_date - timedelta(days=365 * 3)

# -----------------------------
# 2. Compute Stress Index
# -----------------------------
dm = DataManager(str(start_date), str(end_date))
stress = CompositeStress(dm)
composite_val, individual_vals = stress.compute()

# -----------------------------
# 3. Display Global Stress Metric
# -----------------------------
st.metric("Global Stress Index", f"{composite_val:.2f}")

# -----------------------------
# 4. Display Component Scores
# -----------------------------
df_scores = pd.DataFrame({
    "Component": list(TICKERS.values()),
    "Score": [round(val, 2) for val in individual_vals],
    "Weight": [WEIGHTS[k] for k in TICKERS]
})
df_scores["Weighted Score"] = df_scores["Score"] * df_scores["Weight"]
df_scores.set_index("Component", inplace=True)

st.dataframe(df_scores)

# -----------------------------
# 5. Export CSV Button
# -----------------------------
csv = df_scores.to_csv().encode('utf-8')
st.download_button("⬇️ Download CSV", csv, "stress_scores.csv", "text/csv")

# -----------------------------
# 6. Radar Chart Visualization
# -----------------------------
labels = list(TICKERS.values())
values = individual_vals + [individual_vals[0]]
labels_closed = labels + [labels[0]]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=values,
    theta=labels_closed,
    fill='toself',
    name='Stress Score',
    line=dict(color='rgba(192, 57, 43, 1)', width=3),
    marker=dict(size=8),
    fillcolor='rgba(192, 57, 43, 0.45)'
))
fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100]),
        angularaxis=dict(rotation=90, direction='clockwise')
    ),
    title="<b>Component Radar</b>",
    showlegend=False
)
st.plotly_chart(fig_radar, use_container_width=True)

# -----------------------------
# 7. Compute Previous Day's Index for Delta
# -----------------------------
last_business_day = pd.bdate_range(end=pd.to_datetime(end_date), periods=2)[-2]
yesterday_end_str = last_business_day.strftime('%Y-%m-%d')
yesterday_start_str = (last_business_day - timedelta(days=365 * 3)).strftime('%Y-%m-%d')

dm_yesterday = DataManager(yesterday_start_str, yesterday_end_str)
stress_yesterday = CompositeStress(dm_yesterday)
composite_val_yesterday, _ = stress_yesterday.compute()

# -----------------------------
# 8. Gauge Indicator Visualization
# -----------------------------
def gauge_plot(value: float, reference_value: float) -> None:
    """
    Display a styled gauge chart with current market stress value
    and comparison to a reference value (typically the previous day).
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={
            'text': "<span style='font-size:24px; color:white;'><b>Market Stress Index</b></span><br><span style='font-size:16px; color:gray;'>Composite Volatility Tracker</span>",
            'font': {'size': 24}
        },
        number={
            'font': {'size': 48, 'family': 'Montserrat, Arial', 'color': 'white'},
            'valueformat': ".2f"
        },
        delta={
            'reference': reference_value,
            'position': "bottom",
            'increasing': {'color': "#C0392B"},
            'decreasing': {'color': "#27AE60"},
            'valueformat': ".2f"
        },
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray", 'tickfont': {'color': 'white'}},
            'bar': {'color': "#000000", 'thickness': 0.15},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 33], 'color': 'rgba(46, 204, 113, 0.8)'},
                {'range': [33, 66], 'color': 'rgba(241, 196, 15, 0.8)'},
                {'range': [66, 100], 'color': 'rgba(231, 76, 60, 0.8)'}
            ],
            'threshold': {
                'line': {'color': "#000", 'width': 6},
                'thickness': 0.8,
                'value': value
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font={'color': "black", 'family': "Montserrat, Arial"},
        margin=dict(t=80, b=30, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)

gauge_plot(composite_val, composite_val_yesterday)
