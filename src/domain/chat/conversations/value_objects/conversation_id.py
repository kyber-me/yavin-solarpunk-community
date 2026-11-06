from pydantic import BaseModel


class ConversationId(BaseModel):
    _id: str

    def __init__(self, sender: str, receiver: str) -> None:
        self._id = "Conv_" + sender + "_" + receiver

    @property
    def id(self) -> str:
        return self._id
