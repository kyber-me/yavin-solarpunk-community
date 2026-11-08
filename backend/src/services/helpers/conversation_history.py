"""Read persisted conversations and authorize access to their messages."""
from fastapi import Request

from src.infra.db.relational.conversation_repository import PostgresConversationRepository
from src.infra.db.relational.message_repository import PostgresMessageRepository
from src.services.agent_catalog_service import get_agent_catalog
from src.types.app_error import AppError
from src.types.dtos.conversation_history import (
    ConversationPage, ConversationSummary, MessagePage, StoredMessage,
)


def list_conversations(request: Request, sender_id: str, limit: int, offset: int) -> ConversationPage:
    repository = PostgresConversationRepository(request.app.state.conversation_pool)
    records = repository.list_by_participant(sender_id, limit=limit + 1, offset=offset)
    names = {agent.id: agent.name for agent in get_agent_catalog().agents}
    summaries: list[ConversationSummary] = []
    for record in records[:limit]:
        other = record.participant_id if record.sender_id == sender_id else record.sender_id
        summaries.append(ConversationSummary(
            conversation_id=record.id, participant_id=other, participant_name=names.get(other, other),
            created_at=record.created_at, active=record.active,
        ))
    return ConversationPage(conversations=summaries,
                            next_offset=offset + limit if len(records) > limit else None)


def list_messages(request: Request, conversation_id: str, sender_id: str, limit: int, offset: int) -> MessagePage:
    pool = request.app.state.conversation_pool
    conversation = PostgresConversationRepository(pool).get_by_id(conversation_id)
    if conversation is None:
        raise AppError('CONVERSATION_NOT_FOUND', 'The conversation was not found', 404)
    if sender_id not in (conversation.sender_id, conversation.participant_id):
        raise AppError('CONVERSATION_FORBIDDEN', 'The sender does not participate in this conversation', 403)
    records = PostgresMessageRepository(pool).list_by_conversation(conversation_id, limit=limit + 1, offset=offset)
    return MessagePage(messages=[StoredMessage(
        id=record.id, sender_id=record.sender_id, content=record.content, created_at=record.created_at,
    ) for record in records[:limit] if record.deleted_at is None],
        next_offset=offset + limit if len(records) > limit else None)
