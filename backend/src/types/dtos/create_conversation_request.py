from pydantic import BaseModel  # Field


class CreateConversationRequest(BaseModel):
    sender_id: str
    participant_id: str

    # def __init__(self, /, **data: Any):
    #     super().__init__(data)


