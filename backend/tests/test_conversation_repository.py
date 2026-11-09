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
)


class PoolConfigurationTests(unittest.TestCase):
    def test_no_configuration_side_effect(self):
        with self.assertRaises(ValueError), open_conversation_pool(''):
            self.fail('An empty URI must fail before opening a connection')


@unittest.skipUnless(os.getenv('YAVIN_TEST_DB_URI'), 'Requires an empty disposable YAVIN_TEST_DB_URI')
class RepositoryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.uri = os.environ['YAVIN_TEST_DB_URI']
        with psycopg.connect(cls.uri, autocommit=True) as connection:
            if connection.execute("SELECT to_regclass('yavin.conversations')").fetchone()[0] is not None:
                raise RuntimeError('Refusing to run: test DB must not already contain yavin.conversations')
            for name in ('001_initial_schema.sql', '002_agents_documents.sql'):
                connection.execute(Path('src/persistence/db/relational/migrations', name).read_text())
            cls.legacy_agent_id = str(ULID())
            cls.legacy_conversation_id = str(ULID())
            connection.execute('INSERT INTO yavin.agents (id, name) VALUES (%s, %s)', (cls.legacy_agent_id, 'Agente legado'))
            connection.execute(
                'INSERT INTO yavin.conversations (id, sender_id, participant_id, thread_id, created_at) '
                'VALUES (%s, %s, %s, %s, %s)',
                (cls.legacy_conversation_id, 'legacy-owner', cls.legacy_agent_id, str(ULID()), datetime.now(UTC)),
            )
            connection.execute(Path('src/persistence/db/relational/migrations/004_conversation_title.sql').read_text())

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
            id=str(ULID()), sender_id=self.sender, participant_id=participant,
            thread_id=str(ULID()),
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
            self.assertEqual(other.get_active_by_participants(second.sender_id, second.participant_id), second)
            self.assertIsNone(other.get_by_id('missing'))
        self.assertIsNotNone(self.repo.get_by_id(first.id).created_at.utcoffset())

    def test_migration_backfills_legacy_title_and_update_persists(self):
        self.assertEqual(self.repo.get_by_id(self.legacy_conversation_id).title, 'Conversa com Agente legado')
        record = self.repo.create(replace(self.record(), title='Pesquisa inicial'))
        updated = self.repo.update_title(record.id, self.sender, 'Pesquisa solar')
        self.assertEqual(updated.title, 'Pesquisa solar')
        self.assertEqual(self.repo.get_by_id(record.id).title, 'Pesquisa solar')
        self.assertIsNone(self.repo.update_title(record.id, 'other-owner', 'Indevido'))

    def test_reverse_pair_reports_existing(self):
        first = self.repo.create(self.record())
        other = replace(self.record(), sender_id=first.participant_id, participant_id=first.sender_id)
        with self.assertRaises(ActiveConversationExists) as caught:
            self.repo.create(other)
        self.assertEqual(caught.exception.conversation.id, first.id)

    def test_race_is_protected_by_database_and_pool_recovers(self):
        barrier = Barrier(2)
        thread = local()
        original_lookup = self.repo.get_active_by_participants

        def simultaneous_lookup(sender, participant):
            result = original_lookup(sender, participant)
            if not getattr(thread, 'checked', False):
                thread.checked = True
                barrier.wait(timeout=5)
            return result

        def create(record):
            try:
                return self.repo.create(record).id
            except ActiveConversationExists as error:
                return error.conversation.id

        with patch.object(self.repo, 'get_active_by_participants', side_effect=simultaneous_lookup):
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
        self.assertIsNone(self.repo.get_active_by_participants(self.sender, 'other-agent'))
        self.assertIsNotNone(self.repo.get_by_id(first.id))

    def test_reject_bad_participants_and_naive_time_before_write(self):
        for record in [replace(self.record(), participant_id=self.sender),
                       replace(self.record(), participant_id=' '),
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

    def test_database_rejects_reverse_pair_without_repository_check(self):
        first = self.repo.create(self.record())
        with self.assertRaises(UniqueViolation) as caught:
            with psycopg.connect(self.uri) as connection:
                connection.execute(
                    "INSERT INTO yavin.conversations "
                    "(id, sender_id, participant_id, thread_id, created_at, title) VALUES (%s, %s, %s, %s, %s, %s)",
                    (str(ULID()), first.participant_id, first.sender_id, str(ULID()), first.created_at, 'Teste'),
                )
        self.assertEqual(caught.exception.diag.constraint_name, 'conversations_active_pair_uq')

    def test_connection_is_returned_before_agent_work(self):
        self.repo.create(self.record())
        with psycopg.connect(self.uri) as connection:
            row = connection.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() AND state = 'idle in transaction'").fetchone()
        self.assertEqual(row[0], 0)
        self.assertEqual(self.pool.get_stats()['requests_waiting'], 0)


if __name__ == '__main__':
    unittest.main()
