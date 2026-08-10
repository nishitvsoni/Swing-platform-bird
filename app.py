import pandas as pd
import streamlit as st

from screener.data import build_price_history, symbols_from_history
from screener.fundamental import load_fundamentals_file
from screener.scan import score_universe

st.set_page_config(page_title="NSE Swing Screener Pro", layout="wide")

st.title("⚡ NSE Swing Trade Screener")
st.caption(
    "Technical scoring from NSE's official daily Bhavcopy data, optionally "
    "blended with fundamentals you upload yourself."
)

# ---------------------------------------------------------
# Sidebar Settings
# ---------------------------------------------------------
st.sidebar.header("⚙️ Screener Controls")

lookback_days = st.sidebar.slider(
    "Price history to download (trading days)", min_value=60, max_value=200,
    value=130, step=10,
    help="More days = more accurate 50-day EMA etc., but a slower first scan. "
         "Once downloaded, each day is cached for 30 days.",
)

max_symbols = st.sidebar.slider(
    "Max stocks to include (from the downloaded universe)",
    min_value=50, max_value=2000, value=500, step=50,
)

st.sidebar.subheader("📤 Fundamentals (optional)")
fundamentals_file = st.sidebar.file_uploader(
    "Upload your fundamentals data (CSV or Excel)",
    type=["csv", "xlsx", "xls"],
    help="Columns: Symbol, PB, DE, RevenueGrowth, EPSGrowth. "
         "See WHERE_TO_GET_EARNINGS_DATA.md for a template and sourcing tips.",
)
fundamentals_lookup = {}
if fundamentals_file is not None:
    fundamentals_lookup = load_fundamentals_file(fundamentals_file)
    if fundamentals_lookup:
        st.sidebar.success(f"Loaded fundamentals for {len(fundamentals_lookup)} symbols.")
    else:
        st.sidebar.error("Couldn't read that file - check it has a 'Symbol' column.")

st.sidebar.subheader("⚖️ Scoring Weightage")
if fundamentals_lookup:
    tech_weight = st.sidebar.slider("Technical Weight (%)", min_value=0, max_value=100, value=60, step=5)
    st.sidebar.caption(f"Split: Technicals ({tech_weight}%) | Fundamentals ({100 - tech_weight}%)")
else:
    tech_weight = 100
    st.sidebar.caption("No fundamentals uploaded - score is 100% technical.")

min_final_score = st.sidebar.slider(
    "Minimum Score Threshold (%)", min_value=0, max_value=100, value=50, step=5
)

st.sidebar.subheader("📈 Technical Parameters")
tech_checks = {
    "use_ema": st.sidebar.checkbox("Price > 20 EMA > 50 EMA", value=True),
    "use_roc": st.sidebar.checkbox("20-Day ROC > 0% (Positive Momentum)", value=True),
    "use_market_rsi": st.sidebar.checkbox("Stock RSI > Market Median RSI", value=True),
    "use_vol": st.sidebar.checkbox("Volume > 1.1x 20-Day SMA Volume", value=True),
}

st.sidebar.subheader("📊 Fundamental Thresholds")
fund_thresholds = {
    "max_pb": st.sidebar.number_input("Max Price-to-Book (P/B)", value=6.0, step=0.5),
    "max_de": st.sidebar.number_input("Max Debt-to-Equity", value=1.2, step=0.1),
    "min_rev_growth": st.sidebar.number_input("Min YoY Revenue Growth (%)", value=0.0, step=1.0),
    "min_eps_growth": st.sidebar.number_input("Min YoY EPS Growth (%)", value=0.0, step=1.0),
}

# ---------------------------------------------------------
# Execution Flow
# ---------------------------------------------------------
st.markdown(
    f"Will download **{lookback_days} trading days** of Bhavcopy data, "
    f"then score up to **{max_symbols} stocks** from it."
)

if st.button("🚀 Run Swing Screener"):
    st.info("Downloading NSE Bhavcopy files... this is a one-time cost per day (cached after).")

    p_bar = st.progress(0)
    status_txt = st.empty()

    def on_progress(completed, total):
        p_bar.progress(completed / total)
        status_txt.text(f"Downloaded {completed}/{total} trading days...")

    history_df = build_price_history(num_days=lookback_days, progress_callback=on_progress)
    p_bar.empty()
    status_txt.empty()

    if history_df.empty:
        st.error(
            "0 trading days returned data. NSE's archive server may be "
            "temporarily unreachable, or the URL format has changed since "
            "this was built - see TROUBLESHOOT_MODULE_ERROR.md / try again "
            "in a few minutes."
        )
    else:
        all_symbols = symbols_from_history(history_df)
        keep_symbols = set(all_symbols[:max_symbols])
        scoped_df = history_df[history_df["Symbol"].isin(keep_symbols)]

        st.info(f"Scoring {len(keep_symbols)} stocks from {len(history_df):,} rows of price data...")
        res_df, failure_reasons = score_universe(
            scoped_df, tech_checks, fund_thresholds, tech_weight, fundamentals_lookup
        )

        n_scored = len(res_df)
        n_failed = sum(failure_reasons.values())

        if not res_df.empty:
            filtered_df = res_df[res_df["Final Score (%)"] >= min_final_score].sort_values(
                by="Final Score (%)", ascending=False
            )
            st.success(
                f"Scan Finished! {n_scored} stocks scored. "
                f"{len(filtered_df)} matched score criteria (≥ {min_final_score}%)."
            )
            if len(filtered_df) == 0:
                st.info("Try lowering the minimum score threshold in the sidebar.")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.error(f"0 out of {len(keep_symbols)} stocks could be scored.")

        if failure_reasons:
            with st.expander(f"⚠️ Why {n_failed} stocks were skipped (click to view)"):
                reason_df = pd.DataFrame(
                    sorted(failure_reasons.items(), key=lambda x: -x[1]),
                    columns=["Reason", "Count"],
                )
                st.dataframe(reason_df, use_container_width=True)
