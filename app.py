import pandas as pd
import streamlit as st

from screener.data import fetch_all_nse_symbols, fetch_sector_rsis
from screener.scan import run_scan

# ---------------------------------------------------------
# Streamlit UI Setup
# ---------------------------------------------------------
st.set_page_config(page_title="NSE/BSE Swing Screener Pro", layout="wide")

st.title("⚡ NSE/BSE Swing Trade Screener")
st.caption(
    "Technical + fundamental scoring: 20-Day ROC, Sector Relative RSI, "
    "14-Day ATR, ADTV Turnover (₹ Cr), and Price-to-Book."
)

with st.expander("🔍 Diagnose data connection (click if scans return 0 stocks)"):
    st.caption(
        "Tests a handful of stocks directly and shows the exact error Yahoo "
        "Finance is returning - this pinpoints the real cause instead of a "
        "generic 'skipped' count."
    )
    if st.button("Run connection test"):
        import yfinance as yf
        st.write(f"yfinance version: `{yf.__version__}`")
        for test_ticker in ["RELIANCE.NS", "TCS.NS", "INFY.NS"]:
            st.markdown(f"**{test_ticker}**")
            stock = yf.Ticker(test_ticker)

            try:
                df = stock.history(period="1mo")
                if df.empty:
                    st.warning("history(): returned EMPTY (no exception raised)")
                else:
                    st.success(f"history(): OK - {len(df)} rows, latest close {df['Close'].iloc[-1]:.2f}")
            except Exception as exc:
                st.error(f"history(): FAILED - {type(exc).__name__}: {exc}")

            try:
                info = stock.info
                if not info:
                    st.warning(".info: returned EMPTY dict (no exception raised)")
                else:
                    st.success(f".info: OK - sector={info.get('sector')}, bookValue={info.get('bookValue')}")
            except Exception as exc:
                st.error(f".info: FAILED - {type(exc).__name__}: {exc}")
        st.info(
            "Copy/paste everything above back into the chat - the exact "
            "error text (not just 'FAILED') is what pinpoints the real fix."
        )

# ---------------------------------------------------------
# Sidebar Settings
# ---------------------------------------------------------
st.sidebar.header("⚙️ Screener Controls")

universe_choice = st.sidebar.radio(
    "Stock Universe",
    options=["Nifty 500 (~500 Stocks)", "All NSE Listed Equities (~2000+ Stocks)"],
)

st.sidebar.subheader("⚖️ Scoring Weightage")
tech_weight = st.sidebar.slider("Technical Weight (%)", min_value=0, max_value=100, value=60, step=5)
fund_weight = 100 - tech_weight
st.sidebar.caption(f"Split: Technicals ({tech_weight}%) | Fundamentals ({fund_weight}%)")

min_final_score = st.sidebar.slider(
    "Minimum Total Score Threshold (%)", min_value=30, max_value=100, value=60, step=5
)

st.sidebar.subheader("📈 Technical Parameters")
tech_checks = {
    "use_ema": st.sidebar.checkbox("Price > 20 EMA > 50 EMA", value=True),
    "use_roc": st.sidebar.checkbox("20-Day ROC > 0% (Positive Momentum)", value=True),
    "use_sector_rsi": st.sidebar.checkbox("Stock RSI > Sector RSI (Sector Outperformer)", value=True),
    "use_vol": st.sidebar.checkbox("Volume > 1.1x 20-Day SMA Volume", value=True),
}

st.sidebar.subheader("📊 Fundamental Parameters")
use_fundamentals = st.sidebar.checkbox(
    "Apply fundamental filters", value=True,
    help="Turn off to test technical checks in isolation - fundamentals "
         "still get computed and shown, but won't drag the final score down.",
)
if use_fundamentals:
    fund_thresholds = {
        "min_adtv": st.sidebar.number_input("Min Average Daily Turnover (₹ Crores)", value=1.0, step=0.5),
        "max_pb": st.sidebar.number_input("Max Price-to-Book (P/B) Ratio", value=6.0, step=0.5),
        "max_de": st.sidebar.number_input("Max Debt-to-Equity Ratio", value=1.2, step=0.1),
        "min_rev_growth": st.sidebar.number_input("Min YoY Revenue Growth (%)", value=0.0, step=1.0),
    }
else:
    # Effectively unfiltered - every fundamental check passes automatically
    fund_thresholds = {
        "min_adtv": 0.0, "max_pb": float("inf"),
        "max_de": float("inf"), "min_rev_growth": float("-inf"),
    }
    tech_weight = 100
    st.sidebar.caption("Fundamentals disabled - score is 100% technical.")

# Cached sector RSIs (refreshed hourly)
sector_rsi_dict = fetch_sector_rsis()

# ---------------------------------------------------------
# Execution Flow
# ---------------------------------------------------------
all_symbols = fetch_all_nse_symbols()
scan_universe = all_symbols[:500] if "Nifty 500" in universe_choice else all_symbols

st.markdown(f"**Target Stock Universe:** `{len(scan_universe)} Stocks`")

if st.button("🚀 Run Swing Screener"):
    st.info(f"Scanning {len(scan_universe)} stocks in parallel... Please wait.")

    p_bar = st.progress(0)
    status_txt = st.empty()

    def on_progress(completed, total):
        p_bar.progress(completed / total)
        status_txt.text(f"Processed {completed}/{total} stocks...")

    res_df, failure_reasons = run_scan(
        scan_universe, sector_rsi_dict, tech_checks, fund_thresholds, tech_weight,
        progress_callback=on_progress,
    )

    p_bar.empty()
    status_txt.empty()

    n_fetched = len(res_df)
    n_failed = sum(failure_reasons.values())

    if not res_df.empty:
        filtered_df = res_df[res_df["Final Score (%)"] >= min_final_score].sort_values(
            by="Final Score (%)", ascending=False
        )
        st.success(
            f"Scan Finished! {n_fetched} stocks had usable data. "
            f"{len(filtered_df)} matched score criteria (≥ {min_final_score}%)."
        )
        if len(filtered_df) == 0:
            st.info(
                "Data came through fine, but none scored high enough. "
                "Try lowering the minimum score threshold in the sidebar."
            )
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.error(
            f"0 out of {len(scan_universe)} stocks returned usable data - "
            "this is a data-fetch problem, not a filter/threshold problem."
        )

    if failure_reasons:
        with st.expander(f"⚠️ Why {n_failed} stocks were skipped (click to view)"):
            reason_df = pd.DataFrame(
                sorted(failure_reasons.items(), key=lambda x: -x[1]),
                columns=["Reason", "Count"],
            )
            st.dataframe(reason_df, use_container_width=True)
            st.markdown(
                "If most reasons say **'no price history returned'** or "
                "**'no fundamentals info returned'**, Yahoo Finance is "
                "rate-limiting or blocking requests from this server "
                "(common on shared cloud hosting, including Streamlit "
                "Community Cloud) - this is not caused by your sidebar "
                "settings. Try again in a few minutes, or run the scan "
                "with a smaller stock universe."
            )
