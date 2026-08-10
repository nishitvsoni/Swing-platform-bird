# NSE Swing Trade Screener

A Streamlit screener for NSE-listed stocks, scored on technical criteria
pulled from NSE's own official daily **Bhavcopy** files.

## Why Bhavcopy instead of yfinance

The original version used `yfinance` (Yahoo Finance). Yahoo began
returning `YFRateLimitError: Too Many Requests` for every single request,
including single-stock tests run outside this app entirely - confirming a
hard block, not something request-throttling could fix. This version pulls
directly from NSE instead: one small official CSV per trading day, covering
every listed equity's OHLC + volume, downloaded once and cached.

**Trade-off:** NSE's Bhavcopy has no fundamental data (P/B, debt/equity,
revenue growth). Instead, the app lets you **upload your own fundamentals**
(CSV/Excel) via the sidebar - see `WHERE_TO_GET_EARNINGS_DATA.md` for where
to source that data and `fundamentals_template.csv` for the expected format.

## Features

- Price > 20 EMA > 50 EMA (trend)
- 20-day Rate of Change > 0% (momentum)
- Stock RSI > market median RSI (relative strength vs the scanned universe)
- Volume ≥ 1.1x 20-day average volume (volume surge)

Each stock gets a 0–100% technical match score; the sidebar sets which
checks are active and the minimum score to show in results.

## Project structure

```
stock-screener/
├── app.py                          # Streamlit UI
├── screener/
│   ├── data.py                     # NSE Bhavcopy download + caching
│   ├── technical.py                # indicator calculation + scoring
│   ├── fundamental.py              # scores against your uploaded fundamentals file
│   └── scan.py                     # scores the full universe from bulk history
├── requirements.txt
└── .gitignore
```

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploying for free (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. **New app** → pick this repo/branch, main file `app.py` → **Deploy**.

## Notes / known limitations

- First scan of a given day downloads N days of Bhavcopy files
  sequentially (a progress bar shows this) - each day is then cached for
  30 days, so later scans in the same session are fast.
- NSE occasionally changes its Bhavcopy URL format (it last changed in
  2024 to the current "UDiFF" format) - if downloads start failing, that's
  the first thing to check.
- Data is end-of-day only - no live intraday prices.
- Fundamentals are optional and user-supplied - upload a CSV/Excel via the
  sidebar (see `WHERE_TO_GET_EARNINGS_DATA.md`), or leave it out for a
  100% technical score.

## Possible next steps

- Add a real fundamentals source (see `DATA_SOURCE_ALTERNATIVES.md`)
- Add CSV export of scan results
- Persist downloaded Bhavcopy data to disk so it survives redeploys
