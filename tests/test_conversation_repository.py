"""Run against an empty disposable DB explicitly provided in YAVIN_TEST_DB_URI."""
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier, local
from unittest.mock import patch
from uuid import uuid4

import psycopg
from psycopg.errors import UniqueViolation
from ulid import ULID

from src.infra.db.relational.conversation_pool import open_conversation_pool
from src.infra.db.relational.conversation_repository import (
    ActiveConversationExists,
    ConversationRecord,
    PostgresConversationRepository,
    conversation_lookup,
)


class LookupTests(unittest.TestCase):
    def test_unordered_and_unambiguous(self):
        self.assertEqual(conversation_lookup('A', 'B'), conversation_lookup('B', 'A'))
        self.assertNotEqual(conversation_lookup('A_B', 'C'), conversation_lookup('A', 'B_C'))
        self.assertEqual(conversation_lookup('é', 'A'), '["A","é"]')

    def test_invalid_participants(self):
        for pair in [('', 'B'), ('A', ' '), ('A', 'A')]:
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                conversation_lookup(*pair)

    def test_no_configuration_side_effect(self):
        with self.assertRaises(ValueError), open_conversation_pool(''):
            self.fail('An empty URI must fail before opening a connection')


@unittest.skipUnless(os.getenv('YAVIN_TEST_DB_URI'), 'Requires an empty disposable YAVIN_TEST_DB_URI')
class RepositoryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.uri = os.environ['YAVIN_TEST_DB_URI']
        migration = Path('src/infra/db/relational/migrations/001_create_conversations.sql').read_text()
        with psycopg.connect(cls.uri, autocommit=True) as connection:
            if connection.execute("SELECT to_regclass('yavin.conversations')").fetchone()[0] is not None:
                raise RuntimeError('Refusing to run: test DB must not already contain yavin.conversations')
            connection.execute(migration)

    def setUp(self):
        self.sender = 'test-' + str(uuid4())
        self.context = open_conversation_pool(self.uri)
        self.pool = self.context.__enter__()
        self.repo = PostgresConversationRepository(self.pool)
        self.addCleanup(self.context.__exit__, None, None, None)
        self.addCleanup(self.clean_records)

    def clean_records(self):
        with psycopg.connect(self.uri) as connection:
            connection.execute('DELETE FROM yavin.conversations WHERE sender_id = %s OR participant_id = %s',
                               (self.sender, self.sender))

    def record(self, participant='silas'):
        return ConversationRecord(
            id=f'Conv_{ULID()}', sender_id=self.sender, participant_id=participant,
            look_up_key=conversation_lookup(self.sender, participant), thread_id=str(ULID()),
            created_at=datetime.now(UTC),
        )

    def test_create_read_reconnect_and_isolate(self):
        first = self.record()
        second = self.record('other-agent')
        self.assertEqual(self.repo.create(first), first)
        self.repo.create(second)
        with open_conversation_pool(self.uri) as other_pool:
            other = PostgresConversationRepository(other_pool)
            self.assertEqual(other.get_by_id(first.id), first)
            self.assertEqual(other.get_active_by_lookup(second.look_up_key), second)
            self.assertIsNone(other.get_by_id('missing'))
        self.assertIsNotNone(self.repo.get_by_id(first.id).created_at.utcoffset())

    def test_reverse_pair_reports_existing(self):
        first = self.repo.create(self.record())
        other = replace(self.record(), sender_id=first.participant_id, participant_id=first.sender_id)
        with self.assertRaises(ActiveConversationExists) as caught:
            self.repo.create(other)
        self.assertEqual(caught.exception.conversation.id, first.id)

    def test_race_is_protected_by_database_and_pool_recovers(self):
        barrier = Barrier(2)
        thread = local()
        original_lookup = self.repo.get_active_by_lookup

        def simultaneous_lookup(key):
            result = original_lookup(key)
            if not getattr(thread, 'checked', False):
                thread.checked = True
                barrier.wait(timeout=5)
            return result

        def create(record):
            try:
                return self.repo.create(record).id
            except ActiveConversationExists as error:
                return error.conversation.id

        with patch.object(self.repo, 'get_active_by_lookup', side_effect=simultaneous_lookup):
            with ThreadPoolExecutor(max_workers=2) as executor:
                ids = list(executor.map(create, [self.record(), self.record()]))
        self.assertEqual(ids[0], ids[1])
        with psycopg.connect(self.uri) as connection:
            count = connection.execute('SELECT count(*) FROM yavin.conversations WHERE sender_id = %s',
                                       (self.sender,)).fetchone()[0]
        self.assertEqual(count, 1)
        self.assertEqual(self.repo.get_by_id(ids[0]).id, ids[0])

    def test_other_unique_violation_is_not_a_duplicate_conversation(self):
        first = self.repo.create(self.record())
        with self.assertRaises(UniqueViolation):
            self.repo.create(replace(self.record('other-agent'), thread_id=first.thread_id))
        self.assertIsNone(self.repo.get_active_by_lookup(conversation_lookup(self.sender, 'other-agent')))
        self.assertIsNotNone(self.repo.get_by_id(first.id))

    def test_reject_bad_lookup_and_naive_time_before_write(self):
        for record in [replace(self.record(), look_up_key='wrong'),
                       replace(self.record(), created_at=datetime(2026, 11, 7))]:
            with self.subTest(record=record), self.assertRaises(ValueError):
                self.repo.create(record)
            self.assertIsNone(self.repo.get_by_id(record.id))

    def test_inactive_history_does_not_block_new_active_conversation(self):
        first = self.repo.create(self.record())
        with psycopg.connect(self.uri) as connection:
            connection.execute('UPDATE yavin.conversations SET active = FALSE, end_date = now() WHERE id = %s', (first.id,))
        second = self.repo.create(self.record())
        self.assertNotEqual(first.id, second.id)
        self.assertFalse(self.repo.get_by_id(first.id).active)

    def test_connection_is_returned_before_agent_work(self):
        self.repo.create(self.record())
        with psycopg.connect(self.uri) as connection:
            row = connection.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() AND state = 'idle in transaction'").fetchone()
        self.assertEqual(row[0], 0)
        self.assertEqual(self.pool.get_stats()['requests_waiting'], 0)


if __name__ == '__main__':
    unittest.main()
