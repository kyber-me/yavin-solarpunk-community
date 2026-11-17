import os

from dotenv import load_dotenv
load_dotenv()

from langchain_core.embeddings import Embeddings
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from src.ports import EmbeddingsModelIntegrationPort


class NvidiaEmbeddings(EmbeddingsModelIntegrationPort):

    _embedding_container: Embeddings

    def __init__(self):
        self._embedding_container = NVIDIAEmbeddings(model="nvidia/nemotron-3.5-embed-8b", nvidia_api_key=os.getenv("NVIDIA_API_KEY"))

    def embed_query(self):
        raise NotImplementedError()

    def embed_documents(self):
        raise NotImplementedError()

    def get(self) -> Embeddings:
        return super().get()
