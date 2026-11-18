import os

from dotenv import load_dotenv
load_dotenv()

from langchain_core.embeddings import Embeddings
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from src.ports import EmbeddingsModelIntegrationPort


class NvidiaEmbeddings(EmbeddingsModelIntegrationPort):

    def get_embeddings_size(self, text: str) -> int:
        return super().get_embeddings_size(text)

    _embedding_container: Embeddings

    def __init__(self):
        self._embedding_container = NVIDIAEmbeddings(model="nvidia/nemotron-3.5-embed-1b", nvidia_api_key=os.getenv("NVIDIA_API_KEY"))

    def embed_query(self, text: str) -> list[float | int]:
        return super().embed_query(text)

    def embed_documents(self):
        raise NotImplementedError()

    def get(self) -> Embeddings:
        return super().get()
