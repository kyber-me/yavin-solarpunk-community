from pydantic import BaseModel

from src.domain.chat.messages.main import TextMessage


class ChatServiceRequestDto(BaseModel):
    message: TextMessage
    sender_id: str
    receiver_id: str
    thread_id: str
