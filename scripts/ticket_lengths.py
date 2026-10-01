#!/usr/bin/env python3
"""Ticket-length distribution for the team's rows (workload model, Step 3).

Usage: python scripts/ticket_lengths.py [path/to/ict3113_tickets.csv]
Writes workload/ticket_lengths.json and workload/ticket_lengths_hist.csv.
"""
import csv
import json
import math
import sys
from pathlib import Path


TEAM = 9
FIRST_ROW, LAST_ROW = TEAM * 1000, TEAM * 1000 + 999
BIN_WORDS = 25
OUT_DIR = Path("workload")


def percentile(sorted_values: list[int], p: float) -> int:
    # Nearest-rank method: smallest value with at least p% of values at or below it.
    rank = max(1, math.ceil(p / 100 * len(sorted_values)))
    return sorted_values[rank - 1]


def summarise(values: list[int]) -> dict:
    s = sorted(values)
    return {
        "min": s[0],
        "mean": round(sum(s) / len(s), 1),
        "p50": percentile(s, 50),
        "p90": percentile(s, 90),
        "p95": percentile(s, 95),
        "p99": percentile(s, 99),
        "max": s[-1],
    }


def main() -> int:
    csv_path = Path(sys.argv[1] if len(sys.argv) > 1 else "documents/ict3113_tickets.csv")
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if FIRST_ROW <= int(r["row"]) <= LAST_ROW]
    assert len(rows) == 1000, f"expected 1000 rows, got {len(rows)}"

    words = [len(r["narrative"].split()) for r in rows]
    chars = [len(r["narrative"]) for r in rows]
    result = {
        "source": csv_path.as_posix(),
        "rows": f"{FIRST_ROW}-{LAST_ROW}",
        "count": len(rows),
        "words": summarise(words),
        "characters": summarise(chars),
        "tickets_at_max_words": words.count(max(words)),
    }

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "ticket_lengths.json").write_text(json.dumps(result, indent=2) + "\n")
    with (OUT_DIR / "ticket_lengths_hist.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["words_from", "words_to", "tickets"])
        for start in range(0, max(words) + 1, BIN_WORDS):
            end = start + BIN_WORDS - 1
            writer.writerow([start, end, sum(start <= w <= end for w in words)])

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
