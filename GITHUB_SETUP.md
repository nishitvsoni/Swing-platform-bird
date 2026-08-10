# Getting `stock-screener` onto GitHub — full walkthrough

This covers everything from your downloaded zip file to actually using the
live screener, step by step.

## 0. Check you have git installed

Open a terminal (Terminal on Mac, PowerShell/Git Bash on Windows) and run:

```bash
git --version
```

- If it prints a version number, skip to Step 1.
- If it says "command not found":
  - **Windows**: install [Git for Windows](https://git-scm.com/download/win),
    then reopen your terminal (use "Git Bash" afterwards).
  - **Mac**: run `xcode-select --install`, or install via
    [git-scm.com](https://git-scm.com/download/mac).
  - **Linux**: `sudo apt install git` (Debian/Ubuntu) or your distro's
    package manager.

If you don't already have a GitHub account, create one free at
[github.com/join](https://github.com/join) before continuing.

## 1. Unzip and open a terminal there

Unzip `stock-screener.zip` wherever you keep projects (e.g. your home
folder or Documents), then `cd` into it:

```bash
cd path/to/stock-screener
```

Confirm you're in the right place:

```bash
ls
```

You should see `app.py`, `screener/`, `requirements.txt`, `README.md`, etc.

## 2. Create the repo on GitHub

Go to [github.com/new](https://github.com/new):
- Repository name: `stock-screener` (or whatever you like)
- Visibility: Public or Private, your choice
- **Do not** check "Add a README" — you already have one, and an extra one
  will conflict when you push
- Click **Create repository**

GitHub will show you a repo URL like:
`https://github.com/<your-username>/stock-screener.git`

## 3. Initialize git locally and push

From inside the `stock-screener` folder:

```bash
git init
git add .
git commit -m "Initial commit: technical + fundamental swing screener"
git branch -M main
git remote add origin https://github.com/<your-username>/stock-screener.git
git push -u origin main
```

If this is your first time pushing from this machine, GitHub will ask you
to authenticate. GitHub no longer accepts your account password for this —
you need a **Personal Access Token** instead:

1. On GitHub, click your profile photo → **Settings** → **Developer settings**
   (bottom of left sidebar) → **Personal access tokens** → **Tokens (classic)**.
2. **Generate new token (classic)** → give it a name, set an expiration,
   check the **repo** scope box → **Generate token**.
3. Copy the token (you only see it once).
4. When `git push` prompts for a username/password, enter your GitHub
   username, then paste the token as the password.

(Some setups instead open a browser window to log in automatically — if
that happens, just approve it there.)

## 4. Verify it worked

Go back to `https://github.com/<your-username>/stock-screener` in your
browser and refresh. You should see all your files listed — `app.py`,
`screener/`, `README.md`, etc. If they're there, the repo is live.

## 5. (Optional but recommended) Deploy it live for free

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   your GitHub account (authorize Streamlit to access your repos when asked).
2. Click **New app** (or **Create app**).
3. Choose **"From existing repo"**, then pick:
   - Repository: `<your-username>/stock-screener`
   - Branch: `main`
   - Main file path: `app.py`
4. Click **Deploy**.

The first deploy takes a minute or two while it installs everything from
`requirements.txt`. When it's done you'll land on your live app at a URL
like `your-app-name.streamlit.app` — bookmark that, it's your screener from
now on, reachable from any browser or phone.

## 6. Using the screener itself

Once the app loads (locally at `localhost:8501`, or at your `.streamlit.app`
URL):

1. In the left sidebar, choose your **Stock Universe** — Nifty 500 is the
   faster, practical default; "All NSE Listed" is slower.
2. Adjust the **Technical Weight** slider if you want technicals to count
   for more/less than fundamentals in the final score.
3. Set the **Minimum Total Score Threshold** — only stocks scoring at or
   above this show up in results.
4. Tick/untick individual technical checks (EMA trend, ROC, sector RSI,
   volume surge) and set fundamental thresholds (ADTV, P/B, D/E, revenue
   growth) to match what you're looking for.
5. Click **🚀 Run Swing Screener** and wait — a progress bar tracks
   how many stocks have been scanned.
6. Results appear as a sortable table, ranked by Final Score — click any
   column header to re-sort.

Nothing here requires an API key or paid data source; it all runs on free
Yahoo Finance data via `yfinance`.

## 7. Making future changes

Whenever you edit the code (locally, or ask me for changes and re-download
the zip):

```bash
git add .
git commit -m "describe what changed"
git push
```

That's the whole loop — no need to re-create the repo each time.

## Common snags

- **"remote origin already exists"** — you already ran `git remote add`
  once; use `git remote set-url origin <url>` instead, or just skip that
  line next time.
- **Push rejected (non-fast-forward)** — someone/something changed the
  GitHub repo since your last pull. Run `git pull origin main --rebase`
  then push again.
- **Large files rejected** — GitHub blocks files over 100MB; this project
  has none, so this only matters if you add big datasets later.
