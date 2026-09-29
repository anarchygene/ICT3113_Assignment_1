import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.categories import CATEGORY_VALUES, Category
from app.classifier import ClassificationError, OllamaClassifier
from app.config import get_settings
from app.database import Base, engine, get_db
from app.models import Ticket
from app.schemas import SearchResponse, StatsResponse, TicketCreate, TicketResponse

settings = get_settings()
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("complaints.api")
classifier = OllamaClassifier(settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Complaint Classification Baseline", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.2f client=%s",
            request_id,
            request.method,
            request.url.path,
            status_code,
            elapsed_ms,
            request.client.host if request.client else "unknown",
        )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> Ticket:
    narrative = payload.narrative.strip()
    if not narrative:
        raise HTTPException(status_code=422, detail="Narrative must not be blank")
    try:
        category = await classifier.classify(narrative)
    except ClassificationError as exc:
        logger.exception("classification_failed model=%s", settings.ollama_model)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    ticket = Ticket(
        narrative=narrative,
        category=category.value,
        model=settings.ollama_model,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/search", response_model=SearchResponse)
def search_tickets(
    q: str = Query(min_length=1, max_length=500),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> SearchResponse:
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Search query must not be blank")
    tickets = db.scalars(
        select(Ticket)
        .where(Ticket.narrative.ilike(f"%{query}%"))
        .order_by(Ticket.id.desc())
        .limit(limit)
    ).all()
    return SearchResponse(query=query, count=len(tickets), tickets=list(tickets))


@app.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)) -> StatsResponse:
    rows = db.execute(select(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category))
    observed = dict(rows.all())
    counts = {Category(name): observed.get(name, 0) for name in CATEGORY_VALUES}
    return StatsResponse(total=sum(counts.values()), counts=counts)

