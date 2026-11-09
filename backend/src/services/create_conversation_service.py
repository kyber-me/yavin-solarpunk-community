from typing import Any

from ulid import ULID
from fastapi import Request

from src.services.service_interface import IService
from src.services.agent_catalog_service import is_agent_available
from src.types.dtos.create_conversation_request import CreateConversationRequest
from src.types.app_error import AppError

from src.persistence.db.relational.conversation_repository import (
    ActiveConversationExists, PostgresConversationRepository, ConversationRecord,
)


class CreateConversationService(IService):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def run(
        cls, dto: CreateConversationRequest, request: Request
    ) -> dict[str, Any]:
        if not is_agent_available(dto.conversation_details.participant_id, request.app.state.conversation_pool):
            raise AppError(
                code="AGENT_UNAVAILABLE",
                message="The selected participant is not available",
                status_code=422,
            )
        conversation_record = ConversationRecord(
            id=str(ULID()),
            sender_id=dto.owner_id,
            participant_id=dto.conversation_details.participant_id,
            thread_id=str(ULID()),
            title=dto.conversation_details.title,
        )

        result: ConversationRecord
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
                    "participant_id": dto.conversation_details.participant_id,
                    "created_at": existing.created_at.isoformat(),
                    "title": existing.title,
                },
            ) from error

        return {
            "conversation_id": result.id,
            "participant_id": result.participant_id,
            "created_at": result.created_at.isoformat(),
            "title": result.title,
        }


