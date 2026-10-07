#!/usr/bin/env python3
"""Step 5 load/stress analysis. Standard library only.

Reads step5/results/<model>/<level>/run<N>/{results.jtl, meta.json, console.log, stats_*.json}
and evidence/step5/logs/api-*.log, then writes:
  step5/results/runs.csv          one row per run x endpoint (measurement window only)
  step5/results/levels.csv        mean / min / max / sd across the three runs
  step5/results/reconciliation.csv  every run: JTL samples vs service log lines vs /stats delta
  step5/results/<model>/<stress level>/run1/timeline.csv  per-minute stress timeline
  step5/results/summary.md

Definitions (identical for every model and level):
  window      = [t0 + warm-up, t0 + warm-up + measure), t0 = JMeter test start.
                Samples are assigned to the window by their START time; warm-up and
                drain-period arrivals are excluded.
  p50/p95/p99 = nearest-rank percentiles of JMeter `elapsed` over ALL samples in the
                window, failures included (a timed-out request counts at its timeout).
  error rate  = failed samples / samples in the window (JMeter success=false:
                non-201/200 status, timeout, connection error).
  offered/h   = samples started in the window per hour.
  achieved/h  = successful samples that COMPLETED inside the window per hour.
  in-flight   = POSTs started before the window end that had not completed by it
                (backlog indicator for R1).

Usage: python step5/scripts/analyse_jtl.py [results_dir] [service_log_dir]
"""
import csv
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "step5" / "results"
LOGS = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "evidence" / "step5" / "logs"
LOG_RE = re.compile(r"request_id=(\S+) method=(\S+) path=(\S+) status=(\d+) duration_ms=([\d.]+)")
START_RE = re.compile(r"Starting standalone test @ .*\((\d{13})\)")
LABELS = ["POST /tickets", "GET /search"]
LEVEL_ORDER = ["offpeak", "average", "peak", "headroom", "burst", "surge"]


def pct(values: list[float], p: float) -> float | None:
    if not values:
        return None
    s = sorted(values)
    return s[max(1, math.ceil(p / 100 * len(s))) - 1]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_service_log() -> dict[str, tuple[str, int, float]]:
    """request_id -> (path, status, duration_ms) from every saved API log (deduplicated)."""
    seen = {}
    for f in sorted(LOGS.glob("api-*.log")):
        for line in f.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = LOG_RE.search(line)
            if m:
                seen[m.group(1)] = (m.group(3), int(m.group(4)), float(m.group(5)))
    return seen


def load_run(run_dir: Path):
    meta = read_json(run_dir / "meta.json")
    with (run_dir / "results.jtl").open(encoding="utf-8", newline="") as f:
        samples = [
            {
                "start": int(r["timeStamp"]),
                "elapsed": int(r["elapsed"]),
                "label": r["label"],
                "code": r["responseCode"],
                "ok": r["success"].lower() == "true",
                "reqid": r.get("reqid", ""),
            }
            for r in csv.DictReader(f)
            if r["label"] in LABELS
        ]
    t0 = None
    console = run_dir / "console.log"
    if console.exists():
        m = START_RE.search(console.read_text(encoding="utf-8-sig", errors="replace"))
        if m:
            t0 = int(m.group(1))
    if t0 is None:  # fallback: earliest arrival (slightly late, never early)
        t0 = min(s["start"] for s in samples)
    return meta, samples, t0


def window_metrics(samples, w_start, w_end) -> dict:
    hours = (w_end - w_start) / 3_600_000
    out = {}
    for label in LABELS:
        own = [s for s in samples if s["label"] == label]
        inw = [s for s in own if w_start <= s["start"] < w_end]
        el = [s["elapsed"] for s in inw]
        fails = sum(not s["ok"] for s in inw)
        done = [s for s in own if s["ok"] and w_start <= s["start"] + s["elapsed"] < w_end]
        in_flight = sum(1 for s in own if s["start"] < w_end <= s["start"] + s["elapsed"])
        out[label] = {
            "n": len(inw),
            "errors": fails,
            "error_pct": round(100 * fails / len(inw), 2) if inw else None,
            "p50_ms": pct(el, 50),
            "p95_ms": pct(el, 95),
            "p99_ms": pct(el, 99),
            "max_ms": max(el) if el else None,
            "mean_ms": round(statistics.mean(el), 1) if el else None,
            "offered_per_h": round(len(inw) / hours, 1),
            "achieved_per_h": round(len(done) / hours, 1),
            "in_flight_at_end": in_flight,
        }
    return out


def timeline(samples, t0, bucket_ms=60_000) -> list[dict]:
    buckets = defaultdict(lambda: {"arrived": 0, "completed_ok": 0, "errors": 0, "lat": []})
    for s in samples:
        if s["label"] != "POST /tickets":
            continue
        b = buckets[(s["start"] - t0) // bucket_ms]
        b["arrived"] += 1
        b["lat"].append(s["elapsed"])
        b["errors"] += not s["ok"]
        if s["ok"]:
            buckets[(s["start"] + s["elapsed"] - t0) // bucket_ms]["completed_ok"] += 1
    rows, backlog = [], 0
    for k in range(0, max(buckets) + 1 if buckets else 0):
        b = buckets[k]
        backlog += b["arrived"] - b["completed_ok"] - b["errors"]
        rows.append(
            {
                "minute": k,
                "post_arrivals": b["arrived"],
                "post_completed_ok": b["completed_ok"],
                "post_errors_by_arrival": b["errors"],
                "approx_backlog": backlog,
                "p50_latency_s_by_arrival": round(pct(b["lat"], 50) / 1000, 1) if b["lat"] else "",
                "max_latency_s_by_arrival": round(max(b["lat"]) / 1000, 1) if b["lat"] else "",
            }
        )
    return rows


def fmt(v, scale=1.0, nd=1):
    return "–" if v is None else f"{v / scale:.{nd}f}"


def main() -> int:
    service_log = load_service_log()
    run_rows, recon_rows = [], []
    for jtl in sorted(RESULTS.glob("*/*/run*/results.jtl")):
        run_dir = jtl.parent
        meta, samples, t0 = load_run(run_dir)
        model, level = run_dir.parts[-3], run_dir.parts[-2]
        w_start = t0 + int(meta["warmup_min"] * 60_000)
        w_end = w_start + int(meta["measure_min"] * 60_000)
        for label, m in window_metrics(samples, w_start, w_end).items():
            run_rows.append({"model": model, "level": level, "run": meta["run"], "endpoint": label, **m})

        if level.startswith("stress"):
            rows = timeline(samples, t0)
            with (run_dir / "timeline.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)

        # Reconciliation: every JTL sample should have exactly one service log line.
        matched = [service_log.get(s["reqid"]) for s in samples]
        n_logged = sum(m is not None for m in matched)
        status_mismatch = sum(
            1 for s, m in zip(samples, matched) if m is not None and str(m[1]) != s["code"]
        )
        ok_posts = sum(1 for s in samples if s["label"] == "POST /tickets" and s["ok"])
        stats_delta = None
        if (run_dir / "stats_before.json").exists() and (run_dir / "stats_after.json").exists():
            stats_delta = read_json(run_dir / "stats_after.json")["total"] - read_json(run_dir / "stats_before.json")["total"]
        recon_rows.append(
            {
                "model": model, "level": level, "run": meta["run"],
                "jtl_samples": len(samples),
                "found_in_service_log": n_logged,
                "missing_from_log": len(samples) - n_logged,
                "status_mismatches": status_mismatch,
                "jtl_successful_posts": ok_posts,
                "stats_total_delta": stats_delta,
                "stats_reconciles": stats_delta == ok_posts if stats_delta is not None else None,
            }
        )

    if not run_rows:
        print("No results.jtl files found under step5/results")
        return 1

    def write_csv(path, rows):
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    write_csv(RESULTS / "runs.csv", run_rows)
    write_csv(RESULTS / "reconciliation.csv", recon_rows)

    groups = defaultdict(list)
    for r in run_rows:
        groups[(r["model"], r["level"], r["endpoint"])].append(r)
    level_rows = []
    metrics = ["p50_ms", "p95_ms", "p99_ms", "achieved_per_h", "offered_per_h", "error_pct", "in_flight_at_end"]
    for (model, level, ep), rs in sorted(
        groups.items(), key=lambda kv: (kv[0][0], LEVEL_ORDER.index(kv[0][1]) if kv[0][1] in LEVEL_ORDER else 99, kv[0][2])
    ):
        row = {"model": model, "level": level, "endpoint": ep, "runs": len(rs), "samples": sum(r["n"] for r in rs)}
        for m in metrics:
            vals = [r[m] for r in rs if r[m] is not None]
            row[f"{m}_mean"] = round(statistics.mean(vals), 1) if vals else None
            row[f"{m}_min"] = min(vals) if vals else None
            row[f"{m}_max"] = max(vals) if vals else None
            row[f"{m}_sd"] = round(statistics.stdev(vals), 1) if len(vals) > 1 else None
        level_rows.append(row)
    write_csv(RESULTS / "levels.csv", level_rows)

    lines = [
        "# Step 5 load test summary (generated by step5/scripts/analyse_jtl.py)",
        "",
        "Latency in seconds: mean across runs [min–max]. Window excludes warm-up and drain.",
        "",
        "| Model | Level | Endpoint | Runs | p50 s | p95 s | p99 s | Achieved /h | Offered /h | Error % | In-flight at end |",
        "|---|---|---|---:|---|---|---|---|---|---|---|",
    ]
    for r in level_rows:
        def cell(m, scale=1.0, nd=1):
            return f"{fmt(r[m + '_mean'], scale, nd)} [{fmt(r[m + '_min'], scale, nd)}–{fmt(r[m + '_max'], scale, nd)}]"
        lines.append(
            f"| {r['model']} | {r['level']} | {r['endpoint']} | {r['runs']} | {cell('p50_ms', 1000, 2)} | "
            f"{cell('p95_ms', 1000, 2)} | {cell('p99_ms', 1000, 2)} | {cell('achieved_per_h')} | "
            f"{cell('offered_per_h')} | {cell('error_pct', 1, 2)} | {cell('in_flight_at_end', 1, 0)} |"
        )
    lines += ["", "## Reconciliation (JMeter .jtl vs service log vs /stats)", "",
              "| Model | Level | Run | JTL samples | In service log | Status mismatches | Successful POSTs | /stats delta | OK |",
              "|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in recon_rows:
        lines.append(
            f"| {r['model']} | {r['level']} | {r['run']} | {r['jtl_samples']} | {r['found_in_service_log']} | "
            f"{r['status_mismatches']} | {r['jtl_successful_posts']} | {r['stats_total_delta']} | {r['stats_reconciles']} |"
        )
    (RESULTS / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
