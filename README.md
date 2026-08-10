# NSE/BSE Swing Trade Screener

A Streamlit screener for NSE-listed stocks that combines **technical** and
**fundamental** checks into a single weighted score.

## Features

**Technical checks**
- Price > 20 EMA > 50 EMA (trend)
- 20-day Rate of Change > 0% (momentum)
- Stock RSI > sector RSI (relative strength vs its sector index)
- Volume ≥ 1.1x 20-day average volume (volume surge)

**Fundamental checks**
- Average Daily Traded Turnover (₹ Cr) above a minimum liquidity bar
- Price-to-Book ratio below a maximum
- Debt-to-Equity ratio below a maximum
- YoY revenue growth above a minimum

Each side produces a 0–100% match score; the sidebar lets you set the
technical/fundamental weighting (default 60/40) and a minimum final-score
cutoff for the results table.

## Project structure

```
stock-screener/
├── app.py                  # Streamlit UI - sidebar controls, run button, results table
├── screener/
│   ├── data.py             # NSE symbol universe + sector RSI fetching (cached)
│   ├── technical.py        # technical indicator calculation + scoring
│   ├── fundamental.py      # fundamental ratio scoring
│   └── scan.py             # per-stock analysis worker + parallel scan runner
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

The app opens at `http://localhost:8501`.

## Deploying for free (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, pick this repo/branch, set the main file to `app.py`.
4. Deploy. Every push to the branch auto-redeploys.

No secrets/API keys are required for the current technical + fundamental
version — data comes from Yahoo Finance (`yfinance`) and the NSE symbol list.

## Notes / known limitations

- `yfinance` and the NSE symbol CSV are free but unofficial sources; NSE
  occasionally rate-limits or changes its CSV endpoint, in which case the
  screener falls back to a Nifty 500 mirror list, then a small hardcoded list.
- Scanning "All NSE Listed Equities" (~2000+ stocks) is slow on Streamlit
  Community Cloud's shared CPU — Nifty 500 is the practical default.
- Sector RSI values are cached for 1 hour, symbol lists for 24 hours, to
  keep repeated scans fast.

## Possible next steps

- Add unit tests for `screener/technical.py` and `screener/fundamental.py`
- Add CSV export of scan results
- Re-introduce AI-generated commentary/scoring as an optional module later
