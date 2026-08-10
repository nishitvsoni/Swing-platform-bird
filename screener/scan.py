"""
Scan orchestration - computes technical scores for every symbol from a
single bulk price-history DataFrame (built from NSE Bhavcopy), instead of
making a network call per stock. This is the fix for Yahoo Finance
blocking/rate-limiting every individual request.
"""

import pandas as pd

from screener.fundamental import score_fundamental
from screener.technical import compute_technical_indicators, score_technical


def score_universe(history_df: pd.DataFrame, tech_checks: dict,
                    fund_thresholds: dict, tech_weight: int,
                    fundamentals_lookup: dict = None) -> tuple:
    """
    history_df: long DataFrame [Date, Symbol, Open, High, Low, Close, Volume]
    covering the full scan universe, from screener.data.build_price_history().

    fundamentals_lookup: output of screener.fundamental.load_fundamentals_file(),
    or None/{} if the user hasn't uploaded a fundamentals file - in that case
    every stock gets a neutral 100% fundamental pass (technical-only scoring).

    Returns (results_df, failure_reason_counts).
    """
    if history_df.empty:
        return pd.DataFrame(), {"no price history returned (data source empty/blocked)": 1}

    fundamentals_lookup = fundamentals_lookup or {}
    results = []
    reason_counts: dict = {}
    latest_rsis = []
    per_symbol_data = {}

    # Pass 1: compute technical indicators per symbol, collect latest RSI
    # for the market-relative-strength check.
    for symbol, group in history_df.groupby("Symbol"):
        group = group.sort_values("Date")
        if len(group) < 50:
            reason_counts["less than 50 days of history"] = (
                reason_counts.get("less than 50 days of history", 0) + 1
            )
            continue
        try:
            indicators = compute_technical_indicators(group)
            latest = indicators.iloc[-1]
            per_symbol_data[symbol] = (indicators, latest)
            if pd.notna(latest["RSI"]):
                latest_rsis.append(latest["RSI"])
        except Exception as exc:
            reason_counts[f"error: {type(exc).__name__}"] = (
                reason_counts.get(f"error: {type(exc).__name__}", 0) + 1
            )

    market_rsi = pd.Series(latest_rsis).median() if latest_rsis else 50.0

    # Pass 2: score each symbol now that market_rsi is known.
    for symbol, (indicators, latest) in per_symbol_data.items():
        try:
            tech_score, _, _ = score_technical(latest, market_rsi, tech_checks)
            fund_score, _, _, extras = score_fundamental(symbol, fundamentals_lookup, fund_thresholds)

            w_t = tech_weight / 100.0
            w_f = 1.0 - w_t
            final_score = round((tech_score * w_t) + (fund_score * w_f), 1)

            results.append({
                "Symbol": symbol,
                "Price (₹)": round(latest["Close"], 2),
                "Final Score (%)": final_score,
                "Tech Match (%)": round(tech_score, 1),
                "Fund Match (%)": round(fund_score, 1),
                "P/B": extras["pb"],
                "D/E": extras["de"],
                "Rev Growth (%)": extras["rev_growth"],
                "EPS Growth (%)": extras["eps_growth"],
                "RSI (14)": round(latest["RSI"], 1) if pd.notna(latest["RSI"]) else "N/A",
                "Market RSI": round(market_rsi, 1),
                "20D ROC (%)": round(latest["ROC20"], 2) if pd.notna(latest["ROC20"]) else "N/A",
                "14D ATR (₹)": round(latest["ATR"], 2) if pd.notna(latest["ATR"]) else "N/A",
                "Data as of": latest["Date"].strftime("%Y-%m-%d"),
            })
        except Exception as exc:
            reason_counts[f"error: {type(exc).__name__}"] = (
                reason_counts.get(f"error: {type(exc).__name__}", 0) + 1
            )

    return pd.DataFrame(results), reason_counts
