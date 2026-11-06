from datetime import time

from pydantic import BaseModel
from ulid import ULID

from src.domain.chat.conversations.value_objects.conversation_id import ConversationId


class Conversation(BaseModel):
    id: str
    look_up_key: str  # It's a combination of the 2 ULID's from sender and receiver plus a prefix and a separator '_'
    thread_id: str
    created_at: time = time()
    start_date: time | None = None
    end_date: time | None = None
    active: bool = False

    def __init__(self, conversation_id: ConversationId, thread_id: str) -> None:
        super().__init__(
            id=f"Conv_{ULID()}", look_up_key=conversation_id.id, thread_id=thread_id
        )
