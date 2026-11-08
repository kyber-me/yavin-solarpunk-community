"""HTTP request contract and server-owned message metadata, without DB or model."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from main import app
from src.services.chat_service import ChatService
from src.types.dtos.chat_service_request import ChatServiceRequest, Message


class ChatRequestTests(unittest.TestCase):
    def test_frontend_payload_reaches_service_with_request(self):
        # No TestClient context: do not execute the database lifespan.
        with patch('main.ChatService.run', return_value={'content': 'Resposta'}) as run:
            response = TestClient(app).post('/conversation/talk', json={
                'conversation_id': 'Conv_test', 'sender_id': 'idealizador', 'message': 'Olá',
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'], {'content': 'Resposta'})
        dto, request = run.call_args.args
        self.assertIsInstance(dto, ChatServiceRequest)
        self.assertEqual(dto.message, 'Olá')
        self.assertIsInstance(request, Request)
        self.assertIs(request.app, app)

    def test_client_cannot_supply_message_metadata_instead_of_text(self):
        with patch('main.ChatService.run') as run:
            response = TestClient(app).post('/conversation/talk', json={
                'conversation_id': 'Conv_test', 'sender_id': 'idealizador',
                'message': {'id': 'client-id', 'content': 'Olá', 'created_at': '2000-01-01T00:00:00Z'},
            })
        self.assertEqual(response.status_code, 422)
        run.assert_not_called()

    def test_service_builds_message_before_mapping(self):
        application = FastAPI()
        application.state.conversation_pool = object()
        request = Request({'type': 'http', 'app': application})
        dto = ChatServiceRequest(conversation_id='Conv_test', sender_id='idealizador', message='Olá')
        # Stop at the adaptation boundary to isolate this stage from persistence.
        with patch('src.services.chat_service.PostgresConversationRepository') as repository, patch(
            'src.services.chat_service.message_to_record', side_effect=RuntimeError('adaptation boundary')
        ) as mapper:
            repository.return_value.get_by_id.return_value = SimpleNamespace(
                sender_id='idealizador', participant_id='silas', active=True,
            )
            with self.assertRaisesRegex(RuntimeError, 'adaptation boundary'):
                ChatService.run(dto, request)
        message = mapper.call_args.args[0]
        self.assertIsInstance(message, Message)
        self.assertEqual(message.content, 'Olá')
        self.assertTrue(message.id)
        self.assertIsNotNone(message.created_at.utcoffset())
        self.assertEqual(mapper.call_args.kwargs,
                         {'conversation_id': 'Conv_test', 'sender_id': 'idealizador'})

    def test_conversation_errors_reach_http_before_message_or_agent_work(self):
        cases = [
            (None, 404, 'CONVERSATION_NOT_FOUND'),
            (SimpleNamespace(sender_id='other', participant_id='silas', active=True),
             403, 'CONVERSATION_FORBIDDEN'),
            (SimpleNamespace(sender_id='idealizador', participant_id='silas', active=False),
             409, 'CONVERSATION_INACTIVE'),
            (SimpleNamespace(sender_id='other', participant_id='silas', active=False),
             403, 'CONVERSATION_FORBIDDEN'),
        ]
        for conversation, status, code in cases:
            with self.subTest(status=status, conversation=conversation), patch.object(
                app.state, 'conversation_pool', object(), create=True
            ), patch('src.services.chat_service.PostgresConversationRepository') as repository, patch(
                'src.services.chat_service.PostgresMessageRepository'
            ) as messages, patch('src.services.chat_service.Agent') as agent, patch(
                'src.services.chat_service.message_to_record'
            ) as mapper:
                repository.return_value.get_by_id.return_value = conversation
                response = TestClient(app).post('/conversation/talk', json={
                    'conversation_id': 'Conv_test', 'sender_id': 'idealizador', 'message': 'Olá',
                })
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()['error']['code'], code)
                self.assertIsNone(response.json()['data'])
                repository.return_value.get_by_id.assert_called_once_with('Conv_test')
                mapper.assert_not_called()
                messages.assert_not_called()
                agent.assert_not_called()


if __name__ == '__main__':
    unittest.main()
