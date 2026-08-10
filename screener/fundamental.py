"""
Fundamental scoring: ADTV liquidity, Price/Book, Debt/Equity, revenue growth.
"""


def score_fundamental(info: dict, price: float, turnover_20: float, thresholds: dict) -> tuple:
    """
    Score a stock's fundamentals against the configured thresholds.

    thresholds: dict with min_adtv, max_pb, max_de, min_rev_growth
    Returns (fund_score_pct, passed_count, total_count, extras) where extras
    holds the raw computed values for display (adtv_cr, pb_ratio, de_ratio, rev_growth).
    """
    total, passed = 0, 0

    # Average Daily Traded Turnover, in ₹ Crores
    adtv_cr = round(turnover_20 / 1e7, 2)
    total += 1
    if adtv_cr >= thresholds["min_adtv"]:
        passed += 1

    # Price-to-Book ratio
    book_val = info.get("bookValue")
    if book_val and book_val > 0:
        pb_ratio = round(price / book_val, 2)
    else:
        pb_ratio = info.get("priceToBook")

    if pb_ratio is not None:
        total += 1
        if pb_ratio <= thresholds["max_pb"]:
            passed += 1

    # Debt-to-Equity (yfinance sometimes reports this as a percentage)
    de_ratio = info.get("debtToEquity")
    if de_ratio is not None:
        de_ratio = de_ratio / 100.0 if de_ratio > 10 else de_ratio
        total += 1
        if de_ratio <= thresholds["max_de"]:
            passed += 1

    # YoY revenue growth
    rev_growth = (info.get("revenueGrowth", 0) or 0) * 100
    total += 1
    if rev_growth >= thresholds["min_rev_growth"]:
        passed += 1

    score = (passed / max(total, 1)) * 100
    extras = {
        "adtv_cr": adtv_cr,
        "book_val": book_val,
        "pb_ratio": pb_ratio,
        "de_ratio": de_ratio,
        "rev_growth": rev_growth,
    }
    return score, passed, total, extras
