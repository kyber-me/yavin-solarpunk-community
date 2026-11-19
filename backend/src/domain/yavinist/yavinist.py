from typing import Any

from dotenv import load_dotenv

from src.constants import PROJECT_ROOT
load_dotenv(PROJECT_ROOT / ".env")
# from ulid import ULID

from langgraph.store.base import BaseStore
from langgraph.types import Checkpointer

from src.domain.yavinist.role_dto import roleDTO
from src.adapters import (
    LangchainAgentContainer,
    LangchainAgentContainerOptions,
    QdrantVectorStoreContainer
)


class Yavinist:
    id: str
    roles: list[roleDTO]
    name: str
    agent: LangchainAgentContainer

    def __init__(self,
        vector_database: QdrantVectorStoreContainer,
        checkpointer: Checkpointer,
        store: BaseStore,
        roles: list[roleDTO],
        *,
        unique_identifier: str, # Investigate it
        name: str,
        identity_prompt: str, # Is that really necessary?
    ) -> None:
        self.id = unique_identifier #or str(ULID())
        self.roles = roles
        self.name = name
        self.agent = LangchainAgentContainer(
            name.lower(),
            roles,
            LangchainAgentContainerOptions(
                checkpointer=checkpointer,
                store=store,
                retriever=vector_database.get_retriever(),
                identity_prompt=identity_prompt
            )
        )


    def send_message(self, message: str, thread_id: str | None) -> dict[str, Any]:
        if not thread_id:
            raise ValueError("thread_id is required")

        return self.agent.invoke(message, thread_id, [])
