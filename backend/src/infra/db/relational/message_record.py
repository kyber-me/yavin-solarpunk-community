"""Immutable representation of a persisted message, independent of Pydantic."""
from dataclasses import dataclass, field
from datetime import UTC, datetime
from ulid import ULID


@dataclass(frozen=True)
class MessageRecord:
    conversation_id: str
    sender_id: str
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: str = field(default_factory=lambda: str(ULID()))
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
