from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    history: List[Message] = Field(default_factory=list)


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    suggested_questions: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
