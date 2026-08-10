"""
Data access layer - NSE official Bhavcopy (end-of-day CSV) instead of yfinance.

Yahoo Finance was rate-limiting/blocking this app entirely (confirmed via
YFRateLimitError), so this pulls directly from NSE's own daily Bhavcopy
files instead: one small file per trading day, covering every listed
equity's OHLC + volume. No fundamentals are available from this source -
this is a technical-data-only replacement.
"""

import datetime
import io
import zipfile

import pandas as pd
import requests
import streamlit as st

BHAVCOPY_URL_TEMPLATE = (
    "https://nsearchives.nseindia.com/content/cm/"
    "BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"
)

# A realistic browser-like session is required - NSE rejects bare requests
# without cookies/headers that look like a real browser visit.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def _get_nse_session() -> requests.Session:
    """NSE requires cookies from a homepage visit before archive downloads work."""
    session = requests.Session()
    session.headers.update(_HEADERS)
    try:
        session.get("https://www.nseindia.com", timeout=10)
    except Exception:
        pass  # proceed anyway - some environments still succeed without this
    return session


@st.cache_data(ttl=30 * 24 * 3600, show_spinner=False)
def _download_one_bhavcopy(date_str: str) -> pd.DataFrame:
    """
    Download and parse one day's Bhavcopy. date_str is 'YYYYMMDD'.
    Returns an empty DataFrame on holidays/weekends/failures (cached too,
    so we don't re-hit a known-empty date repeatedly).
    Cached for 30 days - a past trading day's data never changes.
    """
    url = BHAVCOPY_URL_TEMPLATE.format(date_str=date_str)
    session = _get_nse_session()
    try:
        res = session.get(url, timeout=15)
        if res.status_code != 200 or len(res.content) < 100:
            return pd.DataFrame()
        with zipfile.ZipFile(io.BytesIO(res.content)) as zf:
            csv_name = zf.namelist()[0]
            with zf.open(csv_name) as f:
                df = pd.read_csv(f)
        # Keep only equity series (drop ETFs/other instrument types if present)
        df = df[(df["Sgmt"] == "CM") & (df["SctySrs"] == "EQ")].copy()
        df = df[["TradDt", "TckrSymb", "OpnPric", "HghPric", "LwPric", "ClsPric", "TtlTradgVol"]]
        df.columns = ["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"]
        return df
    except Exception:
        return pd.DataFrame()


def trading_dates_back(n_days: int) -> list:
    """Last n_days calendar days that are Mon-Fri (approximate trading days;
    actual market holidays are simply skipped when their Bhavcopy comes back empty)."""
    dates = []
    d = datetime.date.today()
    while len(dates) < n_days:
        d -= datetime.timedelta(days=1)
        if d.weekday() < 5:  # Mon-Fri
            dates.append(d)
    return dates


def build_price_history(num_days: int = 130, progress_callback=None) -> pd.DataFrame:
    """
    Download and combine the last num_days of Bhavcopy into one long
    DataFrame: columns [Date, Symbol, Open, High, Low, Close, Volume].
    progress_callback(completed, total) is called after each day, if given.
    """
    dates = trading_dates_back(num_days)
    frames = []
    for i, d in enumerate(dates):
        date_str = d.strftime("%Y%m%d")
        day_df = _download_one_bhavcopy(date_str)
        if not day_df.empty:
            frames.append(day_df)
        if progress_callback:
            progress_callback(i + 1, len(dates))
    if not frames:
        return pd.DataFrame(columns=["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    combined = pd.concat(frames, ignore_index=True)
    combined["Date"] = pd.to_datetime(combined["Date"])
    combined = combined.sort_values(["Symbol", "Date"])
    return combined


def symbols_from_history(history_df: pd.DataFrame, limit: int = None) -> list:
    """Distinct symbols present in a price-history DataFrame, most-recent-day first."""
    if history_df.empty:
        return []
    symbols = sorted(history_df["Symbol"].dropna().unique().tolist())
    return symbols[:limit] if limit else symbols
