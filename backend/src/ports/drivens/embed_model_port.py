
from abc import ABC, abstractmethod

from langchain_core.embeddings import Embeddings

from ports import AiModelPort


class EmbeddingsModelIntegrationPort(ABC):

    _embedding_container: Embeddings


    @abstractmethod
    def __init__(self, model_adapter: AiModelPort):
        ...

    @abstractmethod
    def embed_query(self):
        ...

    @abstractmethod
    def embed_documents(self):
        ...

    @abstractmethod
    def get_embedding_container(self) -> Embeddings:
        return self._embedding_container








