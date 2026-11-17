from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.documents import Document
# from langchain_core.retrievers import BaseRetriever

from src.ports import EmbeddingsModelIntegrationPort
from src.adapters import OpenAiEmbeddingsAdapter

from src.constants import BASE_KNOWLEDGE_PATH

BASE_DOCUMENTS = [
    Document(
        page_content=Path(BASE_KNOWLEDGE_PATH / "institutional" / "YAVIN_RESEARCH_PROJECT.md").read_text(),
        metadata={}
    ),
    Document(
        page_content=Path(BASE_KNOWLEDGE_PATH / "library" / "JUGAAD.md").read_text(),
        metadata={}
    ),
    Document(
        page_content=Path(BASE_KNOWLEDGE_PATH / "library" / "SOLARPUNK_MANIFESTO.md").read_text(),
        metadata={}
    ),
    Document(
        page_content=Path(BASE_KNOWLEDGE_PATH / "library" / "SWADESHI.md").read_text(),
        metadata={}
    )
]

# I want to run Qdrant locally and to have an interface to understand what is going on
class QdrantVectorStoreContainer:
    _client: QdrantClient
    store: QdrantVectorStore
    embeddings: EmbeddingsModelIntegrationPort

    def __init__(self, embeddings: EmbeddingsModelIntegrationPort, collection: str = "library_sec_001") -> None:
        self._client = QdrantClient(
            url="http://localhost:6333",
        )
        self.embeddings = embeddings
        self.setup(init_collection=collection)

    def setup(self, init_collection: str):
        # Create the standard base knowledge library for the agents to consume
        # if it not exists
        collection = init_collection
        try:
            exists = False
            if self._client:
                exists = self._client.collection_exists(collection)
            else:
                raise ValueError("Qdrant client is not initialized")
            if not exists:
                created = self._client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=4096, distance=Distance.COSINE)
                )

                if not created:
                    print("Error creating QdrantVectorStore")
                    return

                text_splitter = (RecursiveCharacterTextSplitter
                    .from_tiktoken_encoder(chunk_size=500, chunk_overlap=50))
                docs_splits = text_splitter.split_documents(BASE_DOCUMENTS)

                # Always instantiate the QdrantVectorStore abstraction
                # It's crucial to keep an instance of QdrantVectorStore?
                self.store = QdrantVectorStore(
                    client=self._client,
                    collection_name=collection,
                    embedding=self.embeddings.get()
                )
                ids = self.store.add_documents(docs_splits) if self.store else []
                print(ids, end="\n\n")
            else:
                # Always instantiate the QdrantVectorStore abstraction
                # It's crucial to keep an instance of QdrantVectorStore?
                self.store = QdrantVectorStore(
                    client=self._client,
                    collection_name=collection,
                    embedding=self.embeddings.get()
                )
        except Exception as e:
            print(f"Error setting up QdrantVectorStore: {e}")
            self._client.delete_collection(collection)



    def create_vector(self,
        docs: list[Document],
        distance: Distance | None = None,
        collection: str | None = None
    ) -> list[str]:
        try:
            if collection is not None and distance is not None:
                # created?
                _ = self.create_collection(collection, distance)
                self.store.collection_name = collection

            ids = self.store.add_documents(docs) if self.store else []
            return ids
        except Exception as e:
            print(f"Error creating QdrantVectorStore: {e}")

        return []


    def create_collection(self, name: str, distance: Distance) -> bool:
        created: bool = False
        if self._client:
            if not self._client.collection_exists(name):
                created = self._client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=768, distance=distance)
                )
        else:
            raise ValueError("Qdrant client is not initialized")
        return created


    def collection_exists(self, name: str) -> bool:
        if self._client:
            return self._client.collection_exists(name)
        else:
            raise ValueError("Qdrant client is not initialized")
