# Where to get earnings/fundamentals data for the upload feature

The screener now accepts a fundamentals file you upload yourself (sidebar
→ "Fundamentals (optional)"). Here's where to actually get that data.

## Upload format

CSV or Excel, one row per stock:

```
Symbol,PB,DE,RevenueGrowth,EPSGrowth
RELIANCE,2.1,0.35,8.2,6.5
TCS,11.4,0.08,10.1,9.0
```

- **Symbol** — NSE ticker, no `.NS` needed (e.g. `RELIANCE`, not `RELIANCE.NS`)
- **PB** — Price-to-Book ratio
- **DE** — Debt-to-Equity ratio
- **RevenueGrowth** / **EPSGrowth** — YoY %, as a plain number (`8.2` for 8.2%, not `0.082`)

Any column can be left blank per row — that check just gets skipped for
that stock rather than penalizing it. A ready-to-fill template is attached
(`fundamentals_template.csv`).

## Where to source this if you're compiling it yourself

**Official, primary sources (most reliable, most manual work):**

- **NSE Corporate Filings** — nseindia.com → Companies → Corporate Filings
  → Financial Results. Every listed company's quarterly/annual results
  (P&L, balance sheet) as filed with the exchange, in PDF.
- **BSE Corporate Announcements** — bseindia.com → Corporates → Corporate
  Announcements / Financial Results. Same idea, BSE's version.
- **Company investor relations pages** — most listed companies publish
  their quarterly earnings press release + investor presentation directly
  on their own website (usually under "Investors" or "IR" in the footer).
  These often have the cleanest, most digestible numbers.
- **Annual reports** — filed with NSE/BSE and posted on company IR pages;
  best source for full-year revenue growth and detailed balance sheet
  figures (for D/E, book value).

**Aggregator sites (faster, pre-compiled, still free for basic use):**

- **Screener.in** — the most popular free source for exactly this kind of
  data among Indian retail investors. Has a per-stock export button and,
  for registered users, a "create a screen" export to CSV covering many
  stocks' ratios at once — this maps almost directly onto the upload
  format above.
- **Moneycontrol / Trendlyne** — company-level fundamental ratios (P/B,
  D/E, growth figures) viewable for free, though bulk export usually needs
  a paid plan.
- **Tijori Finance** — good for company-level detail and historical
  trends, free tier available.

## Practical suggestion

If you already have a batch of earnings releases (PDFs) sitting somewhere,
the fastest path is: pull P/B, D/E, revenue growth, and EPS growth for
each company into a spreadsheet as you review them, save as CSV in the
format above, and upload it directly — no need to standardize on one
external source. Screener.in's export is the quickest way to bulk-fill
this for stocks you haven't already reviewed manually.

If you'd like, share a sample of the earnings release format you have on
hand (or a Screener.in export) and I can adjust `load_fundamentals_file()`
in `screener/fundamental.py` to parse your exact format directly, instead
of requiring the reformatted template above.
