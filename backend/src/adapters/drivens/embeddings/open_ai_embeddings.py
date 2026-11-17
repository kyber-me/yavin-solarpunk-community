from langchain_core.embeddings import Embeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from src.ports import EmbeddingsModelIntegrationPort


class OpenAiEmbeddings(EmbeddingsModelIntegrationPort):

    _embedding_container: Embeddings

    def __init__(self):
        self._embedding_container = OpenAIEmbeddings(model="text-embedding-3-small")

    def embed_query(self):
        raise NotImplementedError()

    def embed_documents(self):
        raise NotImplementedError()

    def get(self) -> Embeddings:
        return super().get()

