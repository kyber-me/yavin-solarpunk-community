from langchain_core.embeddings import Embeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from src.ports import EmbeddingsModelIntegrationPort


class OpenAiEmbeddings(EmbeddingsModelIntegrationPort):

    def get_embeddings_size(self, text: str) -> int:
        return super().get_embeddings_size(text)

    _embedding_container: Embeddings

    def __init__(self):
        self._embedding_container = OpenAIEmbeddings(model="text-embedding-3-small")

    def embed_query(self, text: str) -> list[float | int]:
        return super().embed_query(text)

    def embed_documents(self):
        raise NotImplementedError()

    def get(self) -> Embeddings:
        return super().get()

