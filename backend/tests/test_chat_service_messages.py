"""Response authorship, UTC defaults and preservation of application errors."""
import unittest
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI, Request

from src.infra.db.relational.message_record import MessageRecord
from src.services.send_message_service import ChatService
from src.types.app_error import AppError
from src.types.dtos.send_message_service_request import ChatServiceRequest


class ChatServiceMessageTests(unittest.TestCase):
    def setUp(self):
        application = FastAPI()
        application.state.conversation_pool = object()
        application.state.checkpointer = object()
        self.request = Request({'type': 'http', 'app': application})
        self.dto = ChatServiceRequest(conversation_id='Conv_test', sender_id='idealizador', message='Olá')
        self.conversation = SimpleNamespace(sender_id='idealizador', participant_id='silas', thread_id='thread_test', active=True)
        self.conversations = self.enterContext(patch(
            'src.services.send_message_service.py.PostgresConversationRepository'))
        self.conversations.return_value.get_by_id.return_value = self.conversation
        self.messages = self.enterContext(patch('src.services.send_message_service.py.PostgresMessageRepository')).return_value
        self.messages.create.side_effect = lambda record: record
        self.agent = self.enterContext(patch('src.services.send_message_service.py.Agent')).return_value
        self.agent.invoke.return_value = {'content': 'Resposta'}

    def test_response_uses_other_participant_in_either_pair_orientation(self):
        for sender, participant in [('idealizador', 'silas'), ('silas', 'idealizador')]:
            with self.subTest(sender=sender, participant=participant):
                self.conversation.sender_id = sender
                self.conversation.participant_id = participant
                self.messages.create.reset_mock()
                self.assertEqual(ChatService.run(self.dto, self.request), {'content': 'Resposta'})
                incoming, outgoing = [call.args[0] for call in self.messages.create.call_args_list]
                self.assertEqual(incoming.sender_id, 'idealizador')
                self.assertEqual(outgoing.sender_id, 'silas')
                self.assertEqual(outgoing.content, 'Resposta')
                self.assertEqual(outgoing.created_at.utcoffset(), timedelta(0))
                self.assertNotEqual(incoming.id, outgoing.id)
        self.agent.invoke.assert_called_with('Olá', 'thread_test')

    def test_default_record_timestamp_has_utc_timezone(self):
        record = MessageRecord(conversation_id='Conv_test', sender_id='silas', content='Resposta')
        self.assertEqual(record.created_at.utcoffset(), timedelta(0))

    def test_app_error_preserved_at_each_operation(self):
        for operation in ('incoming', 'agent', 'outgoing'):
            with self.subTest(operation=operation):
                error = AppError(code='TEST_ERROR', message='Specific failure', status_code=409)
                self.messages.create.side_effect = lambda record: record
                self.agent.invoke.side_effect = None
                if operation == 'incoming':
                    self.messages.create.side_effect = error
                elif operation == 'agent':
                    self.agent.invoke.side_effect = error
                else:
                    self.messages.create.side_effect = [SimpleNamespace(content='Olá'), error]
                with self.assertRaises(AppError) as caught:
                    ChatService.run(self.dto, self.request)
                self.assertIs(caught.exception, error)
                self.assertEqual((caught.exception.code, caught.exception.message, caught.exception.status_code),
                                 ('TEST_ERROR', 'Specific failure', 409))


if __name__ == '__main__':
    unittest.main()
