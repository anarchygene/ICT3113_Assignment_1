"""Assignment 2 triage: one model (Assignment 1) or a two-model cascade (assignment2/STEP2.md).

Cascade rule:
  1. The small model classifies the ticket with the unchanged Assignment 1 request.
  2. If its answer is invalid (the Assignment 1 parser rejects it), escalate   -> reason "invalid".
  3. If its predicted category is in CASCADE_ESCALATE_ON, escalate             -> reason "category".
  4. Otherwise its answer is final                                             -> reason "accept".
  An escalated ticket is classified by the large model, whose answer is final. If that answer
  is invalid, the request fails (HTTP 502) exactly as in Assignment 1; there is no fall-back.

Every ticket produces one log line, `triage {json}`, recording which model answered and whether
it escalated, so the escalation fraction can be derived from the service log.
"""
import json
import logging
import time
from dataclasses import asdict, dataclass
from typing import Protocol

from app.categories import Category
from app.classifier import ClassificationError
from app.config import Settings

logger = logging.getLogger("complaints.triage")


class Classifier(Protocol):
    async def classify(self, narrative: str, model: str | None = None) -> Category: ...


@dataclass
class TriageRecord:
    request_id: str
    mode: str  # "single" or "cascade"
    small_model: str | None = None
    small_answer: str | None = None  # a category, or "invalid"
    small_ms: float | None = None
    escalated: bool = False
    reason: str = "single"  # "single", "accept", "category" or "invalid"
    final_model: str | None = None
    large_ms: float | None = None
    category: str | None = None
    outcome: str = "ok"  # "ok" or "error" (final model invalid -> HTTP 502)


async def _timed(classifier: Classifier, narrative: str, model: str) -> tuple[Category | None, float, Exception | None]:
    started = time.perf_counter()
    try:
        category = await classifier.classify(narrative, model)
        error = None
    except ClassificationError as exc:
        category, error = None, exc
    return category, round((time.perf_counter() - started) * 1000, 1), error


class Triage:
    def __init__(self, settings: Settings, classifier: Classifier):
        self.settings = settings
        self.classifier = classifier

    @property
    def model_label(self) -> str:
        """Model name returned to callers and stored with every ticket."""
        return self.settings.service_model_label

    async def classify(self, narrative: str, request_id: str) -> Category:
        """Return the final category, or raise ClassificationError (the endpoint turns it into 502)."""
        if self.settings.cascade_enabled:
            record, error = await self._cascade(narrative, request_id)
        else:
            record, error = await self._single(narrative, request_id)
        logger.info("triage %s", json.dumps(asdict(record)))
        if error is not None:
            raise error  # the final model's own ClassificationError, as in Assignment 1
        return Category(record.category)

    async def _single(self, narrative: str, request_id: str) -> tuple[TriageRecord, Exception | None]:
        model = self.settings.ollama_model
        category, ms, error = await _timed(self.classifier, narrative, model)
        record = TriageRecord(request_id=request_id, mode="single", final_model=model, large_ms=ms)
        return self._finish(record, category, error)

    async def _cascade(self, narrative: str, request_id: str) -> tuple[TriageRecord, Exception | None]:
        small, large = self.settings.cascade_small_model, self.settings.cascade_large_model
        record = TriageRecord(request_id=request_id, mode="cascade", small_model=small)

        category, record.small_ms, error = await _timed(self.classifier, narrative, small)
        if error is not None:
            logger.warning("small_model_invalid request_id=%s model=%s error=%s", request_id, small, error)
            record.small_answer, record.escalated, record.reason = "invalid", True, "invalid"
        else:
            record.small_answer = category.value
            if category.value in self.settings.escalate_on:
                record.escalated, record.reason = True, "category"

        if not record.escalated:
            record.reason, record.final_model, record.category = "accept", small, category.value
            return record, None

        record.final_model = large
        category, record.large_ms, error = await _timed(self.classifier, narrative, large)
        return self._finish(record, category, error)

    @staticmethod
    def _finish(
        record: TriageRecord, category: Category | None, error: Exception | None
    ) -> tuple[TriageRecord, Exception | None]:
        if error is not None:
            logger.error(
                "classification_failed request_id=%s model=%s error=%s", record.request_id, record.final_model, error
            )
            record.outcome = "error"
        else:
            record.category = category.value
        return record, error
