from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


ConversationTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class ConversationDetails(BaseModel):
    title: ConversationTitle
    participant_id: str

class CreateConversationRequest(BaseModel):
    owner_id: str
    conversation_details: ConversationDetails

class UpdateConversationTitleRequest(BaseModel):
    owner_id: str = Field(min_length=1)
    title: ConversationTitle

