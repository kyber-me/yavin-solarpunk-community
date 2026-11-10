from typing import Literal, TypedDict


class ContentTypeReturn(TypedDict):
    content: str
    type: Literal["human", "ai", "system"]