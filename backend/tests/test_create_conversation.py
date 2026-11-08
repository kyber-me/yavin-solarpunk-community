"""Creation HTTP contract, with repository results controlled and no lifespan."""
import unittest
from datetime import UTC, datetime
from unittest.mock import patch

from fastapi.testclient import TestClient
from psycopg.errors import UniqueViolation
from ulid import ULID

from main import app
from src.infra.db.relational.conversation_record import ConversationRecord
from src.infra.db.relational.conversation_repository import ActiveConversationExists


class CreateConversationTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(app.state, 'conversation_pool', object(), create=True))
        self.repository = self.enterContext(patch(
            'src.services.create_conversation_service.PostgresConversationRepository'
        )).return_value

    def test_creation_returns_201_with_server_metadata_and_plain_ulid(self):
        self.repository.create.side_effect = lambda record: record
        response = TestClient(app).post('/conversation/create', json={
            'sender_id': 'idealizador', 'participant_id': 'silas',
        })
        self.assertEqual(response.status_code, 201)
        saved = self.repository.create.call_args.args[0]
        self.assertEqual(str(ULID.from_str(saved.id)), saved.id)
        self.assertEqual(response.json(), {'data': {
            'conversation_id': saved.id, 'participant_id': 'silas',
            'created_at': saved.created_at.isoformat(),
        }, 'error': None})

    def test_duplicate_returns_existing_metadata_in_either_pair_orientation(self):
        for sender, participant in [('idealizador', 'silas'), ('silas', 'idealizador')]:
            with self.subTest(sender=sender, participant=participant):
                existing = ConversationRecord(id=str(ULID()), sender_id=sender, participant_id=participant,
                                              thread_id=str(ULID()), created_at=datetime.now(UTC))
                self.repository.create.side_effect = ActiveConversationExists(existing)
                response = TestClient(app).post('/conversation/create', json={
                    'sender_id': 'idealizador', 'participant_id': 'silas',
                })
                self.assertEqual(response.status_code, 409)
                body = response.json()
                self.assertIsNone(body['data'])
                self.assertEqual(body['error']['code'], 'CONVERSATION_ALREADY_ACTIVE')
                self.assertEqual(body['error']['details'], {
                    'conversation_id': existing.id, 'participant_id': 'silas',
                    'created_at': existing.created_at.isoformat(),
                })
                self.assertNotIn('thread_id', body['error']['details'])

    def test_other_unique_violation_is_not_translated_to_active_pair_conflict(self):
        self.repository.create.side_effect = UniqueViolation('other index')
        response = TestClient(app, raise_server_exceptions=False).post('/conversation/create', json={
            'sender_id': 'idealizador', 'participant_id': 'silas',
        })
        self.assertEqual(response.status_code, 500)

    def test_unavailable_participant_rejected_before_ids_or_repository(self):
        for participant in ('unknown', '', ' ', 'Silas', 'silas '):
            with self.subTest(participant=participant), patch(
                'src.services.create_conversation_service.PostgresConversationRepository'
            ) as repository, patch('src.services.create_conversation_service.ULID') as ulid:
                response = TestClient(app).post('/conversation/create', json={
                    'sender_id': 'idealizador', 'participant_id': participant,
                })
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()['error']['code'], 'AGENT_UNAVAILABLE')
                self.assertIsNone(response.json()['data'])
                repository.assert_not_called()
                ulid.assert_not_called()

    def test_discovery_and_creation_follow_the_same_catalog(self):
        self.repository.create.side_effect = lambda record: record
        with patch('src.services.agent_catalog._AVAILABLE_AGENTS', (('test-agent', 'Test agent'),)):
            catalog = TestClient(app).get('/agents').json()['data']['agents']
            self.assertEqual(catalog, [{'id': 'test-agent', 'name': 'Test agent'}])
            accepted = TestClient(app).post('/conversation/create', json={
                'sender_id': 'idealizador', 'participant_id': catalog[0]['id'],
            })
            self.assertEqual(accepted.status_code, 201)
            self.assertEqual(accepted.json()['data']['participant_id'], 'test-agent')
            rejected = TestClient(app).post('/conversation/create', json={
                'sender_id': 'idealizador', 'participant_id': 'silas',
            })
            self.assertEqual(rejected.status_code, 422)
            self.assertEqual(self.repository.create.call_count, 1)


if __name__ == '__main__':
    unittest.main()
