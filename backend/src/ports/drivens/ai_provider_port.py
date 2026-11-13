from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel

from ports import AiModelPort


# What is the effect of having a Qwen Provider Adapter in the system?

# In someway, AiProvider is coupled with LangChain drought `BaseChatModel`
class AiProviderPort(ABC):
    _container: BaseChatModel

    provider_name: str
    current_model_adapter: AiModelPort

    @abstractmethod
    def __init__(self, model_adapter: AiModelPort):
        ...

    @abstractmethod
    def change_temperature(self, temperature: float):
        self._container.temperature = temperature


    @abstractmethod
    def get_container(self) -> BaseChatModel:
        return self._container






