from datetime import time

from pydantic import BaseModel, Field
from ulid import ULID


class TextMessage(BaseModel):
    id: str = Field(default_factory=lambda: f"Mess_{ULID()}")
    conversation_id: str
    conversation_look_up_id: str
    content: str = Field(min_length=1)
    sender: str
    receiver: str
    created_at: time = time()
