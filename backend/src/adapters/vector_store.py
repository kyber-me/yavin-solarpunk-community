from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from src.ports import EmbeddingsModelIntegrationPort
# from src.adapters import OpenAiEmbeddingsAdapter

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
    _store: QdrantVectorStore
    embeddings: EmbeddingsModelIntegrationPort


    def __init__(self, embeddings: EmbeddingsModelIntegrationPort, collection: str = "library_sec_001") -> None:
        self._client = QdrantClient(
            url="http://localhost:6333",
        )
        self.embeddings = embeddings
        self.setup(init_collection=collection)

    def setup(self, init_collection: str):
        print("Initializing QdrantVectorStore setup...")

        collection = init_collection
        already_exists = False
        try:
            # Verifica se coleção inicial já existe. Isto não quer dizer que os
            # documentos tenham sido carregados
            if self._client:
                # Não usa a conexão com a Nvidia
                # A conexão com a Nvidia é importante para usar o modelo
                # de embeddings
                already_exists = self._client.collection_exists(collection)
            else:
                raise ValueError("Qdrant client is not initialized")

            print("Already exists: ", already_exists, end="\n\n")

            # Caso a coleção não exista, cria a coleção inicial
            size = self.embeddings.get_embeddings_size("Lorem ipsum dolor sit amet")
            print(f"Embedding size: {size}")
            if not already_exists:
                created = self._client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=size, distance=Distance.COSINE)
                )

                # Pensar em arquitetura resiliente para a criação da coleção
                if not created:
                    print("Error creating QdrantVectorStore")
                    raise IOError("Error creating QdrantVectorStore")

                # Aqui o algoritmo continua para a preparação/ chunking dos documentos
                text_splitter = (RecursiveCharacterTextSplitter
                    .from_tiktoken_encoder(chunk_size=500, chunk_overlap=50))
                docs_splits = text_splitter.split_documents(BASE_DOCUMENTS)

                # Always instantiate the QdrantVectorStore abstraction
                # It's crucial to keep an instance of QdrantVectorStore?
                self._store = QdrantVectorStore(
                    client=self._client,
                    collection_name=collection,
                    embedding=self.embeddings.get()
                )
                ids = self._store.add_documents(docs_splits) if self._store else []
                print(ids, end="\n\n")

            # Caso a coleção já exista, instanciar um container QdrantVectorStore
            # É necessário garantir que os documentos iniciais já foram adicionados
            # A coleção inicial deve servir como "prova" da existência dos
            # documentos para a base fundamental de conhecimento
            else:
                # Sempre instanciar um QdrantVectorStore no setup da classe
                # Isto é crucial? Acho que sim
                self._store = QdrantVectorStore(
                    client=self._client,
                    collection_name=collection,
                    embedding=self.embeddings.get()
                )

                has_documents = self._client.count(collection_name=collection, exact=True).count > 0
                print(f"Has documents: {has_documents}")
                if not has_documents:
                    print("No documents found")

                    # Aqui o algoritmo continua para a preparação/ chunking dos documentos
                    text_splitter = (RecursiveCharacterTextSplitter
                        .from_tiktoken_encoder(chunk_size=500, chunk_overlap=50))
                    docs_splits = text_splitter.split_documents(BASE_DOCUMENTS)

                    ids = self._store.add_documents(docs_splits) if self._store else []
                    print(ids, end="\n\n")
        except (IOError or ValueError) as e:
            print(f"Error setting up QdrantVectorStore: {e}")
        except Exception as e:
            print(f"Error setting up QdrantVectorStore: {e}")
            # self._client.delete_collection(collection)


    def create_vector(self,
        docs: list[Document],
        distance: Distance | None = None,
        collection: str | None = None
    ) -> list[str]:
        try:
            if collection is not None and distance is not None:
                # created?
                _ = self.create_collection(collection, distance)
                self._store.collection_name = collection

            ids = self._store.add_documents(docs) if self._store else []
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
                    vectors_config=VectorParams(size=self.embeddings_size, distance=distance)
                )
        else:
            raise ValueError("Qdrant client is not initialized")
        return created


    def collection_exists(self, name: str) -> bool:
        if self._client:
            return self._client.collection_exists(name)
        else:
            raise ValueError("Qdrant client is not initialized")


    def get_retriever(self) -> BaseRetriever:
        """Create a retriever that searches this Qdrant vector store.

        Returns:
            A LangChain retriever configured for similarity search.

        Raises:
            ValueError: If no Qdrant vector store has been initialized.
        """
        if not hasattr(self, "_store"):
            raise ValueError("Qdrant vector store is not initialized")

        return self._store.as_retriever()
