"""Persisted conversation and message read contracts; never expose agent threads."""
from datetime import datetime

from pydantic import BaseModel


class ConversationSummary(BaseModel):
    conversation_id: str
    title: str
    participant_id: str
    participant_name: str
    created_at: datetime
    active: bool


class ConversationPage(BaseModel):
    conversations: list[ConversationSummary]
    next_offset: int | None = None


class StoredMessage(BaseModel):
    id: str
    sender_id: str
    content: str
    created_at: datetime


class MessagePage(BaseModel):
    messages: list[StoredMessage]
    next_offset: int | None = None
