#!/usr/bin/env python3
"""Step 5 accuracy test: send every frozen golden-set ticket through POST /tickets.

Tickets are sent one at a time in golden-set row order (no concurrency), so the
recorded latencies are also the warm single-request latencies used to check the
Step 4 latency predictions. Each request carries X-Request-ID=acc-<label>-<row>
so it can be matched to the service log.

Usage:
  python step5/scripts/accuracy_test.py --label qwen3-4b --model qwen3:4b-instruct-2507-q4_K_M
       [--base-url http://localhost:8000]

Outputs step5/results/<label>/accuracy/{predictions.csv, confusion_matrix.csv, summary.json, summary.md}.
A non-201 response (e.g. 502 for invalid model JSON) counts as an output-conformance
failure (R7) and as an incorrect classification (R5/R6).
Standard library only.
"""
import argparse
import csv
import json
import math
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "step5" / "data" / "golden_set.csv"
CATEGORIES = [
    "Credit reporting",
    "Debt collection",
    "Mortgage",
    "Credit card",
    "Bank account or service",
    "Consumer loan",
    "Money transfer or service",
]
INVALID = "(invalid/error)"


def percentile(sorted_values: list[float], p: float) -> float:
    rank = max(1, math.ceil(p / 100 * len(sorted_values)))
    return sorted_values[rank - 1]


def post_ticket(base_url: str, narrative: str, request_id: str) -> tuple[int, dict | None, float]:
    req = urllib.request.Request(
        base_url + "/tickets",
        data=json.dumps({"narrative": narrative}).encode(),
        method="POST",
        headers={"Content-Type": "application/json", "X-Request-ID": request_id},
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            body = json.load(resp)
            status = resp.status
    except urllib.error.HTTPError as exc:
        status, body = exc.code, None
    except (urllib.error.URLError, TimeoutError):
        status, body = 0, None
    return status, body, (time.perf_counter() - started) * 1000


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="short model label, e.g. qwen3-4b")
    ap.add_argument("--model", required=True, help="exact Ollama tag the service must report")
    ap.add_argument("--base-url", default="http://localhost:8000")
    args = ap.parse_args()

    out = ROOT / "step5" / "results" / args.label / "accuracy"
    if (out / "predictions.csv").exists():
        raise SystemExit(f"{out} already has results; move them aside to re-run.")
    out.mkdir(parents=True, exist_ok=True)

    with GOLDEN.open(encoding="utf-8", newline="") as f:
        golden = list(csv.DictReader(f))

    started_utc = datetime.now(timezone.utc).isoformat()
    records = []
    for i, g in enumerate(golden, 1):
        request_id = f"acc-{args.label}-{g['row']}"
        status, body, ms = post_ticket(args.base_url, g["narrative"], request_id)
        if body is not None and body.get("model") != args.model:
            raise SystemExit(f"Service is running {body.get('model')!r}, expected {args.model!r}. Stopping.")
        predicted = body["category"] if status == 201 and body else INVALID
        records.append(
            {
                "row": g["row"],
                "golden": g["label"],
                "predicted": predicted,
                "correct": predicted == g["label"],
                "http_status": status,
                "latency_ms": round(ms, 1),
                "request_id": request_id,
                "ticket_id": body["id"] if body else "",
            }
        )
        print(f"[{i:3}/{len(golden)}] row {g['row']} {status} {ms/1000:6.1f}s  {g['label']!r} -> {predicted!r}")

    with (out / "predictions.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]))
        w.writeheader()
        w.writerows(records)

    cols = CATEGORIES + [INVALID]
    matrix = Counter((r["golden"], r["predicted"]) for r in records)
    with (out / "confusion_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["golden \\ predicted"] + cols)
        for g in CATEGORIES:
            w.writerow([g] + [matrix[(g, p)] for p in cols])

    n = len(records)
    correct = sum(r["correct"] for r in records)
    conforming = sum(r["http_status"] == 201 for r in records)
    per_cat = {}
    for c in CATEGORIES:
        rs = [r for r in records if r["golden"] == c]
        k = sum(r["correct"] for r in rs)
        per_cat[c] = {"n": len(rs), "correct": k, "accuracy_pct": round(100 * k / len(rs), 1)}
    lat = sorted(r["latency_ms"] for r in records if r["http_status"] == 201)
    summary = {
        "label": args.label,
        "model": args.model,
        "base_url": args.base_url,
        "started_utc": started_utc,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "n": n,
        "correct": correct,
        "overall_accuracy_pct": round(100 * correct / n, 1),
        "output_conformance_pct": round(100 * conforming / n, 1),
        "per_category": per_cat,
        "single_request_latency_ms": {
            "n": len(lat),
            "mean": round(sum(lat) / len(lat), 1) if lat else None,
            "p50": percentile(lat, 50) if lat else None,
            "p95": percentile(lat, 95) if lat else None,
            "p99": percentile(lat, 99) if lat else None,
            "max": lat[-1] if lat else None,
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        f"# Accuracy: {args.model}",
        "",
        f"Overall: **{correct}/{n} = {summary['overall_accuracy_pct']}%** (R5 needs >= 136/160)  ",
        f"Output conformance: {conforming}/{n} = {summary['output_conformance_pct']}% (R7 needs >= 99.0%)  ",
        "Sequential single-request latency (ms): "
        + ", ".join(f"{k} {v}" for k, v in summary["single_request_latency_ms"].items()),
        "",
        "| Category | n | Correct | Accuracy | R6 (>= 70%) |",
        "|---|---:|---:|---:|---|",
    ]
    for c, v in per_cat.items():
        lines.append(f"| {c} | {v['n']} | {v['correct']} | {v['accuracy_pct']}% | {'pass' if v['accuracy_pct'] >= 70 else 'FAIL'} |")
    lines += ["", "## Confusion matrix (rows = golden, columns = predicted)", ""]
    short = ["CR", "DC", "Mtg", "CC", "Bank", "Loan", "MT", "Invalid"]
    lines.append("| golden \\ predicted | " + " | ".join(short) + " |")
    lines.append("|---" * (len(short) + 1) + "|")
    for g, s in zip(CATEGORIES, short):
        lines.append(f"| {s} | " + " | ".join(str(matrix[(g, p)]) for p in cols) + " |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
