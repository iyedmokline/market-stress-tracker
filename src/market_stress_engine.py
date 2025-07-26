
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

import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import argparse
import logging
from functools import lru_cache
from math import erf, sqrt
from typing import Tuple, List
import os

# =========================
# TICKER SETUP
# =========================
# Tickers for macroeconomic and risk sentiment indicators
TICKERS = {
    "EURUSD=X": "EUR/USD",        # FX risk proxy
    "GC=F": "Gold",               # Safe haven asset
    "CL=F": "Crude Oil",          # Sensitive to geopolitical shocks
    "DX-Y.NYB": "DXY",            # Dollar index - risk aversion gauge
    "^BCOM": "Bloomberg Commodity Index",  # Broad commodity index
    "^SPGSCI": "S&P GSCI",        # Physical commodity index (oil-sensitive)
    "^VIX": "VIX",                # Implied volatility of S&P 500
    "^GVZ": "GVZ"                 # Implied volatility of Gold
}
# Selected based on interviews with FX, Options, and Commodities desks at BIAT.
# Assets include proxies for:
# - Currency stress (EUR/USD)
# - Commodity stress (Oil, Gold, Indexes)
# - Volatility shocks (VIX, GVZ)

# Custom weights for stress components
WEIGHTS = {
    "EURUSD=X": 0.07,
    "GC=F": 0.10,
    "CL=F": 0.10,
    "DX-Y.NYB": 0.05,
    "^BCOM": 0.10,
    "^SPGSCI": 0.10,
    "^VIX": 0.23,
    "^GVZ": 0.25
}
# Custom weights determined by feedback from front-desk traders.
# Weights reflect perceived relevance in capturing market-wide stress signals.
# Volatility indexes (VIX, GVZ) given higher weight due to sensitivity to systemic shocks.


# =========================
# DATA MANAGER
# =========================
class DataManager:
    def __init__(self, start_date: str, end_date: str) -> None:
        self.start_date = start_date
        self.end_date = end_date

    @lru_cache(maxsize=32)
    def get_history(self, ticker: str) -> pd.DataFrame:
        try:
            return yf.Ticker(ticker).history(start=self.start_date, end=self.end_date)
        except Exception as e:
            logging.error("Error fetching history for %s: %s", ticker, e)
            return pd.DataFrame()

# =========================
# INDICATOR BASE CLASS
# =========================
class Indicator:
    def __init__(self, data_manager: DataManager, ticker: str) -> None:
        self.dm = data_manager
        self.ticker = ticker

    def calculate(self) -> float:
        raise NotImplementedError("Must implement calculate method")

    @staticmethod
    def scale_with_history(values: np.ndarray, current: float) -> float:
        values = np.array(values)
        if len(values) < 10:
            return 50.0
        m = np.mean(values)
        s = np.std(values)
        if s < 1e-8:
            return 50.0
        z = (current - m) / s
        sc = 0.5 * (1 + erf(z / sqrt(2))) * 100
        return max(0, min(100, sc))
# Normalizes the current volatility value using a Z-score over historical data
# Then rescales to 0–100 via Gaussian CDF (erf) → gives a consistent stress level interpretation

# =========================
# VOLATILITY INDICATOR
# =========================
class VolatilityIndicator(Indicator):
    def calculate(self) -> float:
        df = self.dm.get_history(self.ticker)
        if df.empty or len(df) < 10:
            return 50.0
        df["returns"] = df["Close"].pct_change()
        volatility = df["returns"].rolling(window=10).std() * 100
        vol_series = volatility.dropna().values
        current_vol = volatility.iloc[-1]
        return Indicator.scale_with_history(vol_series, current_vol)

# =========================
# COMPOSITE STRESS
# =========================
class CompositeStress:
    def __init__(self, data_manager: DataManager) -> None:
        self.dm = data_manager
        self.indicators = [VolatilityIndicator(self.dm, ticker) for ticker in TICKERS]

    def compute(self) -> Tuple[float, List[float]]:
        values = []
        for ind in self.indicators:
            try:
                values.append(ind.calculate())
            except Exception as e:
                logging.error("Error computing indicator for %s: %s", ind.ticker, e)
                values.append(50.0)

        weights = np.array([WEIGHTS.get(ind.ticker, 0.0) for ind in self.indicators])
        values_array = np.array(values)

        if weights.sum() > 0:
            composite = np.average(values_array, weights=weights)
        else:
            composite = np.mean(values_array)

        composite = max(0, min(100, composite))
        return composite, values

# =========================
# PLOTLY GAUGE
# =========================
def gauge_plot(value: float, reference_value: float) -> None:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={
            'text': "<b>Market Stress Index</b><br><span style='font-size:16px;color:gray'>Composite Volatility Tracker</span>",
            'font': {'size': 24}
        },
        number={'font': {'size': 48, 'family': 'Montserrat, Arial'},'valueformat': ".2f"},
        delta={
            'reference': reference_value,
            'position': "bottom",
            'increasing': {'color': "#C0392B"},
            'decreasing': {'color': "#27AE60"},
            'valueformat': ".2f"
        },
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
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
        paper_bgcolor="rgba(250, 250, 255, 1)",
        font={'color': "black", 'family': "Montserrat, Arial"},
        margin=dict(t=80, b=30, l=20, r=20)
    )

    fig.show()

# =========================
# RADAR PLOT - COMPONENTS
# =========================

def radar_plot(individual_values: List[float]) -> None:
    labels = list(TICKERS.values())
    values = individual_values + [individual_values[0]]
    labels_closed = labels + [labels[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels_closed,
        fill='toself',
        name='Stress Score',
        line=dict(color='rgba(192, 57, 43, 1)', width=3),
        marker=dict(size=8),
        fillcolor='rgba(192, 57, 43, 0.45)'
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(250, 250, 255, 1)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showline=True,
                showgrid=True,
                gridcolor='rgba(0,0,0,0.15)',
                gridwidth=1.2,
                linecolor='rgba(0,0,0,0.4)',
                linewidth=1.2,
                tickfont=dict(size=13),
                tickangle=0,
                tickcolor='gray'
            ),
            angularaxis=dict(
                tickfont=dict(size=13),
                rotation=90,
                direction='clockwise',
                gridcolor='rgba(0,0,0,0.15)',
                gridwidth=1.2,
                linecolor='rgba(0,0,0,0.3)'
            )
        ),
        showlegend=False,
        title=dict(
            text="<b>Breakdown of Market Stress by Component</b>",
            font=dict(size=22),
            x=0.5
        ),
        font=dict(family='Montserrat, Arial', size=14),
        paper_bgcolor='rgba(250, 250, 255, 1)',
        margin=dict(t=80, b=40, l=40, r=40)
    )

    fig.show()

# =========================
# MAIN FUNCTION
# =========================
def main() -> None:
    parser = argparse.ArgumentParser(description="Compute composite market stress indicator.")
    parser.add_argument("--start_date", type=str, default=None, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end_date", type=str, default=None, help="End date in YYYY-MM-DD format")
    args = parser.parse_args()

    today = datetime.date.today()
    default_end = today - datetime.timedelta(days=1)
    default_start = default_end - datetime.timedelta(days=365 * 3)

    start_date = args.start_date if args.start_date else str(default_start)
    end_date = args.end_date if args.end_date else str(default_end)

    logging.info("Using date range from %s to %s", start_date, end_date)
    dm = DataManager(start_date, end_date)
    stress = CompositeStress(dm)
    comp_value, individual_values = stress.compute()

    # Compute the last business day before the end date
    last_business_day = pd.bdate_range(end=pd.to_datetime(end_date), periods=2)[-2]
    yesterday_end_str = last_business_day.strftime('%Y-%m-%d')
    yesterday_start_str = (last_business_day - timedelta(days=365 * 3)).strftime('%Y-%m-%d')

    dm_yesterday = DataManager(yesterday_start_str, yesterday_end_str)
    stress_yesterday = CompositeStress(dm_yesterday)
    comp_yesterday, _ = stress_yesterday.compute()


    for (symbol, name), val in zip(TICKERS.items(), individual_values):
        print(f"{name:30s}: {round(val, 2)}")
    print(f"Composite Market Stress Index: {round(comp_value, 2)}")

    gauge_plot(comp_value, comp_yesterday)
    radar_plot(individual_values)


    # Save results to a CSV file
    df_out = pd.DataFrame({
        "Ticker": list(TICKERS.values()),
        "Stress Score": [round(val, 2) for val in individual_values]
    })
    df_out.loc[len(df_out)] = ["Composite", round(comp_value, 2)]
    df_out.to_csv("market_stress_data.csv", index=False)
    print("✅ Results saved to market_stress_data.csv")

main()