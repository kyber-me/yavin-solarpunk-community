# from langgraph.checkpoint.postgres import PostgresSaver
from typing import Any

from ulid import ULID
from fastapi import Request

from src.services.service_interface import IService
from src.services.agent_catalog import is_agent_available
from src.types.dtos.create_conversation_request import CreateConversationRequest
from src.types.app_error import AppError

from src.infra.db.relational.conversation_repository import (
    ActiveConversationExists, PostgresConversationRepository, ConversationRecord,
)


class CreateConversationService(IService):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def run(
        cls, dto: CreateConversationRequest, request: Request
    ) -> dict[str, Any]:
        if not is_agent_available(dto.participant_id):
            raise AppError(
                code="AGENT_UNAVAILABLE",
                message="The selected participant is not available",
                status_code=422,
            )
        conversation_record = ConversationRecord(
            id=str(ULID()),
            sender_id=dto.sender_id,
            participant_id=dto.participant_id,
            thread_id=str(ULID())
        )

        result: ConversationRecord

        # Still does not understand exactly what it does under hood, even after
        # explanation in the codex chat
        pool = request.app.state.conversation_pool

        # Still not DI (!)
        conversation_repo = PostgresConversationRepository(pool)
        try:
            result = conversation_repo.create(conversation_record)
        except ActiveConversationExists as error:
            existing = error.conversation
            raise AppError(
                code="CONVERSATION_ALREADY_ACTIVE",
                message="An active conversation already exists for these participants",
                status_code=409,
                details={
                    "conversation_id": existing.id,
                    "participant_id": dto.participant_id,
                    "created_at": existing.created_at.isoformat(),
                },
            ) from error

        # return {
        #     "id": result.id,
        #     "sender_id": result.sender_id,
        #     "participant_id": result.participant_id,
        #     "active": result.active,
        #     "thread_id": result.thread_id,
        # }

        # "look_up_key": result.look_up_key,  # Do I'm going to need this information at Frontend?
        # Don't think so. I can always build the `look_up_key` based on the sender id and the participant id to verify if exists a conversation on going.
        # Actually, I don't need even to persist this key at all. I can just use it as a runtime verification. (?)
        return {
            "conversation_id": result.id,
            "participant_id": result.participant_id,
            "created_at": result.created_at.isoformat(),
        }


