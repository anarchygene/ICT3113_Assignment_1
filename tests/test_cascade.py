"""Assignment 2 cascade tests. No Ollama or PostgreSQL needed: Ollama is faked."""
import asyncio
import json
import logging

import httpx
import pytest
from pydantic import ValidationError

import app.classifier as classifier_module
from app.cascade import Triage
from app.categories import Category
from app.classifier import SYSTEM_PROMPT, ClassificationError, OllamaClassifier
from app.config import Settings

SMALL = "qwen3:4b-instruct-2507-q4_K_M"
LARGE = "llama3.1:8b-instruct-q4_K_M"


def settings(**overrides) -> Settings:
    values = dict(
        _env_file=None,
        ollama_model=LARGE,
        cascade_enabled=True,
        cascade_small_model=SMALL,
        cascade_large_model=LARGE,
        cascade_escalate_on="Credit card",
    )
    values.update(overrides)
    return Settings(**values)


class FakeClassifier:
    """Returns a scripted answer per model; a string that is not a category means invalid output."""

    def __init__(self, answers: dict[str, str]):
        self.answers = answers
        self.calls: list[str] = []

    async def classify(self, narrative: str, model: str | None = None) -> Category:
        self.calls.append(model)
        try:
            return Category(self.answers[model])
        except ValueError as exc:
            raise ClassificationError(f"Ollama returned an invalid classification: {exc}") from exc


def run(triage: Triage, caplog) -> tuple[Category | None, dict, Exception | None]:
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="complaints.triage"):
        try:
            category, error = asyncio.run(triage.classify("narrative", "req-1")), None
        except ClassificationError as exc:
            category, error = None, exc
    lines = [r.getMessage() for r in caplog.records if r.getMessage().startswith("triage ")]
    assert len(lines) == 1, "exactly one triage log line per ticket"
    return category, json.loads(lines[0].removeprefix("triage ")), error


def test_accepts_small_model_answer_not_on_list(caplog):
    fake = FakeClassifier({SMALL: "Mortgage", LARGE: "Debt collection"})
    category, log, error = run(Triage(settings(), fake), caplog)
    assert category is Category.MORTGAGE and error is None
    assert fake.calls == [SMALL]
    assert log["escalated"] is False and log["reason"] == "accept"
    assert log["final_model"] == SMALL and log["small_answer"] == "Mortgage" and log["large_ms"] is None


def test_escalates_category_on_list(caplog):
    fake = FakeClassifier({SMALL: "Credit card", LARGE: "Credit reporting"})
    category, log, error = run(Triage(settings(), fake), caplog)
    assert category is Category.CREDIT_REPORTING
    assert fake.calls == [SMALL, LARGE]
    assert log["escalated"] is True and log["reason"] == "category"
    assert log["small_answer"] == "Credit card" and log["final_model"] == LARGE
    assert log["category"] == "Credit reporting" and log["outcome"] == "ok"


def test_escalates_invalid_small_answer(caplog):
    fake = FakeClassifier({SMALL: "bank account or service", LARGE: "Bank account or service"})
    category, log, error = run(Triage(settings(), fake), caplog)
    assert category is Category.BANK_ACCOUNT
    assert log["escalated"] is True and log["reason"] == "invalid" and log["small_answer"] == "invalid"


def test_second_setting_list(caplog):
    fake = FakeClassifier({SMALL: "Credit reporting", LARGE: "Debt collection"})
    triage = Triage(settings(cascade_escalate_on="Credit card, Credit reporting"), fake)
    category, log, _ = run(triage, caplog)
    assert category is Category.DEBT_COLLECTION and log["reason"] == "category"


def test_invalid_large_answer_fails_without_fallback(caplog):
    fake = FakeClassifier({SMALL: "Credit card", LARGE: "Student loan"})
    category, log, error = run(Triage(settings(), fake), caplog)
    assert category is None and isinstance(error, ClassificationError)
    assert log["outcome"] == "error" and log["final_model"] == LARGE and log["category"] is None


def test_single_model_mode_is_assignment1(caplog):
    fake = FakeClassifier({LARGE: "Mortgage"})
    triage = Triage(settings(cascade_enabled=False), fake)
    category, log, _ = run(triage, caplog)
    assert category is Category.MORTGAGE and fake.calls == [LARGE]
    assert log["mode"] == "single" and log["escalated"] is False and log["final_model"] == LARGE
    assert triage.model_label == LARGE


def test_model_label_hides_answering_model():
    assert Triage(settings(), FakeClassifier({})).model_label == f"cascade:{SMALL}>{LARGE}"
    assert Triage(settings(cascade_label="triage-v2"), FakeClassifier({})).model_label == "triage-v2"


@pytest.mark.parametrize(
    "overrides",
    [dict(cascade_escalate_on="credit card"), dict(cascade_escalate_on="Credit card,Other"), dict(cascade_small_model="")],
)
def test_bad_cascade_settings_are_rejected(overrides):
    with pytest.raises(ValidationError):
        settings(**overrides)


def test_ollama_request_is_unchanged_apart_from_model(monkeypatch):
    """The cascade must send each model the exact Assignment 1 request."""
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        answer = {SMALL: "Credit card", LARGE: "credit card"}[seen[-1]["model"]]
        return httpx.Response(200, json={"message": {"content": json.dumps({"category": answer})}})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        classifier_module.httpx,
        "AsyncClient",
        lambda **kw: real_client(transport=httpx.MockTransport(handler), **kw),
    )
    client = OllamaClassifier(settings(ollama_model=SMALL))

    assert asyncio.run(client.classify("text")) is Category.CREDIT_CARD  # default = OLLAMA_MODEL
    with pytest.raises(ClassificationError):  # case-sensitive, as in Assignment 1
        asyncio.run(client.classify("text", LARGE))

    expected = {
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_ctx": 4096},
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": "text"}],
    }
    assert seen == [{"model": SMALL, **expected}, {"model": LARGE, **expected}]


def test_endpoint_returns_fixed_label_and_502(monkeypatch, caplog):
    """POST /tickets keeps its contract: one category back, same model label whichever model answered."""
    from datetime import datetime, timezone

    from fastapi.testclient import TestClient

    import app.main as main

    class FakeSession:
        def add(self, ticket):
            self.ticket = ticket

        def commit(self):
            pass

        def refresh(self, ticket):
            ticket.id, ticket.created_at = 1, datetime.now(timezone.utc)

    fake = FakeClassifier({SMALL: "Mortgage", LARGE: "Credit reporting"})
    monkeypatch.setattr(main, "triage", Triage(settings(), fake))
    main.app.dependency_overrides[main.get_db] = lambda: FakeSession()
    try:
        client = TestClient(main.app)  # no lifespan: no database needed
        with caplog.at_level(logging.INFO, logger="complaints.triage"):
            accepted = client.post("/tickets", json={"narrative": "a"}, headers={"X-Request-ID": "acc-1"})
            fake.answers[SMALL] = "Credit card"
            escalated = client.post("/tickets", json={"narrative": "b"}, headers={"X-Request-ID": "esc-1"})
            fake.answers[LARGE] = "Other"
            failed = client.post("/tickets", json={"narrative": "c"}, headers={"X-Request-ID": "err-1"})
    finally:
        main.app.dependency_overrides.clear()

    assert (accepted.status_code, accepted.json()["category"]) == (201, "Mortgage")
    assert (escalated.status_code, escalated.json()["category"]) == (201, "Credit reporting")
    assert accepted.json()["model"] == escalated.json()["model"] == f"cascade:{SMALL}>{LARGE}"
    assert failed.status_code == 502
    logged = [json.loads(r.getMessage().removeprefix("triage ")) for r in caplog.records if r.getMessage().startswith("triage ")]
    assert [(r["request_id"], r["escalated"], r["outcome"]) for r in logged] == [
        ("acc-1", False, "ok"),
        ("esc-1", True, "ok"),
        ("err-1", True, "error"),
    ]
