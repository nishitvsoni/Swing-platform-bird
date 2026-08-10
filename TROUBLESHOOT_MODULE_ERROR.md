# Fixing "ModuleNotFoundError: screener" on Streamlit Cloud

This error means Streamlit Cloud can't find the `screener` folder next to
`app.py` in your GitHub repo. This almost always means the folder
structure went in wrong during the upload — most commonly, the `screener`
folder ended up nested one level too deep, or didn't upload at all.

## Step 1: Check what's actually in your GitHub repo

1. Go to your repository on GitHub (looks like it's called
   `swing-platform-bird` based on the error path).
2. Look at the file list on the main page.

**You should see, all at the same top level:**
```
app.py
screener/
requirements.txt
README.md
.gitignore
```

**Common wrong versions to look for:**

- **Nested folder** — you see a folder called `stock-screener` (or similar)
  and *inside that* is another copy of `app.py` and `screener/`. This
  happens when you dragged the outer unzipped folder in, instead of just
  its contents.
- **Missing `screener` folder entirely** — you only see `app.py` and a
  few other files, no `screener` folder at all. This happens if the drag
  only picked up loose files and skipped the subfolder.
- **`screener` folder present but empty** — GitHub's upload UI sometimes
  drops the files inside a subfolder if you didn't drag it in one motion.

## Step 2: Fix it based on what you find

### If everything is nested one level too deep

1. Go into the nested folder on GitHub (click into `stock-screener/` if
   that's what's shown).
2. Select all the files inside it the same way as before (open it, note
   what's there).
3. You'll need to re-upload correctly: click **Add file → Upload files**
   at the **top level** of the repo (not inside the nested folder), then
   drag in the *contents* of the nested folder — `app.py`, the `screener`
   folder, `requirements.txt`, etc. — directly.
4. Commit that.
5. Then delete the now-duplicate nested folder: click into it on GitHub,
   there's a trash/delete option per file, or delete the whole folder via
   the file view (**"..."** menu → **Delete directory**, or delete each
   file then the empty folder disappears).
6. Commit the deletion.

### If the `screener` folder is missing or empty

1. On your computer, open the unzipped `stock-screener` folder again.
2. Open the `screener` subfolder — confirm you see 5 files inside:
   `__init__.py`, `data.py`, `technical.py`, `fundamental.py`, `scan.py`.
3. On GitHub, click **Add file → Create new folder**, or more reliably:
   click **Add file → Upload files**, then drag the **`screener` folder
   itself** into the upload box this time (dragging a folder in is
   usually more reliable than dragging its loose contents for this step).
4. GitHub should show `screener/__init__.py`, `screener/data.py`, etc. in
   the upload preview before you commit — check that before clicking
   **Commit changes**.

## Step 3: Confirm the fix

After committing, refresh your GitHub repo's main page. Click into the
`screener` folder — you should see all 5 `.py` files listed there,
sitting directly next to `app.py` at the top level (not nested further).

## Step 4: Redeploy

Streamlit Cloud usually auto-redeploys within a minute or two of any
commit. If it doesn't:

1. Go to your app on `share.streamlit.io`.
2. Click **Manage app** (bottom right, as the error message mentioned).
3. Click the **"⋮"** menu → **Reboot app**.

Watch the logs there — if it still fails, the log will show the exact
missing file, which tells you exactly what's still out of place.

## If you'd rather avoid this folder juggling entirely

An easier alternative for a small project like this: GitHub also lets you
create a **new repository directly from a zip-like structure** using
**GitHub Desktop** (a free app, no command-line typing) — you point it at
your local `stock-screener` folder and it publishes the whole thing,
preserving the structure exactly, in one click. Let me know if you'd like
that walkthrough instead.
