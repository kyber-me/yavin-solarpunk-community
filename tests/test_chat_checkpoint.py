import unittest
from contextlib import contextmanager
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from main import app
from src.agents.main import Agent
from src.domain.chat.messages.main import TextMessage
from src.services.chat_service import CHAT_CACHE
from src.types.dtos.chat_service_request import ChatServiceRequestDto


def test_graph(**kwargs):
    graph = StateGraph(MessagesState)
    graph.add_node('reply', lambda state: {'messages': [AIMessage(content='ok')]})
    graph.add_edge(START, 'reply')
    graph.add_edge('reply', END)
    return graph.compile(checkpointer=kwargs['checkpointer'])


class CheckpointTests(unittest.TestCase):
    def test_nested_message_round_trip(self):
        message = TextMessage(content='oi', sender='a', receiver='b',
                              conversation_id='Conv_1', conversation_look_up_id='Conv_a_b')
        dto = ChatServiceRequestDto(message=message.model_dump(), sender_id='a',
                                    receiver_id='b', thread_id='one')
        self.assertEqual(dto.message.id, message.id)

    def test_restore_without_duplicating_knowledge_and_isolate_threads(self):
        verify_persistence(self, InMemorySaver())

    def test_frontend_contract_and_empty_message(self):
        @contextmanager
        def checkpointer():
            yield InMemorySaver()

        CHAT_CACHE.clear()
        try:
            with patch('main.open_checkpointer', checkpointer), patch(
                'src.agents.main.create_agent', side_effect=test_graph
            ), patch.object(Agent, '_retrieval_knowledge', return_value=[SystemMessage('reference')]):
                with TestClient(app) as client:
                    payload = {'message': 'oi', 'sender_id': 'idealizador', 'thread_id': 'one'}
                    response = client.post('/chat', json=payload)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json()['data']['content'], 'ok')
                    payload['thread_id'] = 'two'
                    self.assertEqual(client.post('/chat', json=payload).status_code, 200)
                    self.assertEqual(len(CHAT_CACHE), 2)
                    payload['message'] = '  '
                    self.assertEqual(client.post('/chat', json=payload).status_code, 400)
        finally:
            CHAT_CACHE.clear()


def verify_persistence(case, saver, restore=None):
    thread = 'test-checkpoint-' + str(uuid4())
    other = thread + '-other'
    try:
        with patch('src.agents.main.create_agent', side_effect=test_graph), patch.object(
            Agent, '_retrieval_knowledge', return_value=[SystemMessage('reference')]
        ) as knowledge:
            Agent('Silas', None, saver).invoke('first', thread)
            if restore:
                saver = restore()
            agent = Agent('Silas', None, saver)
            agent.invoke('second', thread)
            messages = agent.get_state(thread)[0].values['messages']
            case.assertEqual([m.content for m in messages], ['reference', 'first', 'ok', 'second', 'ok'])
            case.assertEqual(knowledge.call_count, 1)
            case.assertFalse(agent.get_state(other)[0].values)
    finally:
        saver.delete_thread(thread)


if __name__ == '__main__':
    unittest.main()
