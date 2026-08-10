"""
Fundamental scoring - driven by a user-uploaded fundamentals file.

NSE Bhavcopy (the price/volume data source this project uses) has no
fundamentals. Instead of a paid API, this module scores against whatever
fundamentals data the user uploads themselves (e.g. exported from
Screener.in, or compiled from earnings releases/annual reports) - see
WHERE_TO_GET_EARNINGS_DATA.md for sourcing options.

Expected upload columns (case-insensitive, extra columns are ignored):
    Symbol, PB, DE, RevenueGrowth, EPSGrowth
- Symbol: NSE ticker, e.g. RELIANCE (no .NS suffix needed)
- PB: Price-to-Book ratio
- DE: Debt-to-Equity ratio
- RevenueGrowth: YoY revenue growth, in percent (e.g. 12.5, not 0.125)
- EPSGrowth: YoY EPS growth, in percent - optional, scored if present
Any column can be missing/blank for a given row; that check is just
skipped for that stock rather than failing it.
"""

import pandas as pd

EXPECTED_COLUMNS = ["Symbol", "PB", "DE", "RevenueGrowth", "EPSGrowth"]


def load_fundamentals_file(uploaded_file) -> dict:
    """
    Parse an uploaded CSV or Excel file into {symbol: {col: value}}.
    Column names are matched case-insensitively; a Symbol column is required.
    Returns an empty dict (not an error) if parsing fails, so the app can
    fall back to technical-only scoring instead of crashing.
    """
    try:
        if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
    except Exception:
        return {}

    # Normalise column names (strip spaces, match case-insensitively)
    col_map = {c: c.strip() for c in df.columns}
    df = df.rename(columns=col_map)
    lower_to_actual = {c.lower(): c for c in df.columns}

    symbol_col = lower_to_actual.get("symbol")
    if not symbol_col:
        return {}

    result = {}
    for _, row in df.iterrows():
        symbol = str(row[symbol_col]).strip().upper()
        if not symbol or symbol == "NAN":
            continue
        entry = {}
        for key in ["pb", "de", "revenuegrowth", "epsgrowth"]:
            actual_col = lower_to_actual.get(key)
            if actual_col is not None and pd.notna(row[actual_col]):
                entry[key] = float(row[actual_col])
        result[symbol] = entry
    return result


def score_fundamental(symbol: str, fundamentals_lookup: dict, thresholds: dict) -> tuple:
    """
    Score one symbol against uploaded fundamentals data, if present.
    fundamentals_lookup: output of load_fundamentals_file(), or {} if none uploaded.
    thresholds: dict with max_pb, max_de, min_rev_growth, min_eps_growth.

    Returns (fund_score_pct, passed_count, total_count, extras_dict).
    If the symbol has no uploaded data at all, returns a neutral 100% pass
    with 0 checks applied - it doesn't get penalized for missing data.
    """
    data = fundamentals_lookup.get(symbol.upper())
    if not data:
        return 100.0, 0, 0, {"pb": "N/A", "de": "N/A", "rev_growth": "N/A", "eps_growth": "N/A"}

    total, passed = 0, 0

    if "pb" in data:
        total += 1
        if data["pb"] <= thresholds.get("max_pb", float("inf")):
            passed += 1

    if "de" in data:
        total += 1
        if data["de"] <= thresholds.get("max_de", float("inf")):
            passed += 1

    if "revenuegrowth" in data:
        total += 1
        if data["revenuegrowth"] >= thresholds.get("min_rev_growth", float("-inf")):
            passed += 1

    if "epsgrowth" in data:
        total += 1
        if data["epsgrowth"] >= thresholds.get("min_eps_growth", float("-inf")):
            passed += 1

    score = (passed / max(total, 1)) * 100
    extras = {
        "pb": data.get("pb", "N/A"),
        "de": data.get("de", "N/A"),
        "rev_growth": data.get("revenuegrowth", "N/A"),
        "eps_growth": data.get("epsgrowth", "N/A"),
    }
    return score, passed, total, extras
