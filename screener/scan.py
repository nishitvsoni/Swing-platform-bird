"""
Scan orchestration: runs technical + fundamental scoring across the stock
universe in parallel and combines them into a final weighted score.
"""

import concurrent.futures

import pandas as pd
import yfinance as yf

from screener.data import SECTOR_MAP
from screener.fundamental import score_fundamental
from screener.technical import compute_technical_indicators, score_technical


def analyze_stock(ticker: str, sector_rsi_dict: dict, tech_checks: dict,
                   fund_thresholds: dict, tech_weight: int) -> tuple:
    """
    Fetch history + info for one ticker and return its scored row.
    Returns (row_dict_or_None, reason_str). reason_str is None on success,
    otherwise a short label explaining why the ticker was dropped - this is
    what lets the UI show *why* a scan came back empty instead of just "0
    results", which is otherwise impossible to debug.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6m")
        if df.empty:
            return None, "no price history returned (data source empty/blocked)"
        if len(df) < 50:
            return None, "less than 50 days of history"

        info = stock.info
        if not info:
            return None, "no fundamentals info returned (data source empty/blocked)"
        price = df["Close"].iloc[-1]

        df = compute_technical_indicators(df)
        latest = df.iloc[-1]

        sector_name = info.get("sector", "")
        sector_ticker = SECTOR_MAP.get(sector_name, "^NSEI")
        sec_rsi = sector_rsi_dict.get(sector_ticker, sector_rsi_dict.get("^NSEI", 50.0))

        tech_score, _, _ = score_technical(latest, sec_rsi, tech_checks)
        fund_score, _, _, extras = score_fundamental(
            info, price, latest["Turnover_20"], fund_thresholds
        )

        w_t = tech_weight / 100.0
        w_f = 1.0 - w_t
        final_score = round((tech_score * w_t) + (fund_score * w_f), 1)

        row = {
            "Symbol": ticker.replace(".NS", ""),
            "Price (₹)": round(price, 2),
            "Final Score (%)": final_score,
            "Tech Match (%)": round(tech_score, 1),
            "Fund Match (%)": round(fund_score, 1),
            "RSI (14)": round(latest["RSI"], 1),
            "Sector RSI": sec_rsi,
            "20D ROC (%)": round(latest["ROC20"], 2),
            "14D ATR (₹)": round(latest["ATR"], 2),
            "ADTV (₹ Cr)": extras["adtv_cr"],
            "Book Val (₹)": round(extras["book_val"], 2) if extras["book_val"] else "N/A",
            "P/B Ratio": extras["pb_ratio"] if extras["pb_ratio"] else "N/A",
            "D/E Ratio": round(extras["de_ratio"], 2) if extras["de_ratio"] is not None else "N/A",
            "Rev Growth (%)": round(extras["rev_growth"], 1),
        }
        return row, None
    except Exception as exc:
        return None, f"error: {type(exc).__name__}: {exc}"


def run_scan(scan_universe: list, sector_rsi_dict: dict, tech_checks: dict,
             fund_thresholds: dict, tech_weight: int, max_workers: int = 10,
             progress_callback=None) -> tuple:
    """
    Run analyze_stock across the universe in parallel.
    progress_callback(completed, total), if given, is called after each result.
    Returns (results_df, failure_reason_counts) so the caller can show why a
    scan returned fewer rows than expected instead of just an empty table.
    Default max_workers lowered from 30 to 10 - Yahoo Finance rate-limits/
    blocks bursts of parallel requests, especially from shared cloud IPs
    (e.g. Streamlit Community Cloud), which otherwise silently kills most
    or all of a scan.
    """
    results = []
    reason_counts: dict = {}
    completed = 0
    total_count = len(scan_universe)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures_map = {
            executor.submit(
                analyze_stock, sym, sector_rsi_dict, tech_checks, fund_thresholds, tech_weight
            ): sym
            for sym in scan_universe
        }
        for future in concurrent.futures.as_completed(futures_map):
            completed += 1
            row, reason = future.result()
            if row is not None:
                results.append(row)
            elif reason:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
            if progress_callback:
                progress_callback(completed, total_count)

    return pd.DataFrame(results), reason_counts
