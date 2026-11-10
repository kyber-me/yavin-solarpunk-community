from abc import ABC, abstractmethod
from typing import Literal, Any

from ports.drivens.ai_provider_port import AiProviderPort
from src.types.adapters.content_type_return import ContentTypeReturn


class AiGatewayPort(ABC):
    ai_provider_port: AiProviderPort

    @abstractmethod
    def __init__(self, options: object, model: Literal["gpt-4o-mini", "qwen/qwen3.8-27b"]):
        ...

    @abstractmethod
    def invoke(self, thread_id: str, retrieval_knowledge_base: list[ContentTypeReturn]) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_mapped_state_messages(self, thread_id: str) -> list[ContentTypeReturn] | list[Any]:
        ...

    @abstractmethod
    def should_load(self, thread_id: str) -> bool:
        ...


# class LlmPort(ABC):
#     @abstractmethod
#     def get_llm(self) -> str:
#         pass