from langgraph.types import Checkpointer
from langgraph.store.base import BaseStore
from pydantic import BaseModel

from adapters import QdrantVectorStoreContainer


class FactoryDTO(BaseModel):
    id: str
    vector_database: QdrantVectorStoreContainer
    checkpointer: Checkpointer
    store: BaseStore
    identity_prompt: str
