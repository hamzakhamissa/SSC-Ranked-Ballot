from flask import Flask, request, redirect, url_for
from flask import Response
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path
import sys

# Ensure we can import the scorer from Backend/main.py
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent / "Backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Reuse the existing scorer
from main import read_ranked_csv, borda_scores, top_x


app = Flask(__name__)


def render_html(content: str) -> Response:
    html = f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ranked Ballot Calculator</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', Arial, sans-serif; margin: 2rem; }}
      .card {{ max-width: 720px; margin: 0 auto; padding: 1.5rem; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
      h1 {{ font-size: 1.5rem; margin: 0 0 1rem; }}
      form {{ display: grid; gap: 0.75rem; }}
      label {{ font-weight: 600; }}
      input[type="number"], input[type="file"] {{ padding: 0.6rem; border: 1px solid #d1d5db; border-radius: 8px; }}
      button {{ padding: 0.6rem 0.9rem; border-radius: 8px; border: 0; background: #111827; color: white; cursor: pointer; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
      th, td {{ border: 1px solid #e5e7eb; padding: 0.5rem; text-align: left; }}
      th {{ background: #f9fafb; }}
      .muted {{ color: #6b7280; font-size: 0.9rem; }}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Ranked Ballot Calculator</h1>
      {content}
    </div>
  </body>
</html>
"""
    return Response(html, mimetype="text/html")


@app.get("/")
def index() -> Response:
    content = """
<form action="/score" method="post" enctype="multipart/form-data">
  <div>
    <label for="csv">CSV file</label><br>
    <input type="file" id="csv" name="csv" accept=".csv" required>
  </div>
  <div>
    <label for="top">Top X to display</label><br>
    <input type="number" id="top" name="top" min="1" value="5" required>
  </div>
  <div>
    <button type="submit">Calculate</button>
  </div>
  <p class="muted">Detects Rank 1..N columns automatically (no fixed length required).</p>
  <p class="muted">Method: Borda (Rank 1 gets k points, Rank k gets 1 point).</p>
  </form>
"""
    return render_html(content)


@app.post("/score")
def score() -> Response:
    file = request.files.get("csv")
    if not file or file.filename == "":
        return redirect(url_for("index"))

    try:
        top_x_n = int(request.form.get("top", "5"))
        if top_x_n < 1:
            top_x_n = 5
    except Exception:
        top_x_n = 5

    filename = secure_filename(file.filename)
    with tempfile.NamedTemporaryFile(prefix="ranked_", suffix=Path(filename).suffix, delete=True) as tmp:
        file.save(tmp.name)
        path = Path(tmp.name)
        ballots = read_ranked_csv(path)
        scores = borda_scores(ballots)
        winners = top_x(scores, top_x_n)

    rows = "".join(
        f"<tr><td>{i+1}</td><td>{name}</td><td>{score}</td></tr>"
        for i, (name, score) in enumerate(winners)
    )
    content = f"""
<p><strong>Results</strong></p>
<p>Ballots: {len(ballots)} | Candidates: {len(scores)}</p>
<table>
  <thead>
    <tr><th>Rank</th><th>Candidate</th><th>Score</th></tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
  </table>
  <p><a href="/">Back</a></p>
"""
    return render_html(content)


if __name__ == "__main__":
    # Run the dev server
    app.run(host="0.0.0.0", port=5555, debug=True)


