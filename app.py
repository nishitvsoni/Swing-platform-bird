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
fund_thresholds = {
    "min_adtv": st.sidebar.number_input("Min Average Daily Turnover (₹ Crores)", value=1.0, step=0.5),
    "max_pb": st.sidebar.number_input("Max Price-to-Book (P/B) Ratio", value=6.0, step=0.5),
    "max_de": st.sidebar.number_input("Max Debt-to-Equity Ratio", value=1.2, step=0.1),
    "min_rev_growth": st.sidebar.number_input("Min YoY Revenue Growth (%)", value=0.0, step=1.0),
}

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

    res_df = run_scan(
        scan_universe, sector_rsi_dict, tech_checks, fund_thresholds, tech_weight,
        progress_callback=on_progress,
    )

    p_bar.empty()
    status_txt.empty()

    if not res_df.empty:
        filtered_df = res_df[res_df["Final Score (%)"] >= min_final_score].sort_values(
            by="Final Score (%)", ascending=False
        )
        st.success(
            f"Scan Finished! Found {len(filtered_df)} stocks matching score "
            f"criteria (≥ {min_final_score}%)."
        )
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("No stocks passed the required score threshold. Lower the sidebar minimum score slider.")
