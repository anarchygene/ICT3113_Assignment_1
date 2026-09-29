from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.categories import Category


class TicketCreate(BaseModel):
    narrative: str = Field(min_length=1, max_length=20_000)


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    narrative: str
    category: Category
    model: str
    created_at: datetime


class SearchResponse(BaseModel):
    query: str
    count: int
    tickets: list[TicketResponse]


class StatsResponse(BaseModel):
    total: int
    counts: dict[Category, int]

