#!/usr/bin/env python3
"""A2 speed-test workload (brief Step 4): fixed, ordered ticket list + three fixed warm-up tickets.

Usage (from the repo root): python assignment2/scripts/make_speed_workload.py

Source: step5/data/tickets_load.tsv, the 840 non-golden team-9 rows (9000-9839) that the A1 load
tests sent. Golden rows (9840-9999, i.e. the A2 test and tuning sets) are never used.

Writes:
  assignment2/workload/speed_tickets.tsv   row<TAB>body, 60 tickets in send order (JMeter tickets_file)
  assignment2/workload/warmup_tickets.tsv  row<TAB>body, the 3 warm-up tickets, same for every run

Selection, by word count over the 840 rows (deterministic, seed 3113):
  typical = between the 25th and 75th percentile; long = at or above the 90th percentile.
  Warm-up = the first 3 typical rows after the shuffle. Workload = the next 48 typical + 12 long rows,
  ordered so every 5th ticket (positions 5, 10, ...) is long: each ~30-ticket run sees 6 long tickets.
The script re-checks its own output and fails if anything is out of range, golden, or repeated.
"""
import csv
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "step5" / "data" / "tickets_load.tsv"
GOLDEN = [ROOT / "assignment2" / "data" / "test_set.csv", ROOT / "assignment2" / "data" / "tuning_set.csv"]
OUT = ROOT / "assignment2" / "workload"
SEED = 3113
N_WARMUP, N_TYPICAL, N_LONG, LONG_EVERY = 3, 48, 12, 5


def words(body: str) -> int:
    return len(json.loads(body)["narrative"].split())


def percentile(sorted_values: list[int], p: float) -> int:
    # Nearest-rank, as in scripts/ticket_lengths.py.
    return sorted_values[max(1, math.ceil(p / 100 * len(sorted_values))) - 1]


def main() -> int:
    # Checkouts may have CRLF (core.autocrlf); bodies are JSON-escaped, so splitlines() is safe.
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "row\tbody"
    rows = {}
    for line in lines[1:]:
        if line:
            row, body = line.split("\t", 1)
            rows[int(row)] = body
    assert len(rows) == 840 and min(rows) == 9000 and max(rows) == 9839

    golden = set()
    for path in GOLDEN:
        with path.open(encoding="utf-8", newline="") as f:
            golden |= {int(r["row"]) for r in csv.DictReader(f)}
    assert len(golden) == 160 and not golden & set(rows)

    length = {r: words(b) for r, b in rows.items()}
    s = sorted(length.values())
    p25, p75, p90 = percentile(s, 25), percentile(s, 75), percentile(s, 90)

    order = sorted(rows)
    random.Random(SEED).shuffle(order)
    typical = [r for r in order if p25 <= length[r] <= p75]
    long_ = [r for r in order if length[r] >= p90]

    warmup = typical[:N_WARMUP]
    typ, lng = iter(typical[N_WARMUP:N_WARMUP + N_TYPICAL]), iter(long_[:N_LONG])
    workload = [next(lng) if (i + 1) % LONG_EVERY == 0 else next(typ) for i in range(N_TYPICAL + N_LONG)]

    picked = warmup + workload
    assert len(set(picked)) == len(picked) == N_WARMUP + N_TYPICAL + N_LONG
    assert all(9000 <= r <= 9839 and r not in golden for r in picked)
    assert sum(length[r] >= p90 for r in workload) == N_LONG

    OUT.mkdir(parents=True, exist_ok=True)
    for name, chosen in (("speed_tickets.tsv", workload), ("warmup_tickets.tsv", warmup)):
        with (OUT / name).open("w", encoding="utf-8", newline="\n") as f:
            f.write("row\tbody\n")
            f.writelines(f"{r}\t{rows[r]}\n" for r in chosen)

    print(f"word percentiles over rows 9000-9839: p25={p25} p75={p75} p90={p90}")
    print("warm-up:", ", ".join(f"{r} ({length[r]}w)" for r in warmup))
    print("workload:", " ".join(f"{r}:{length[r]}" for r in workload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
