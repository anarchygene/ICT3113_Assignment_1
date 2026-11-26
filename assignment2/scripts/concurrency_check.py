"""Diagnostic (not a benchmark): do concurrent Gemma + Llama calls slow each other down?

Run INSIDE the api container with both cascade models already resident:
  docker compose exec -T api python - < assignment2/scripts/concurrency_check.py

Synthetic tickets only. Uses the service's exact request (prompt, JSON, temperature 0, num_ctx 4096).
Phase 1: Llama then Gemma, one at a time (x2). Phase 2: Llama and Gemma started at the same moment (x2).
Each phase prints per-call wall time and the VM-wide major page faults (pgmajfault, /proc/vmstat), i.e.
pages that had to be read back from disk. Different synthetic text per call, so no prompt-cache reuse.
"""
import json
import threading
import time

import httpx

from app.classifier import SYSTEM_PROMPT
from app.config import get_settings

S = get_settings()
SMALL, LARGE, BASE = S.cascade_small_model, S.cascade_large_model, S.ollama_base_url
TEXTS = [f"Synthetic concurrency check {i}. My bank charged a monthly maintenance fee on my checking account "
         f"even though I kept the minimum balance for the whole statement period number {i}." for i in range(1, 9)]


def majfaults() -> int:
    for line in open("/proc/vmstat"):
        if line.startswith("pgmajfault "):
            return int(line.split()[1])
    return -1


def call(model: str, text: str, out: dict, key: str) -> None:
    payload = {"model": model, "stream": False, "format": "json", "options": {"temperature": 0, "num_ctx": 4096},
               "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}]}
    t = time.perf_counter()
    r = httpx.post(f"{BASE}/api/chat", json=payload, timeout=900).json()
    out[key] = {"model": model.split(":")[0], "wall_s": round(time.perf_counter() - t, 2), "load_s": round(r.get("load_duration", 0) / 1e9, 2)}


def phase(name: str, concurrent: bool, texts: list[str]) -> None:
    out: dict = {}
    f0, t0 = majfaults(), time.perf_counter()
    if concurrent:
        ths = [threading.Thread(target=call, args=(LARGE, texts[0], out, "large")),
               threading.Thread(target=call, args=(SMALL, texts[1], out, "small"))]
        [t.start() for t in ths]
        [t.join() for t in ths]
    else:
        call(LARGE, texts[0], out, "large")
        call(SMALL, texts[1], out, "small")
    print(json.dumps({"phase": name, **out, "total_s": round(time.perf_counter() - t0, 2), "major_page_faults": majfaults() - f0}), flush=True)


phase("sequential-1", False, TEXTS[0:2])
phase("sequential-2", False, TEXTS[2:4])
phase("concurrent-1", True, TEXTS[4:6])
phase("concurrent-2", True, TEXTS[6:8])
