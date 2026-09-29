#!/usr/bin/env python3
import json
import sys
import urllib.parse
import urllib.request


BASE_URL = "http://localhost:8000"


def request(method: str, path: str, data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        BASE_URL + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=360) as response:
        return json.load(response)


def main() -> int:
    assert request("GET", "/health") == {"status": "ok"}
    narrative = "A debt collector keeps calling me about a debt I do not recognize."
    ticket = request("POST", "/tickets", {"narrative": narrative})
    assert ticket["category"]
    query = urllib.parse.quote("debt collector")
    search = request("GET", f"/search?q={query}")
    assert any(item["id"] == ticket["id"] for item in search["tickets"])
    stats = request("GET", "/stats")
    assert stats["total"] >= 1
    assert len(stats["counts"]) == 7
    print(json.dumps({"ticket": ticket, "stats": stats}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

