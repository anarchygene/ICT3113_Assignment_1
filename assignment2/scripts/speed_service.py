#!/usr/bin/env python3
"""A2 speed tests, SERVICE PC (Lenovo) side. Brief Step 4 "Set-up" and "Each run".

  python assignment2/scripts/speed_service.py measure-s
      Sets the arrival rate. Llama alone: restart Ollama, 3 fixed warm-up tickets (discarded), then
      three DIFFERENT typical-length tickets (rows 9094, 9108, 9246: 137 words each, the median of
      rows 9000-9839, in neither the workload nor the warm-up list), one at a time. S = middle time.
      Writes assignment2/results/speed/S.json and S.md with S, rate, run length, timeout and pause.

  python assignment2/scripts/speed_service.py run <config> <run>
      config: llama | qwen | gemma | cascadeA | cascadeB (STEP2.md §6), or cascadeA_lock | cascadeB_lock
      (post-freeze: same settings with CASCADE_SERIALIZE=true). For each run:
        1. set .env for the config, recreate the api container, save the env dump;
        2. restart Ollama (clears its prompt cache; no model loaded) and wait until it is up;
        3. send the 3 fixed warm-up tickets through POST /tickets, one at a time (timings discarded);
        4. cascade only: run cascade_warmup.py, which must print READY;
        5. save `ollama ps`, call GET /stats (before), print READY and wait for ENTER;
      -> start the JMeter run on the load-generator PC; press ENTER here once JMeter has finished ->
        6. GET /stats (after); save the API and Ollama logs; count model loads, evictions and runner
           kills in the Ollama log after READY (there should be none).
      Output: assignment2/results/speed/<config>/run<N>/

Standard library only. Run from the repository root on the Lenovo.
"""
import json
import re
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assignment2" / "results" / "speed"
BASE = "http://localhost:8000"
LLAMA, QWEN, GEMMA = "llama3.1:8b-instruct-q4_K_M", "qwen3:4b-instruct-2507-q4_K_M", "gemma3:1b-it-q4_K_M"
ESC_A = "Credit reporting,Credit card,Bank account or service,Consumer loan,Money transfer or service"
CONFIGS = {  # .env values per configuration (STEP2.md §6)
    "llama": {"CASCADE_ENABLED": "false", "OLLAMA_MODEL": LLAMA},
    "qwen": {"CASCADE_ENABLED": "false", "OLLAMA_MODEL": QWEN},
    "gemma": {"CASCADE_ENABLED": "false", "OLLAMA_MODEL": GEMMA},
    "cascadeA": {"CASCADE_ENABLED": "true", "CASCADE_SMALL_MODEL": GEMMA, "CASCADE_LARGE_MODEL": LLAMA, "CASCADE_ESCALATE_ON": ESC_A, "CASCADE_SERIALIZE": "false"},
    "cascadeB": {"CASCADE_ENABLED": "true", "CASCADE_SMALL_MODEL": GEMMA, "CASCADE_LARGE_MODEL": LLAMA, "CASCADE_ESCALATE_ON": ESC_A + ",Debt collection", "CASCADE_SERIALIZE": "false"},
}
# Post-freeze variant (26 Nov): same rule and settings, but at most one Ollama call at a time (CASCADE_SERIALIZE).
CONFIGS["cascadeA_lock"] = CONFIGS["cascadeA"] | {"CASCADE_SERIALIZE": "true"}
CONFIGS["cascadeB_lock"] = CONFIGS["cascadeB"] | {"CASCADE_SERIALIZE": "true"}
S_ROWS = [9094, 9108, 9246]


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sh(*args: str, stdin: Path | None = None, check: bool = True) -> str:
    data = stdin.read_text(encoding="utf-8") if stdin else None
    p = subprocess.run(list(args), cwd=ROOT, input=data, stdin=None if data is not None else subprocess.DEVNULL,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        raise SystemExit(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}\n{p.stderr}")
    return p.stdout + p.stderr


def http(method: str, path: str, body: dict | None = None, rid: str | None = None, timeout: float = 900) -> tuple[int, dict, float]:
    headers = {"Content-Type": "application/json"} | ({"X-Request-ID": rid} if rid else {})
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body else None, method=method, headers=headers)
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.load(r), time.perf_counter() - t
    except urllib.error.HTTPError as e:
        return e.code, {}, time.perf_counter() - t


def wait_up() -> None:
    for _ in range(150):
        try:
            if http("GET", "/health", timeout=5)[0] == 200 and "NAME" in sh("docker", "compose", "exec", "-T", "ollama", "ollama", "list", check=False):
                return
        except Exception:
            pass
        time.sleep(2)
    raise SystemExit("service or Ollama did not come up")


def set_config(config: str) -> str:
    env = (ROOT / ".env").read_text(encoding="utf-8").splitlines()
    for key, value in CONFIGS[config].items():
        if not any(line.startswith(f"{key}=") for line in env):
            env.append(f"{key}={value}")
        env = [f"{key}={value}" if line.startswith(f"{key}=") else line for line in env]
    (ROOT / ".env").write_text("\n".join(env) + "\n", encoding="utf-8")
    sh("docker", "compose", "up", "-d", "--force-recreate", "api")
    wait_up()
    dump = sh("docker", "compose", "exec", "-T", "api", "env")
    dump = "\n".join(sorted(l for l in dump.splitlines() if re.match(r"(OLLAMA_MODEL|CASCADE_)", l)))
    for key, value in CONFIGS[config].items():
        if f"{key}={value}" not in dump.splitlines():
            raise SystemExit(f"api container did not pick up {key}={value}:\n{dump}")
    return dump


def restart_ollama() -> None:
    sh("docker", "compose", "restart", "ollama")
    wait_up()


def tsv(path: Path) -> list[tuple[str, dict]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row, _, body = line.partition("\t")
        if row.isdigit():
            out.append((row, json.loads(body)))
    return out


def warm_up(tag: str) -> list[str]:
    lines = []
    for row, body in tsv(ROOT / "assignment2/workload/warmup_tickets.tsv"):
        status, resp, secs = http("POST", "/tickets", body, rid=f"warmup-{tag}-{row}")
        lines.append(f"warm-up row {row}: HTTP {status} {resp.get('category')} {secs:.1f} s (discarded)")
        print(lines[-1], flush=True)
    return lines


def stats_total() -> int:
    return http("GET", "/stats", timeout=30)[1]["total"]


def ollama_events(since: str) -> dict:
    log = sh("docker", "compose", "logs", "--no-color", "--since", since, "ollama", check=False)
    return {
        "model_loads": log.count('msg="starting runner"'),
        "evictions": log.count("evicting a model"),
        "runner_killed": log.count("signal: killed"),
    }


def measure_s() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tickets = {row: body for row, body in tsv(ROOT / "step5/data/tickets_load.tsv")}
    dump = set_config("llama")
    restart_ollama()
    log = [f"# S measurement, Llama alone, {now()}", dump, *warm_up("S")]
    timings = []
    for row in S_ROWS:
        status, resp, secs = http("POST", "/tickets", tickets[str(row)], rid=f"S-{row}")
        if status != 201:
            raise SystemExit(f"row {row}: HTTP {status}")
        timings.append(round(secs, 2))
        log.append(f"row {row} ({len(tickets[str(row)]['narrative'].split())} words): {secs:.2f} s -> {resp['category']}")
        print(log[-1], flush=True)
    s = statistics.median(timings)
    interval = 2 * s
    run_min = max(5.0, s)                         # run length: S minutes, at least 5
    timeout_s = max(300.0, 10 * s)                # HTTP response timeout: 10 x S seconds, at least 5 min
    pause_min = timeout_s / 60 + 1                # schedule pause: timeout + 1 min
    result = {
        "measured_utc": now(), "rows": S_ROWS, "timings_s": timings, "S_s": s,
        "interval_s": round(interval, 2), "rate_per_min": round(60 / interval, 4), "rate_per_hour": round(3600 / interval, 2),
        "run_min": round(run_min, 2), "response_timeout_s": round(timeout_s, 1), "pause_min": round(pause_min, 2),
        "expected_tickets_per_run": round(run_min * 60 / interval, 1),
        "client_peak_per_hour": {"A1 peak": 81, "A1 peak + 30% headroom": 105},
    }
    (OUT / "S.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (OUT / "S.md").write_text("\n".join(log + ["", "```json", json.dumps(result, indent=2), "```"]) + "\n", encoding="utf-8")
    side = "ABOVE" if result["rate_per_hour"] > 105 else "BELOW"
    print(json.dumps(result, indent=2))
    print(f"Test rate {result['rate_per_hour']}/h is {side} the A1 client peak (81/h; 105/h with headroom).")
    return 0


def wait_for_jmeter(since: str, expected: int) -> None:
    """Return when the JMeter run is over on the service side: the arrival period has certainly ended
    (first completed JMeter POST + run length) and no JMeter POST has completed for 240 s. A request is
    logged when it finishes, whether it succeeded or failed. JMeter's own schedule then still has its
    drain pause (timeout + 1 min) left, so nothing is cut off. `expected` is only for the progress line
    (JMeter sends floor(rate x run length) arrivals); the .jtl and /stats reconciliation confirm the count."""
    run_s = json.loads((OUT / "S.json").read_text(encoding="utf-8"))["run_min"] * 60
    seen, first, last_change = 0, None, time.time()
    while True:
        log = sh("docker", "compose", "logs", "--no-color", "--since", since, "api", check=False)
        n = len(re.findall(r"request_id=post-\S+ method=POST path=/tickets ", log))
        if n != seen:
            seen, last_change = n, time.time()
            first = first or last_change
            print(f"  {now()}  JMeter POSTs completed: {n} (about {expected} expected)", flush=True)
        if first and time.time() >= first + run_s and time.time() - last_change >= 240:
            return
        time.sleep(10)


def run(config: str, n: int, expected: int = 0) -> int:
    if config not in CONFIGS:
        raise SystemExit(f"config must be one of {list(CONFIGS)}")
    d = OUT / config / f"run{n}"
    if (d / "stats_after.json").exists():
        raise SystemExit(f"{d} already finished; keep it (rename to run{n}_invalid if it was invalid)")
    d.mkdir(parents=True, exist_ok=True)
    (d / "env.txt").write_text(set_config(config) + "\n", encoding="utf-8")
    restart_ollama()
    (d / "warmup.txt").write_text("\n".join(warm_up(f"{config}-run{n}")) + "\n", encoding="utf-8")
    if config.startswith("cascade"):
        out = sh("docker", "compose", "exec", "-T", "api", "python", "-", stdin=ROOT / "assignment2/scripts/cascade_warmup.py", check=False)
        (d / "cascade_warmup.txt").write_text(out, encoding="utf-8")
        print(out.strip())
        if "READY: both models resident" not in out:
            raise SystemExit("cascade warm-up NOT READY: do not start the run")
    ps = sh("docker", "compose", "exec", "-T", "ollama", "ollama", "ps")
    (d / "ollama_ps_before.txt").write_text(ps, encoding="utf-8")
    before = stats_total()
    ready = now()
    (d / "stats_before.json").write_text(json.dumps({"total": before, "utc": ready}), encoding="utf-8")
    print(ps.strip())
    print(f"\n*** READY {config} run {n} at {ready}  (/stats total {before}) ***")
    if expected:
        print(f"Start JMeter on the load-generator PC now. Finishing automatically once {expected} JMeter POSTs are logged.", flush=True)
        wait_for_jmeter(ready, expected)
    else:
        print("Start JMeter on the load-generator PC now. Press ENTER here after JMeter has finished.\a", flush=True)
        input()
    after = stats_total()
    done = now()
    (d / "stats_after.json").write_text(json.dumps({"total": after, "utc": done, "delta": after - before}), encoding="utf-8")
    (d / "api.log").write_text(sh("docker", "compose", "logs", "--no-color", "--timestamps", "api"), encoding="utf-8")
    (d / "ollama.log").write_text(sh("docker", "compose", "logs", "--no-color", "--timestamps", "ollama"), encoding="utf-8")
    (d / "ollama_ps_after.txt").write_text(sh("docker", "compose", "exec", "-T", "ollama", "ollama", "ps"), encoding="utf-8")
    events = ollama_events(ready) | {"window": [ready, done], "stats_delta": after - before}
    (d / "ollama_events_during_run.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    print(json.dumps(events, indent=2))
    if events["model_loads"] or events["evictions"] or events["runner_killed"]:
        print("WARNING: a model loaded/evicted/killed DURING the run; report this run as affected by loading.")
    print(f"Saved {d.relative_to(ROOT)}. Commit it with the load-generator's files.")
    return 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["measure-s"]:
        raise SystemExit(measure_s())
    if sys.argv[1:2] == ["run"] and len(sys.argv) == 4:
        raise SystemExit(run(sys.argv[2], int(sys.argv[3])))
    if sys.argv[1:2] == ["series"] and len(sys.argv) == 3:
        # Runs 1-3 back to back (skipping finished ones); each finishes once the expected number of
        # JMeter POSTs (S.json) have completed in the API log.
        exp = round(json.loads((OUT / "S.json").read_text(encoding="utf-8"))["expected_tickets_per_run"])
        for i in (1, 2, 3):
            if not (OUT / sys.argv[2] / f"run{i}" / "stats_after.json").exists():
                run(sys.argv[2], i, exp)
        raise SystemExit(0)
    raise SystemExit(__doc__)
