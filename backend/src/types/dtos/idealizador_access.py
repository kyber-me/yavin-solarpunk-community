from pydantic import BaseModel, Field


class IdealizadorAccessRequest(BaseModel):
    key: str = Field(min_length=1)
