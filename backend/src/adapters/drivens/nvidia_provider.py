# from src.constants import PROJECT_ROOT
import os

from dotenv import load_dotenv
# load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.language_models import BaseChatModel

from src.ports.drivens.ai_provider_port import AiModelPort, AiProviderPort

nvidia_api_key = os.environ["NVIDIA_API_KEY"] or ""

class NvidiaProviderAdapter(AiProviderPort):
    def __init__(self, model_adapter: AiModelPort, temperature: float):
        self.current_model_adapter = model_adapter

        # base_url = "https://integrate.api.nvidia.com/v1",
        # model = "nvidia/nemotron-3.5-super-vl-120b-a12b",
        # api_key = os.environ["NVIDIA_API_KEY"],
        # temperature = 1,
        # top_p = 0.95,
        # max_completion_tokens = 16384,
        #
        # seed = 42,
        self._container = ChatNVIDIA(
            base_url="https://integrate.api.nvidia.com/v1",
            model=model_adapter.codename,
            top_p=0.95,
            max_completion_tokens=16384,
            temperature=temperature,
            api_key=os.environ["NVIDIA_API_KEY"],
        )
        self.provider_name = "nvidia"

    def change_temperature(self, temperature: float):
        super().change_temperature(temperature)
        self._container.temperature = temperature

    def get_container(self) -> BaseChatModel:
        return super().get_container()