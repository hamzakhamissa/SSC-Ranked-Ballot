import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def read_ranked_csv(csv_path: Path) -> List[List[str]]:
    """
    Read a ranked-choice CSV where columns include Rank 1..Rank N.
    Returns a list of ballots, each ballot is an ordered list of candidate names.
    """
    ballots: List[List[str]] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Identify rank columns in order: Rank 1, Rank 2, ...
        rank_columns = [h for h in reader.fieldnames or [] if h.strip().lower().startswith("rank ")]
        # Sort by the numeric suffix
        def rank_index(h: str) -> int:
            try:
                return int(h.strip().split()[1])
            except Exception:
                return 10_000

        rank_columns.sort(key=rank_index)

        for row in reader:
            ranked_choices = []
            for col in rank_columns:
                name = (row.get(col) or "").strip()
                if name:
                    ranked_choices.append(name)
            if ranked_choices:
                ballots.append(ranked_choices)
    return ballots


def borda_scores(ballots: List[List[str]]) -> Dict[str, int]:
    """
    Compute Borda count: for each ballot with k candidates ranked,
    Rank 1 gets k points, Rank 2 gets k-1, ..., Rank k gets 1 point.
    """
    scores: Dict[str, int] = defaultdict(int)
    for ranked in ballots:
        k = len(ranked)
        for position, candidate in enumerate(ranked, start=1):
            scores[candidate] += (k - position + 1)
    return dict(scores)


def top_x(scores: Dict[str, int], x: int) -> List[Tuple[str, int]]:
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:x]


def main() -> None:
    parser = argparse.ArgumentParser(description="Ranked ballot calculator (Borda count)")
    parser.add_argument("csv_path", type=str, help="Path to the ranked CSV")
    parser.add_argument("--top", type=int, default=3, help="How many top candidates to display")
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    ballots = read_ranked_csv(csv_path)
    if not ballots:
        raise SystemExit("No ballots found in CSV (no Rank columns or empty rows)")

    scores = borda_scores(ballots)
    winners = top_x(scores, args.top)

    print("Total ballots:", len(ballots))
    print("Candidates scored:", len(scores))
    print()
    print(f"Top {args.top} (Borda):")
    for rank, (name, score) in enumerate(winners, start=1):
        print(f"{rank}. {name}: {score}")


if __name__ == "__main__":
    main()


