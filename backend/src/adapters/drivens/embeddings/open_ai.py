from langchain_core.embeddings import Embeddings

from langchain_openai.embeddings import OpenAIEmbeddings

from src.ports import EmbeddingsModelIntegrationPort


class OpenAiEmbedding(EmbeddingsModelIntegrationPort):

    _embedding_container: Embeddings

    def __init__(self):
        self._embedding_container = OpenAIEmbeddings()

    def embed_query(self):
        raise NotImplementedError()

    def embed_documents(self):
        raise NotImplementedError()

    def get_embedding_container(self) -> Embeddings:
        return super().get_embedding_container()

