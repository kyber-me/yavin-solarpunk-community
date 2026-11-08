"""Message adaptation and persistence; DB tests require a fresh disposable database."""
import os
import unittest
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from pydantic import ValidationError
from ulid import ULID

from src.infra.db.relational.conversation_pool import open_conversation_pool
from src.infra.db.relational.conversation_record import ConversationRecord
from src.infra.db.relational.conversation_repository import PostgresConversationRepository
from src.infra.db.relational.message_repository import PostgresMessageRepository
from src.services.message_mapper import message_from_record, message_to_record
from src.types.dtos.chat_service_request import Message


class MessageMappingTests(unittest.TestCase):
    def test_round_trip_preserves_identity_dates_and_context(self):
        message = Message(content='Olá', updated_at=datetime.now(UTC), deleted_at=datetime.now(UTC))
        record = message_to_record(message, conversation_id='Conv_test', sender_id='silas')
        self.assertEqual((record.conversation_id, record.sender_id), ('Conv_test', 'silas'))
        self.assertEqual(message_from_record(record), message)
        self.assertIsNotNone(record.created_at.utcoffset())

    def test_naive_timestamps_are_rejected_by_model(self):
        for name in ('created_at', 'updated_at', 'deleted_at'):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                Message.model_validate({'content': 'Olá', name: datetime(2026, 11, 7)})

    def test_invalid_records_rejected_before_borrowing_connection(self):
        repository = PostgresMessageRepository(None)  # type: ignore[arg-type]
        record = message_to_record(Message(content='Olá'), conversation_id='Conv_test', sender_id='silas')
        for invalid in (replace(record, content=' \n\t'), replace(record, sender_id=''),
                        replace(record, created_at=datetime(2026, 11, 7))):
            with self.subTest(record=invalid), self.assertRaises(ValueError):
                repository.create(invalid)
        with self.assertRaises(ValueError):
            repository.list_by_conversation('Conv_test', limit=0)


@unittest.skipUnless(os.getenv('YAVIN_TEST_DB_URI'), 'Requires fresh disposable YAVIN_TEST_DB_URI')
class MessageRepositoryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.uri = os.environ['YAVIN_TEST_DB_URI']
        with psycopg.connect(cls.uri, autocommit=True) as connection:
            if connection.execute("SELECT to_regclass('yavin.conversations')").fetchone()[0] is not None:
                raise RuntimeError('Refusing to run: test database must be empty')
            connection.execute(Path('src/infra/db/relational/migrations/001_initial_schema.sql').read_text())

    def setUp(self):
        self.context = open_conversation_pool(self.uri)
        self.pool = self.context.__enter__()
        self.addCleanup(self.context.__exit__, None, None, None)
        self.conversations = PostgresConversationRepository(self.pool)
        self.messages = PostgresMessageRepository(self.pool)
        self.conversation = self.conversations.create(ConversationRecord(
            id=str(ULID()), sender_id=str(uuid4()), participant_id='silas', thread_id=str(ULID()),
        ))
        self.addCleanup(self.clean_records)

    def clean_records(self):
        with psycopg.connect(self.uri) as connection:
            connection.execute('DELETE FROM yavin.messages WHERE conversation_id = %s', (self.conversation.id,))
            connection.execute('DELETE FROM yavin.conversations WHERE id = %s', (self.conversation.id,))

    def record(self, content='Olá'):
        return message_to_record(Message(content=content), conversation_id=self.conversation.id,
                                 sender_id=self.conversation.sender_id)

    def test_create_read_reconnect_and_preserve_conversation_row_factory(self):
        record = self.record()
        self.assertEqual(self.messages.create(record), record)
        self.assertIsInstance(self.conversations.get_by_id(self.conversation.id), ConversationRecord)
        with open_conversation_pool(self.uri) as pool:
            repository = PostgresMessageRepository(pool)
            self.assertEqual(repository.get_by_id(record.id), record)
            self.assertIsNone(repository.get_by_id('missing'))

    def test_order_limit_and_conversation_isolation(self):
        timestamp = datetime.now(UTC)
        records = [replace(self.record(str(index)), id=f"{index:026d}", created_at=timestamp + timedelta(seconds=index // 2))
                   for index in (3, 1, 2, 0)]
        for record in records:
            self.messages.create(record)
        self.assertEqual([record.id for record in self.messages.list_by_conversation(self.conversation.id, limit=3)],
                         [f"{index:026d}" for index in (0, 1, 2)])
        self.assertEqual(self.messages.list_by_conversation('missing'), [])

    def test_duplicate_id_rolls_back_and_pool_remains_usable(self):
        record = self.messages.create(self.record())
        with self.assertRaises(UniqueViolation):
            self.messages.create(record)
        self.assertEqual(self.messages.get_by_id(record.id), record)
        self.assertEqual(self.pool.get_stats()['requests_waiting'], 0)

    def test_foreign_key_rejects_missing_conversation(self):
        with self.assertRaises(ForeignKeyViolation):
            self.messages.create(replace(self.record(), conversation_id='missing'))
        self.assertEqual(self.messages.list_by_conversation(self.conversation.id), [])

    def test_metadata_round_trip_and_connection_returned(self):
        record = replace(self.record(), updated_at=datetime.now(UTC), deleted_at=datetime.now(UTC))
        self.assertEqual(self.messages.create(record), record)
        with psycopg.connect(self.uri) as connection:
            self.assertEqual(connection.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() AND state = 'idle in transaction'"
            ).fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
