from ulid import ULID

from pydantic import AwareDatetime, BaseModel, Field
from datetime import UTC, datetime


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(ULID()))
    content: str = Field(min_length=1)
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: AwareDatetime | None = Field(default=None)
    deleted_at: AwareDatetime | None = Field(default=None)

class ChatServiceRequest(BaseModel):
    sender_id: str
    conversation_id: str
    message: str = Field(min_length=1)
    # thread_id: str = Field(min_length=1)
