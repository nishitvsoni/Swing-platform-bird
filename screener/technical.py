"""
Technical scoring: EMA trend, 20-day ROC, sector-relative RSI, volume surge.
"""

import pandas as pd
import ta


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add EMA20/EMA50/RSI/ROC20/ATR/volume-SMA/turnover columns to price history."""
    df = df.copy()
    df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
    df["ROC20"] = ta.momentum.roc(df["Close"], window=20)
    df["ATR"] = ta.volatility.average_true_range(
        df["High"], df["Low"], df["Close"], window=14
    )
    df["Vol_SMA20"] = df["Volume"].rolling(20).mean()
    df["Turnover_20"] = (df["Volume"] * df["Close"]).rolling(20).mean()
    return df


def score_technical(latest: pd.Series, market_rsi: float, checks: dict) -> tuple:
    """
    Score a stock's latest row against the enabled technical checks.

    market_rsi replaces the old per-sector RSI (which came from Yahoo Finance
    sector indices, no longer available) - it's the median RSI across the
    scanned universe for that day, so the check becomes "stock RSI > market RSI".

    checks: dict of booleans - use_ema, use_roc, use_market_rsi, use_vol
    Returns (tech_score_pct, passed_count, total_count).
    """
    total, passed = 0, 0

    if checks.get("use_ema"):
        total += 1
        if latest["Close"] > latest["EMA20"] > latest["EMA50"]:
            passed += 1

    if checks.get("use_roc"):
        total += 1
        if latest["ROC20"] > 0:
            passed += 1

    if checks.get("use_market_rsi"):
        total += 1
        if latest["RSI"] > market_rsi:
            passed += 1

    if checks.get("use_vol"):
        total += 1
        if latest["Volume"] >= 1.1 * latest["Vol_SMA20"]:
            passed += 1

    score = (passed / max(total, 1)) * 100
    return score, passed, total
