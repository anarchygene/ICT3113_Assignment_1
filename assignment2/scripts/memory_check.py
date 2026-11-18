"""A2 Step 2 memory check: can two candidate models stay loaded in Ollama together?

Runs INSIDE the api container (it has httpx and the app's prompt), so requests are
byte-identical to the service's: same system prompt, format=json, temperature 0,
num_ctx 4096. Uses synthetic tickets only (no dataset or golden-set text).

  docker compose restart ollama
  docker compose exec -T api python - <MODEL_A> <MODEL_B> < assignment2/scripts/memory_check.py

Sequence: A, A, B, B, then A, B, A, B. After each call it records the call's
load_duration and Ollama's /api/ps. Both models resident means: /api/ps lists both after
the B calls, and the alternating calls show near-zero load_duration (no reload).
Prints one JSON object per call.
"""
import json
import sys
import time

import httpx

from app.classifier import SYSTEM_PROMPT

OLLAMA = "http://ollama:11434"
TICKETS = [
    "Synthetic check 1. My debit card was declined at a supermarket even though my checking account had enough money.",
    "Synthetic check 2. A collection agency keeps calling about a medical bill that I already paid in full last year.",
    "Synthetic check 3. My mortgage servicer added a late fee although my payment was sent before the due date.",
    "Synthetic check 4. A wire transfer I sent to my sister never arrived and the bank cannot tell me where it is.",
    "Synthetic check 5. An account I never opened appears on my credit report and the bureau will not remove it.",
    "Synthetic check 6. My credit card was charged twice for one hotel booking and the dispute was rejected.",
    "Synthetic check 7. The lender on my car loan applied my extra payment to interest instead of principal.",
    "Synthetic check 8. My savings account was frozen without notice and I cannot reach anyone at the branch.",
]


def chat(client: httpx.Client, model: str, text: str) -> dict:
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_ctx": 4096},
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
    }
    started = time.perf_counter()
    r = client.post(f"{OLLAMA}/api/chat", json=payload)
    r.raise_for_status()
    body = r.json()
    return {
        "wall_s": round(time.perf_counter() - started, 2),
        "load_s": round(body.get("load_duration", 0) / 1e9, 2),
        "answer": body["message"]["content"][:60],
    }


def main() -> int:
    a, b = sys.argv[1], sys.argv[2]
    order = [a, a, b, b, a, b, a, b]
    with httpx.Client(timeout=600) as client:
        for i, (model, text) in enumerate(zip(order, TICKETS), 1):
            result = chat(client, model, text)
            ps = client.get(f"{OLLAMA}/api/ps").json().get("models", [])
            loaded = [{"name": m["name"], "size_gb": round(m["size"] / 1e9, 2), "ctx": m.get("context_length")} for m in ps]
            print(json.dumps({"call": i, "model": model, **result, "loaded": loaded}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
