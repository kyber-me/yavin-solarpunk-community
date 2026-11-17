from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings


class EmbeddingsModelIntegrationPort(ABC):

    _embedding_container: Embeddings


    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    def embed_query(self):
        ...

    @abstractmethod
    def embed_documents(self):
        ...

    @abstractmethod
    def get(self) -> Embeddings:
        return self._embedding_container








