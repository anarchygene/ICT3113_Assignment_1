#!/usr/bin/env python3
"""Pre-flight check of the A2 service on the test machine (TUNING rows only; not a benchmark).

For each row: POST /tickets with X-Request-ID=pre-<mode>-<row>, compare the returned category with the
expected one, then find that request's `triage {...}` line in `docker compose logs api`.

  python assignment2/scripts/preflight_check.py <mode> <row>=<expected category>[@<small|large|single>] ...

An expected value of 502 means the request must fail with HTTP 502 (final model invalid).
<mode> is a free label (e.g. single, cascadeA). The optional @model says which model must have produced
the final answer according to the triage line. Expected answers come from the Assignment 1 per-ticket
records (step5/results/<model>/accuracy/predictions.csv). Prints one result line per row and exits 1 on
any mismatch.
"""
import csv
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "http://localhost:8000"


def main() -> int:
    mode, specs = sys.argv[1], sys.argv[2:]
    narratives = {r["row"]: r["narrative"] for r in csv.DictReader(open(ROOT / "assignment2/data/tuning_set.csv", encoding="utf-8"))}
    failures = 0
    for spec in specs:
        row, _, rest = spec.partition("=")
        expected, _, want_final = rest.partition("@")
        assert row in narratives, f"row {row} is not a tuning row"
        rid = f"pre-{mode}-{row}"
        req = urllib.request.Request(
            BASE + "/tickets", data=json.dumps({"narrative": narratives[row]}).encode(), method="POST",
            headers={"Content-Type": "application/json", "X-Request-ID": rid},
        )
        try:
            with urllib.request.urlopen(req, timeout=900) as resp:
                body, status = json.load(resp), resp.status
        except urllib.error.HTTPError as exc:  # e.g. 502 when the final model's answer is invalid
            body, status = {"category": str(exc.code), "model": "-"}, exc.code
        logs = subprocess.run(["docker", "compose", "logs", "--no-color", "api"], cwd=ROOT, capture_output=True, text=True).stdout
        lines = [json.loads(m.group(1)) for m in re.finditer(r"triage (\{.*\})", logs) if f'"request_id": "{rid}"' in m.group(1)]
        t = lines[0] if len(lines) == 1 else {}
        final = {"single": "single"}.get(t.get("mode"), "small" if t.get("final_model") == t.get("small_model") else "large")
        ok = (status == 201 or expected == str(status)) and body["category"] == expected and len(lines) == 1 and (not want_final or final == want_final)
        failures += not ok
        print(f"{mode:<9} {row} {status} {body['category']:<26} expected {expected:<26} {'MATCH' if ok else 'MISMATCH'}"
              f"  model_field={body['model']}  triage_lines={len(lines)} small={t.get('small_answer')} "
              f"escalated={t.get('escalated')} reason={t.get('reason')} final_model={t.get('final_model')}"
              f" small_ms={t.get('small_ms')} large_ms={t.get('large_ms')}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
