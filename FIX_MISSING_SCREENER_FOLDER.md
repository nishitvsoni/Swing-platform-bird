# Fixing your repo: move 5 files into a `screener` folder

From your screenshot, this is exactly the "missing folder" case: `data.py`,
`fundamental.py`, `scan.py`, `technical.py`, and `__init__.py` all landed
loose at the top level, instead of inside a `screener` folder next to
`app.py`. That's why Python can't find `screener.data`.

The fix on GitHub's website: **rename** each of those 5 files to include
`screener/` at the front of the filename. GitHub treats that as moving the
file into a folder (and creates the folder automatically).

## Do this for each of the 5 files

Repeat these steps once per file: `__init__.py`, `data.py`, `technical.py`,
`fundamental.py`, `scan.py`.

1. On your repo page, click the filename (e.g. `data.py`) to open it.
2. Click the **pencil icon** (Edit this file) near the top right of the
   file view.
3. At the top of the edit screen, there's a filename field showing just
   `data.py`. Click into it and change it to:
   ```
   screener/data.py
   ```
4. Scroll down, leave the commit message as-is (or type "move into
   screener folder"), make sure **"Commit directly to the main branch"**
   is selected, then click **Commit changes**.
5. Repeat for the other 4 files, changing the filename field to:
   - `screener/__init__.py`
   - `screener/technical.py`
   - `screener/fundamental.py`
   - `screener/scan.py`

## Check the result

After all 5 renames, refresh your repo's main page. You should now see:

```
app.py
screener/          ← new folder, click into it to confirm all 5 files are there
requirements.txt
README.md
.gitignore
```

Click into `screener/` and confirm it contains `__init__.py`, `data.py`,
`fundamental.py`, `scan.py`, `technical.py` — nothing more, nothing less.

## Redeploy

1. Go to your app on `share.streamlit.io`.
2. Click **Manage app** in the corner.
3. Click the **"⋮"** menu → **Reboot app** (it may also auto-redeploy on
   its own within a minute or two of the commits above).

It should load without the `ModuleNotFoundError` this time.

## If renaming one-by-one feels tedious

That's genuinely the only way to fix it through the GitHub website with no
command line — GitHub's browser upload can't create a folder and drop
existing files into it in one step. Five renames is a one-time fix; once
the folder exists, all future updates to those files can just be uploaded
normally into the `screener/` folder going forward.
