"""Explicit adaptation between the message model and persistence data."""
from src.infra.db.relational.message_record import MessageRecord
from src.types.dtos.send_message_service_request import Message


# Usamos "*" isso porque conversation_id e sender_id são ambos strings:
# exigir seus nomes torna a chamada mais legível e reduz o risco de inverter os valores.
def message_to_record(
    message: Message, *, conversation_id: str, sender_id: str
) -> MessageRecord:
    return MessageRecord(
        id=message.id,
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=message.content,
        created_at=message.created_at,
        updated_at=message.updated_at,
        deleted_at=message.deleted_at,
    )


def message_from_record(record: MessageRecord) -> Message:
    return Message(
        id=record.id,
        content=record.content,
        created_at=record.created_at,
        updated_at=record.updated_at,
        deleted_at=record.deleted_at,
    )
