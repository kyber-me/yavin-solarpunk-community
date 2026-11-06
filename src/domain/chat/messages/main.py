from datetime import time

from pydantic import BaseModel
from ulid import ULID


class TextMessage(BaseModel):
    id: str
    conversation_id: str
    conversation_look_up_id: str
    content: str
    sender: str
    receiver: str
    created_at: time = time()

    def __init__(
        self,
        content: str,
        sender: str,
        receiver: str,
        conversation_id: str,
        conversation_look_up_id: str,
    ) -> None:
        self.id = f"Mess_{ULID()}"
        self.content = content
        self.sender = sender
        self.receiver = receiver
        self.conversation_id = conversation_id
        self.conversation_look_up_id = conversation_look_up_id
