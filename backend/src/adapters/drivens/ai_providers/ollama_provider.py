from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel

from src.ports import AiModelPort, AiProviderPort


class OllamaProviderAdapter(AiProviderPort):
    def __init__(self, model_adapter: AiModelPort, temperature: float):
        self.current_model_adapter = model_adapter

        self._container = ChatOllama(model=model_adapter.codename, temperature=temperature)
        self.provider_name = "ollama"

    def change_temperature(self, temperature: float):
        super().change_temperature(temperature)
        self._container.temperature = temperature

    def get_container(self) -> BaseChatModel:
        return super().get_container()