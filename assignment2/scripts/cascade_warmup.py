"""A2 cascade warm-up check (assignment2/STEP2.md §7): make both cascade models resident before a run.

Run INSIDE the api container, after the Ollama restart and the three fixed warm-up tickets
sent through POST /tickets:

  docker compose exec -T api python - < assignment2/scripts/cascade_warmup.py

Sends one fixed synthetic ticket directly to each model through Ollama, using the service's exact
request (same prompt, JSON mode, temperature 0, num_ctx 4096), in the order large, small, large,
small. The large model goes first because loading it second can evict the small model (Lenovo
pre-flight, 25 Nov: Gemma -> Llama), which would make the small model's next call a reload. Any
such reload happens here, not in the measured run. Prints one JSON line per call, then `ollama ps`
as JSON.

Exit code 0 = ready: both models listed and the last two calls loaded in under 1 s.
Exit code 1 = do not start the run.
"""
import json
import sys
import time

import httpx

from app.classifier import SYSTEM_PROMPT
from app.config import get_settings

TICKETS = [
    "Warm-up 1. My checking account was charged an overdraft fee even though my deposit had cleared.",
    "Warm-up 2. A debt collector keeps calling my workplace about a loan I already repaid.",
    "Warm-up 3. The servicer applied my escrow payment late and charged me a penalty.",
    "Warm-up 4. A transfer I sent through a payment app went to the wrong person and was not refunded.",
]


def chat(client: httpx.Client, base: str, model: str, text: str) -> dict:
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_ctx": 4096},
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
    }
    started = time.perf_counter()
    response = client.post(f"{base}/api/chat", json=payload)
    response.raise_for_status()
    body = response.json()
    return {
        "model": model,
        "wall_s": round(time.perf_counter() - started, 2),
        "load_s": round(body.get("load_duration", 0) / 1e9, 2),
    }


def main() -> int:
    settings = get_settings()
    if not settings.cascade_enabled:
        print("CASCADE_ENABLED is false; this check is only for cascade runs", file=sys.stderr)
        return 1
    small, large, base = settings.cascade_small_model, settings.cascade_large_model, settings.ollama_base_url
    with httpx.Client(timeout=600) as client:
        calls = [chat(client, base, model, text) for model, text in zip([large, small, large, small], TICKETS)]
        for call in calls:
            print(json.dumps(call), flush=True)
        loaded = {m["name"] for m in client.get(f"{base}/api/ps").json().get("models", [])}
    print(json.dumps({"ollama_ps": sorted(loaded)}), flush=True)

    ready = {small, large} <= loaded and all(call["load_s"] < 1 for call in calls[-2:])
    print("READY: both models resident" if ready else "NOT READY: do not start the run", flush=True)
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
