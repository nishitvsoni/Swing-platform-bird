# You made the repo — now what? (No command line needed)

You already have an empty repository on GitHub. Here's the easiest way to
get your files into it, entirely through your web browser — no `git`
commands required.

## Step 1: Open your repository on GitHub

Go to `github.com`, log in, and click on the repository you created
(e.g. `stock-screener`). You'll land on a mostly-empty page with a button
that says **"uploading an existing file"** or similar, and a
**"Add file"** button near the top right.

## Step 2: Unzip the folder on your computer

Find `stock-screener.zip` wherever you downloaded it (usually your
**Downloads** folder). Double-click it to unzip — this creates a regular
folder called `stock-screener` with everything inside it.

Open that folder so you can see its contents: `app.py`, a folder called
`screener`, `requirements.txt`, `README.md`, and a couple more files.

## Step 3: Upload the files through the browser

Back on the GitHub repository page:

1. Click **Add file** → **Upload files**.
2. Open the unzipped `stock-screener` folder on your computer in a second
   window (File Explorer on Windows, Finder on Mac).
3. Select everything **inside** that folder — not the folder itself:
   - Click one file, then press **Ctrl+A** (Windows) or **Cmd+A** (Mac) to
     select all of them, including the `screener` folder.
4. **Drag** all the selected items into the GitHub upload box in your
   browser (the area that says "Drag files here to add them to your
   repository").
5. Wait for the upload bar(s) to finish — for a project this size it
   should take a few seconds.

## Step 4: Commit the upload

Scroll down on that same page. You'll see a box labeled **"Commit
changes"** with a text field pre-filled with something like "Add files via
upload."

1. Leave that message as-is, or change it to something like
   `Initial upload`.
2. Make sure **"Commit directly to the main branch"** is selected.
3. Click the green **Commit changes** button.

That's it — refresh the repository page and you should see all your files
listed there (`app.py`, `screener/`, `README.md`, etc).

## Step 5: (Optional) Make the app live on the internet

This step turns your code into an actual working website you (or anyone)
can open in a browser.

1. Go to **share.streamlit.io** in a new tab.
2. Click **Sign in** and choose **Continue with GitHub** — approve access
   when it asks.
3. Click **Create app** (or **New app**).
4. Choose **"From existing repo"**.
5. Fill in:
   - **Repository**: your `stock-screener` repo (pick it from the dropdown)
   - **Branch**: `main`
   - **Main file path**: `app.py`
6. Click **Deploy**.

Streamlit will take a minute or two to set everything up. When it's
done, you'll have a working link like `something.streamlit.app` — open
it and your screener runs right there, no installation needed.

## Step 6: Using the screener once it's open

1. On the left, pick **Nifty 500** as your stock universe (faster than
   scanning all NSE stocks).
2. Leave the sliders and checkboxes at their defaults for your first run,
   or adjust them if you already know what you want to change.
3. Click the **🚀 Run Swing Screener** button.
4. Wait for the progress bar to finish — it's scanning each stock.
5. A table of results appears, sorted by score. Click any column heading
   to re-sort by that instead.

## If you need to update the code later

If I give you new/changed files:

1. Go back to your repository on GitHub.
2. Click **Add file** → **Upload files** again.
3. Drag in the new versions of whichever files changed.
4. Scroll down, click **Commit changes** again.
5. If the app is already deployed on Streamlit, it will automatically
   update itself within a minute or two — you don't need to redo Step 5.

## Common confusion points

- **"Do I select the stock-screener folder itself, or what's inside it?"**
  What's *inside* it. If you drag the outer `stock-screener` folder in,
  GitHub will create a nested `stock-screener/stock-screener/...`
  structure, which breaks the deploy step. Always upload the *contents*.
- **"It says some files were skipped."** GitHub's browser upload doesn't
  always handle empty folders well — as long as `app.py` and the
  `screener` folder (with `.py` files inside) show up, you're fine.
- **"Where's the .gitignore file, did it not upload?"** Files starting
  with a dot are hidden by default in Finder/File Explorer. It's still
  there — you can turn on "show hidden files" if you want to check.
