"""Response and request models (they also document the API at /docs)."""
from typing import Optional

from pydantic import BaseModel, Field


class Count(BaseModel):
    name: str
    n: int


class Stats(BaseModel):
    nodes: list[Count]
    relations: list[Count]
    articles: int
    facts: int


class EntitySummary(BaseModel):
    name: str
    type: str
    degree: int


class Fact(BaseModel):
    subject: str
    subject_type: str
    relation: str
    object: str
    object_type: str
    support: int
    source: str


class Article(BaseModel):
    title: str
    url: str
    date: Optional[str] = None


class EntityDetail(BaseModel):
    name: str
    type: str
    threshold: Optional[str] = None
    mentioned_in: int
    facts: list[Fact]


class SymptomQuery(BaseModel):
    symptoms: list[str] = Field(min_length=1, max_length=20)
    min_support: int = Field(1, ge=0)


class SymptomMatch(BaseModel):
    type: str
    matched: list[str]
    evidence: int


class Path(BaseModel):
    nodes: list[EntitySummary]
    relations: list[str]
    forward: list[bool]      # False: the fact points from the next node back to this one
