from pydantic import BaseModel, Field

from src.domain.chat.messages.main import TextMessage


class ChatServiceRequestDto(BaseModel):
    message: str | TextMessage
    sender_id: str
    receiver_id: str = "silas"
    thread_id: str = Field(min_length=1)
