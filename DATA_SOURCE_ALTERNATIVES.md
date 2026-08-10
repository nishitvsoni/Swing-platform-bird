# Alternative data sources for Indian stock data (close price + fundamentals)

Indian market data is more tightly controlled than US markets — NSE/BSE
don't publish a free public REST API themselves, so data flows through
either broker APIs or paid aggregators. Here's what's actually available,
ranked roughly by reliability-to-effort for your use case.

## 1. Broker APIs — best option if reliability matters

These come straight from an actual exchange-licensed source, so they
don't get blocked the way scraped sources do.

| Provider | Cost | Notes |
|---|---|---|
| **Zerodha Kite Connect** | ₹2,000/month | You've mentioned being open to a Zerodha account for your other trading project — this is the same API. Clean, well-documented, official. Good historical OHLC + live data. No fundamentals (P/B, D/E, revenue) built in though. |
| **Angel One SmartAPI** | Free | Needs an Angel One trading account, but the API access itself is free. Similar coverage to Kite. |
| **Upstox API** | Free | Same pattern — free API access with an Upstox account. |
| **ICICI Breeze API** | Free | Free for resident Indians with an ICICI Direct account; note SEBI now requires a static IP for API trading from April 2026, which affects live trading more than historical data pulls. |

**Trade-off:** all of these need you to open (or already have) a trading
account with that broker, and none of them include fundamental ratios —
you'd still need a second source for P/B, D/E, revenue growth.

## 2. NSE Bhavcopy — official, free, no account needed

NSE itself publishes a daily end-of-day CSV ("Bhavcopy") covering every
listed stock's OHLC data for that day. It's the same data source your
current screener's fallback already points at.

- **Pros:** official, free, no signup, one file covers the whole market
  for a day (way fewer requests than per-stock calls).
- **Cons:** only price/volume data — no fundamentals. You'd build up
  history by downloading each day's file over time, and still need a
  separate source for P/B, D/E, revenue growth.

## 3. Paid aggregator APIs — built for exactly this

| Provider | Notes |
|---|---|
| **TrueData / Global Datafeeds** | NSE-licensed data vendors used by many Indian fintech apps. Real-time + historical + fundamentals, but priced for production use (not free-tier friendly). |
| **DalalAI, IndianAPI.in** and similar aggregators | Package both technicals and fundamentals (P/B, financials, shareholding, corporate actions) into one API. Free tiers typically give EOD data, 1-2 years history, low rate limits — paid tiers run roughly ₹500-5,000/month depending on volume. |

**Trade-off:** costs money past a small free tier, but this is the
category actually designed to replace what you're trying to do with
yfinance — technical + fundamental data, for Indian equities, without
scraping-related blocks.

## 4. Alpha Vantage

Has some NSE coverage as part of its global free tier, but Indian stock
coverage and depth is noticeably weaker than its US coverage, and the free
tier's rate limit (a handful of calls/minute) makes a 2000+ stock scan
impractical without a paid plan.

## What I'd suggest for your case

Given you're already open to a Zerodha account for the other project:
**Kite Connect for prices/technicals** (reliable, ₹2,000/month, you may
already be heading this direction) **+ NSE Bhavcopy or a small paid
aggregator tier for fundamentals** (P/B, D/E, revenue growth) is the most
realistic combination if you want this to actually work in production.

If you'd rather stay free, **NSE Bhavcopy for technicals only**, with
fundamentals either dropped from the score entirely or added later once
you're ready to pay for a data source, is the practical free path.

Let me know which direction you want to go, and I'll rebuild the data
layer (`screener/data.py`) around whichever source you pick.
