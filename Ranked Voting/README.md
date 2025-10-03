# Ranked Voting

Backend + simple web UI for Borda-count scoring of ranked ballots.

## Run locally

```bash
python3 -m venv "./venv"
"./venv/bin/pip" install -r "Backend/requirements.txt"
"./venv/bin/python" "Frontend/app.py"
```

Open `http://localhost:5555`.

## CLI usage

```bash
"./venv/bin/python" "Backend/main.py" "Backend/First year rep (Hamza) - Form Responses 1.csv" --top 5
```

## GitHub Pages

A static page is in `docs/` that can call your API (configure URL inside `docs/index.html`).

Enable GitHub Pages to serve from `docs` folder in repo settings.

## Notes
- CSV must have `Rank 1..N` columns. Other columns are ignored.
- Borda scoring: Rank 1 gets k points, Rank k gets 1 point.
