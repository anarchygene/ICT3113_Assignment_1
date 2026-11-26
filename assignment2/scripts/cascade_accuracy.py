#!/usr/bin/env python3
"""A2 Step 4 accuracy test for one cascade setting, SERVICE PC (Lenovo). Run ONCE per setting.

  python assignment2/scripts/cascade_accuracy.py cascadeA
  python assignment2/scripts/cascade_accuracy.py cascadeB

1. Sets .env for the setting (speed_service.CONFIGS, from STEP2.md §6), recreates the api, saves the env dump.
2. Restarts Ollama, runs cascade_warmup.py (must print READY: both models resident), saves `ollama ps`.
3. Sends the 80 test rows (assignment2/data/test_set.csv, frozen A1 text) through POST /tickets, one at a
   time, with step5/scripts/accuracy_test.py and label a2-<setting> (request IDs acc-a2-<setting>-<row>).
4. Saves the API log (one `triage` line per ticket), the Ollama log, `ollama ps` after, and counts model
   loads / evictions / runner kills during the test.
Output: assignment2/results/accuracy/<setting>/
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import speed_service as s  # noqa: E402

LABEL_MODEL = "cascade:gemma3:1b-it-q4_K_M>llama3.1:8b-instruct-q4_K_M"


def main() -> int:
    setting = sys.argv[1]
    assert setting in ("cascadeA", "cascadeB"), "setting must be cascadeA or cascadeB"
    out = s.ROOT / "assignment2" / "results" / "accuracy" / setting
    if (out / "predictions.csv").exists():
        raise SystemExit(f"{out} already has results; the brief allows one run per configuration")
    out.mkdir(parents=True, exist_ok=True)

    (out / "env.txt").write_text(s.set_config(setting) + "\n", encoding="utf-8")
    s.restart_ollama()
    warm = s.sh("docker", "compose", "exec", "-T", "api", "python", "-", stdin=s.ROOT / "assignment2/scripts/cascade_warmup.py", check=False)
    (out / "cascade_warmup.txt").write_text(warm, encoding="utf-8")
    print(warm.strip())
    if "READY: both models resident" not in warm:
        raise SystemExit("NOT READY: both models are not resident; accuracy test not started")
    (out / "ollama_ps_before.txt").write_text(s.sh("docker", "compose", "exec", "-T", "ollama", "ollama", "ps"), encoding="utf-8")

    start = s.now()
    p = subprocess.run(
        [sys.executable, "step5/scripts/accuracy_test.py", "--label", f"a2-{setting}", "--model", LABEL_MODEL,
         "--golden", "assignment2/data/test_set.csv", "--out", str(out)],
        cwd=s.ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    (out / "accuracy_test_console.txt").write_text(p.stdout + p.stderr, encoding="utf-8")
    end = s.now()

    (out / "api.log").write_text(s.sh("docker", "compose", "logs", "--no-color", "--timestamps", "api"), encoding="utf-8")
    (out / "ollama.log").write_text(s.sh("docker", "compose", "logs", "--no-color", "--timestamps", "ollama"), encoding="utf-8")
    (out / "ollama_ps_after.txt").write_text(s.sh("docker", "compose", "exec", "-T", "ollama", "ollama", "ps"), encoding="utf-8")
    events = s.ollama_events(start) | {"window": [start, end], "accuracy_test_exit": p.returncode}
    (out / "ollama_events_during_test.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    print(json.dumps(events, indent=2))
    print((out / "summary.md").read_text(encoding="utf-8") if (out / "summary.md").exists() else p.stdout[-3000:] + p.stderr[-3000:])
    return p.returncode


if __name__ == "__main__":
    raise SystemExit(main())
