from fastapi import Request

from src.persistence.db.relational.conversation_repository import PostgresConversationRepository
from src.types.app_error import AppError
from src.types.dtos.create_conversation_request import UpdateConversationTitleRequest


class UpdateConversationTitleService:
    @classmethod
    def run(cls, conversation_id: str, dto: UpdateConversationTitleRequest, request: Request) -> dict[str, str]:
        repository = PostgresConversationRepository(request.app.state.conversation_pool)
        conversation = repository.get_by_id(conversation_id)
        if conversation is None:
            raise AppError('CONVERSATION_NOT_FOUND', 'The conversation was not found', 404)
        if conversation.sender_id != dto.owner_id:
            raise AppError('CONVERSATION_FORBIDDEN', 'The owner does not own this conversation', 403)
        updated = repository.update_title(conversation_id, dto.owner_id, dto.title)
        if updated is None:
            raise AppError('CONVERSATION_NOT_FOUND', 'The conversation was not found', 404)
        return {'conversation_id': updated.id, 'title': updated.title}
