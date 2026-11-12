from abc import ABC, abstractmethod
from typing import Any
from fastapi import Request


class IService(ABC):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    @abstractmethod
    def run(cls, dto: Any, request: Request) -> Any: ...

