"""
Run this by itself (not through Streamlit) to see the EXACT error yfinance
is hitting, separated by call type. This tells us whether it's the price
history call, the .info call, or both - which points to a different fix
for each.

Usage:
    pip install --upgrade yfinance
    python diagnose_yfinance.py
"""

import sys

import yfinance as yf

print(f"yfinance version: {yf.__version__}\n")

TEST_TICKERS = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

for ticker in TEST_TICKERS:
    print(f"--- {ticker} ---")
    stock = yf.Ticker(ticker)

    # Test 1: price history
    try:
        df = stock.history(period="1mo")
        if df.empty:
            print("  history(): returned EMPTY dataframe (no exception)")
        else:
            print(f"  history(): OK - {len(df)} rows, latest close = {df['Close'].iloc[-1]:.2f}")
    except Exception as exc:
        print(f"  history(): FAILED - {type(exc).__name__}: {exc}")

    # Test 2: .info (this is the one that needs a Yahoo "crumb" and breaks most often)
    try:
        info = stock.info
        if not info:
            print("  .info: returned EMPTY dict (no exception)")
        else:
            print(f"  .info: OK - sector={info.get('sector')}, bookValue={info.get('bookValue')}")
    except Exception as exc:
        print(f"  .info: FAILED - {type(exc).__name__}: {exc}")

    print()

print(
    "If history() works but .info fails for all tickers, the fundamental-data "
    "side is broken (a known, ongoing Yahoo Finance issue with the .info "
    "endpoint's crumb/cookie requirement) while technical data is fine.\n"
    "If BOTH fail for all tickers, either your network is blocking Yahoo "
    "entirely, or yfinance needs upgrading: pip install --upgrade yfinance"
)
