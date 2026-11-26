#!/usr/bin/env python3
"""A2 speed-test analysis (brief Step 4, "Report, per run"). Reads only committed files; no service needed.

  python assignment2/scripts/analyse_speed.py

For every assignment2/results/speed/<config>/run<N>/ that has both the load-generator files (results.jtl,
meta_loadgen.json) and the Lenovo files (api.log, stats_*.json, ollama_events_during_run.json):

Per run
  sent        JMeter POST /tickets samples (JMeter sends floor(rate x run length) arrivals)
  completed   samples with success=true (HTTP 201 within the 300 s response timeout)
  errored     samples that got an HTTP error response (e.g. 502) within the timeout
  unfinished  samples JMeter gave up on at its response timeout, or that never got a response
              ("Non HTTP response" / timeout). The service may still have finished them later; the
              service-side outcome of each is counted from the API log.
  p50         median JMeter `elapsed` of the completed samples (nearest-rank on sorted values)
  throughput  completed / (last completed sample's end - first sample's start), per second
  error rate  (errored + unfinished) / sent
  escalation  share of this run's JMeter requests whose `triage` line has escalated=true (cascade only),
              matched by X-Request-ID; warm-up tickets are excluded
  /stats      Lenovo's /stats delta (taken before the next run's warm-up) vs the service's 201s for this run's
              JMeter requests
Per configuration
  p50 mean, min, max and sample SD across the runs; p95 POOLED over the completed samples of all runs, with n.
  No p99 (the brief: sample too small).
Writes assignment2/results/speed/summary.md and runs.csv.
"""
import csv
import json
import math
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEED = ROOT / "assignment2" / "results" / "speed"
ORDER = ["llama", "qwen", "gemma", "cascadeA", "cascadeB", "cascadeA_lock", "cascadeB_lock"]
LOG = re.compile(r"request_id=(\S+) method=POST path=/tickets status=(\d+) duration_ms=([\d.]+)")
TRIAGE = re.compile(r"triage (\{.*\})")


def pct(values: list[float], p: float) -> float | None:
    if not values:
        return None
    s = sorted(values)
    return s[max(1, math.ceil(p / 100 * len(s))) - 1]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def analyse_run(d: Path) -> dict:
    jtl = [r for r in csv.DictReader(open(d / "results.jtl", encoding="utf-8", newline="")) if r["label"] == "POST /tickets"]
    other = sum(1 for r in csv.DictReader(open(d / "results.jtl", encoding="utf-8", newline="")) if r["label"] != "POST /tickets")
    log = (d / "api.log").read_text(encoding="utf-8", errors="replace")
    server = {m.group(1): (int(m.group(2)), float(m.group(3))) for m in LOG.finditer(log)}
    triage = {t["request_id"]: t for t in (json.loads(m.group(1)) for m in TRIAGE.finditer(log))}

    completed = [r for r in jtl if r["success"].lower() == "true"]
    errored = [r for r in jtl if r["success"].lower() != "true" and r["responseCode"].isdigit()]
    unfinished = [r for r in jtl if r["success"].lower() != "true" and not r["responseCode"].isdigit()]
    el = [int(r["elapsed"]) for r in completed]
    start = min(int(r["timeStamp"]) for r in jtl)
    end = max((int(r["timeStamp"]) + int(r["elapsed"]) for r in completed), default=start)
    ids = [r["reqid"] for r in jtl]
    tri = [triage[i] for i in ids if i in triage]
    lenovo_delta = read_json(d / "stats_after.json")["delta"] if (d / "stats_after.json").exists() else None
    events = read_json(d / "ollama_events_during_run.json") if (d / "ollama_events_during_run.json").exists() else {}
    return {
        "sent": len(jtl),
        "completed": len(completed),
        "errored": len(errored),
        "unfinished": len(unfinished),
        "unfinished_later_201_on_server": sum(1 for r in unfinished if server.get(r["reqid"], (0,))[0] == 201),
        "search_samples": other,
        "p50_s": round(pct(el, 50) / 1000, 2) if el else None,
        "max_completed_s": round(max(el) / 1000, 2) if el else None,
        "throughput_per_s": round(len(completed) / ((end - start) / 1000), 4) if completed and end > start else 0.0,
        "error_rate_pct": round(100 * (len(errored) + len(unfinished)) / len(jtl), 1) if jtl else None,
        "in_service_log": sum(1 for i in ids if i in server),
        "service_201": sum(1 for i in ids if server.get(i, (0,))[0] == 201),
        "lenovo_stats_delta": lenovo_delta,
        "escalated": sum(1 for t in tri if t.get("escalated")) if tri and tri[0].get("mode") == "cascade" else None,
        "triage_lines": len(tri),
        # Split of escalations: a Gemma call that hit the 300 s Ollama timeout is logged as "invalid" and escalated,
        # so it is not a decision of the rule.
        "esc_small_timeout": sum(1 for t in tri if t.get("reason") == "invalid" and (t.get("small_ms") or 0) >= 299_000),
        "esc_invalid_answer": sum(1 for t in tri if t.get("reason") == "invalid" and (t.get("small_ms") or 0) < 299_000),
        "esc_category": sum(1 for t in tri if t.get("reason") == "category"),
        "model_loads_during_run": events.get("model_loads"),
        "evictions_during_run": events.get("evictions"),
        "runner_killed_during_run": events.get("runner_killed"),
        "_elapsed_ms": el,
    }


def main() -> int:
    S = read_json(SPEED / "S.json")
    rows, lines = [], []
    lines += [
        "# A2 speed-test results (generated by assignment2/scripts/analyse_speed.py)",
        "",
        f"S = {S['S_s']} s (rows {', '.join(map(str, S['rows']))}: {', '.join(map(str, S['timings_s']))} s). "
        f"Rate: one ticket every {S['interval_s']} s ({S['rate_per_hour']}/h; A1 client peak 81/h, 105/h with headroom). "
        f"Run length {S['run_min']} min; JMeter response timeout {S['response_timeout_s']:.0f} s; drain pause {S['pause_min']} min.",
        "",
        "## Per run",
        "",
        "| Config | Run | Sent | Completed | Errored | Unfinished (later 201 on server) | p50 s | Max s | Throughput /s | Error % | Escalated | /stats Lenovo vs service 201 | Loads/evict/kill in run |",
        "|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|---|---|",
    ]
    summary = []
    for config in [c for c in ORDER if (SPEED / c).is_dir()]:
        runs = []
        for d in sorted((SPEED / config).glob("run[0-9]*")):
            if not ((d / "results.jtl").exists() and (d / "api.log").exists()):
                continue
            r = analyse_run(d)
            r["config"], r["run"] = config, d.name.removeprefix("run")
            runs.append(r)
            esc = (f"{r['escalated']}/{r['triage_lines']} ({r['esc_small_timeout']} Gemma timeouts, {r['esc_category']} category, {r['esc_invalid_answer']} invalid)"
                   if r["escalated"] is not None else "n/a")
            lines.append(
                f"| {config} | {r['run']} | {r['sent']} | {r['completed']} | {r['errored']} | {r['unfinished']} ({r['unfinished_later_201_on_server']}) | "
                f"{r['p50_s']} | {r['max_completed_s']} | {r['throughput_per_s']} | {r['error_rate_pct']} | {esc} | "
                f"{r['lenovo_stats_delta']} vs {r['service_201']} | {r['model_loads_during_run']}/{r['evictions_during_run']}/{r['runner_killed_during_run']} |"
            )
            rows.append({k: v for k, v in r.items() if not k.startswith("_")})
        if runs:
            p50s = [r["p50_s"] for r in runs if r["p50_s"] is not None]
            pooled = [ms for r in runs for ms in r["_elapsed_ms"]]
            sent = sum(r["sent"] for r in runs)
            esc = [r for r in runs if r["escalated"] is not None]
            summary.append(
                f"| {config} | {len(runs)} | {', '.join(f'{p:.1f}' for p in p50s)} | {statistics.mean(p50s):.1f} | "
                f"{min(p50s):.1f}-{max(p50s):.1f} | {statistics.stdev(p50s):.1f} | " if len(p50s) > 1 else f"| {config} | {len(runs)} | {p50s} | | | | "
            )
            summary[-1] += (
                f"{pct(pooled, 95) / 1000:.1f} (n = {len(pooled)} of {sent} sent) | "
                f"{sum(r['completed'] for r in runs)}/{sent} | "
                + (f"{sum(r['escalated'] for r in esc)}/{sum(r['triage_lines'] for r in esc)} ({100 * sum(r['escalated'] for r in esc) / sum(r['triage_lines'] for r in esc):.1f}%); "
                   f"excluding Gemma timeouts {sum(r['escalated'] - r['esc_small_timeout'] for r in esc)}/{sum(r['triage_lines'] - r['esc_small_timeout'] for r in esc)} |" if esc else "n/a |")
            )
    lines += [
        "",
        "## Per configuration (p50 from completed samples; p95 pooled over all completed samples of the runs)",
        "",
        "| Config | Runs | p50 per run (s) | p50 mean | p50 range | p50 SD | Pooled p95 s | Completed / sent | Escalated (service log) |",
        "|---|---:|---|---:|---|---:|---|---|---|",
        *summary,
        "",
        "Notes: completed = HTTP 201 within JMeter's 300 s timeout. Unfinished = JMeter gave up at 300 s; the number in",
        "brackets is how many of those the service still finished later with 201 (a cascade request can take up to",
        "600 s: a 300 s Ollama timeout for each model). p50/p95 use completed samples only, as the brief specifies, so",
        "they understate a configuration that times requests out; read them with the error rate.",
        "Escalated: from the service's triage lines for this run's JMeter requests. A Gemma call that hits the 300 s Ollama",
        "timeout is logged as an invalid answer and escalated, so 'excluding Gemma timeouts' is the rule's own escalation",
        "fraction, comparable with the accuracy test (85% A, 92.5% B).",
    ]
    (SPEED / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(SPEED / "runs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
