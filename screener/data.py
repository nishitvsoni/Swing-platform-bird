"""
Data access layer: NSE/BSE symbol universe fetching and sector RSI caching.
Kept separate from scoring logic so data sources can be swapped later.
"""

import io

import pandas as pd
import requests
import streamlit as st
import ta
import yfinance as yf

# Sector Index Mapping for Relative Strength Comparison
SECTOR_MAP = {
    "Financial Services": "^NSEBANK",
    "Technology": "^CNXIT",
    "Healthcare": "^CNXPHARMA",
    "Consumer Cyclical": "^CNXAUTO",
    "Basic Materials": "^CNXMETAL",
    "Energy": "^CNXENERGY",
    "Consumer Defensive": "^CNXFMCG",
}

DEFAULT_FALLBACK_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "SBIN.NS", "LT.NS",
]


@st.cache_data(ttl=3600)
def fetch_sector_rsis() -> dict:
    """Fetch current 14-day RSI for each sector index + Nifty, cached for 1 hour."""
    sector_rsis = {}
    sector_tickers = list(SECTOR_MAP.values()) + ["^NSEI"]
    for t in sector_tickers:
        try:
            hist = yf.Ticker(t).history(period="6m")
            if not hist.empty and len(hist) >= 20:
                rsi_series = ta.momentum.rsi(hist["Close"], window=14)
                sector_rsis[t] = round(rsi_series.iloc[-1], 2)
        except Exception:
            sector_rsis[t] = 50.0  # Neutral fallback
    return sector_rsis


@st.cache_data(ttl=86400)
def fetch_all_nse_symbols() -> list:
    """Fetch the full NSE equity list, with a Nifty 500 mirror as fallback."""
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            df = pd.read_csv(io.StringIO(res.text))
            return [f"{str(sym).strip()}.NS" for sym in df["SYMBOL"].dropna().unique()]
    except Exception:
        pass

    try:
        fallback_url = (
            "https://raw.githubusercontent.com/kprohith/nse-stock-analysis/"
            "master/ind_nifty500list.csv"
        )
        df = pd.read_csv(fallback_url)
        return [f"{str(sym).strip()}.NS" for sym in df["Symbol"].dropna().unique()]
    except Exception:
        return DEFAULT_FALLBACK_SYMBOLS
