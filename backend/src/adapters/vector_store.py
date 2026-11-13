from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
# from langchain_core.retrievers import BaseRetriever

from src.ports import EmbeddingsModelIntegrationPort
from src.adapters import OpenAiEmbedding as OpenAIEmbeddingsModelIntegrationAdapter


class QdrantVectorStoreContainer:

    client: QdrantClient
    store: QdrantVectorStore
    embeddings: EmbeddingsModelIntegrationPort

    def __init__(self):
        self.embeddings = OpenAIEmbeddingsModelIntegrationAdapter()
        self.setup()

    def setup(self) -> bool:
        try:
            self.client = QdrantClient(":memory:")

            self.create_collection("default", Distance.COSINE)

            self.store = QdrantVectorStore(
                client=self.client,
                collection_name="default",
                embedding=self.embeddings.get_embedding_container()
            )
        except Exception as e:
            print(f"Error setting up QdrantVectorStore: {e}")
            return False

        return True


    # Distance.COSINE
    def create_collection(self, name: str, distance: Distance):
        if self.client:
            if not self.client.collection_exists(name):
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=1536, distance=distance)
                )
        else:
            raise ValueError("Qdrant client is not initialized")