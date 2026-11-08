from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass(frozen=True)
class ConversationRecord:
    id: str
    sender_id: str
    participant_id: str
    thread_id: str
    updated_at: datetime | None = field(default=None)
    start_date: datetime | None = field(default=None)
    end_date: datetime | None = field(default=None)
    active: bool = field(default=True)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC)) # What does mean the parameter `init`? It initializes the field with a default value?
