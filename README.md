# FITS Radial Intensity Profile

A Streamlit web app for extracting a radial intensity profile from a FITS
image along a chosen position angle, starting from the brightest pixel.

## Files

- `line_profile.py` — the `make_line` function (your original logic, with
  the two `plt.show()` calls replaced by capturing and returning the
  `Figure` objects, since Streamlit needs the figure objects to render them
  — see the docstring at the top of the file for exactly what changed).
- `app.py` — the Streamlit UI that uploads a FITS file, collects inputs
  (angle, xlim, ylim, wcs flags), calls `make_line`, and displays the two
  plots plus a downloadable CSV of the profile data.
- `requirements.txt` — dependencies.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: FITS radial profile Streamlit app"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   GitHub.
2. Click **New app**, pick your repo/branch, and set the main file path to
   `app.py`.
3. Click **Deploy**. Streamlit Cloud will install `requirements.txt`
   automatically and give you a public URL.

## Notes / known limitations (from the original function)

- `wcs_xlim` / `wcs_ylim` are accepted but not currently used to compute
  actual WCS-based limits in the underlying function — passing them just
  sets `xlim`/`ylim` to `'unknown'`. This is inherited from your original
  code and left unchanged.
- The angle-to-gradient math assumes a roughly square, non-WCS-projected
  pixel grid.
- Uploaded FITS files are written to a temporary file on disk (and deleted
  after processing) because `make_line` requires a string file path.
