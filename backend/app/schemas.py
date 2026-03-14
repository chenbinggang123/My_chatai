from typing import Any, Literal

from pydantic import BaseModel, Field


class HatchRequest(BaseModel):
    chat_log: str = Field(min_length=1)
    relationship_context: str | None = None
    user_preference: str | None = None
    hatch_goal: str | None = None


class LearnRequest(BaseModel):
    brain_id: str = Field(min_length=1)
    chat_log: str = Field(min_length=1)
    learn_goal: str | None = None


class ChatHistoryTurn(BaseModel):
    role: Literal["user", "pet"]
    content: str


class ChatRequest(BaseModel):
    brain_id: str = Field(min_length=1)
    user_message: str = Field(min_length=1)
    history: list[ChatHistoryTurn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    brain_id: str
    reply: str


class BrainStateResponse(BaseModel):
    brain_id: str
    brain_state: dict[str, Any]


class LearnResponse(BaseModel):
    brain_id: str
    updated_fields: list[str]
    brain_state: dict[str, Any]


class ErrorResponse(BaseModel):
    error: dict[str, Any]


class HealthResponse(BaseModel):
    status: Literal["ok"]


# ---------------------------------------------------------------------------
# 聊天导入记录查询
# ---------------------------------------------------------------------------

class ChatImportItem(BaseModel):
    import_id: str
    brain_id: str | None = None
    mode: str
    chat_length: int
    created_at: str
    excerpt: str


class ChatImportListResponse(BaseModel):
    items: list[ChatImportItem]
    total: int
    limit: int
    offset: int
