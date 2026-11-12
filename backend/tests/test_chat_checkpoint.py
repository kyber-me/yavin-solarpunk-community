"""Checkpoint unit tests; HTTP integration awaits the owner's new conversation routes."""
import unittest
from unittest.mock import patch
from uuid import uuid4

from langchain_core.messages import AIMessage, SystemMessage
from langsmith import tracing_context
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from src.agents.yavinist import Agent
from src.types.dtos.send_message_service_request import Message


def test_graph(**kwargs):
    graph = StateGraph(MessagesState)
    graph.add_node('reply', lambda state: {'messages': [AIMessage(content='ok')]})
    graph.add_edge(START, 'reply')
    graph.add_edge('reply', END)
    return graph.compile(checkpointer=kwargs['checkpointer'])


class CheckpointTests(unittest.TestCase):
    def test_nested_message_round_trip(self):
        message = Message(content='oi')
        restored = Message.model_validate(message.model_dump())
        self.assertEqual(restored, message)

    def test_restore_without_duplicating_knowledge_and_isolate_threads(self):
        verify_persistence(self, InMemorySaver())

    def test_missing_thread_id_is_rejected(self):
        with patch('src.agents.yavinist.py.py.create_agent', side_effect=test_graph):
            agent = Agent('Silas', None, InMemorySaver())
            with self.assertRaises(ValueError):
                agent.invoke('oi', '')


def verify_persistence(case, saver, restore=None):
    thread = 'test-checkpoint-' + str(uuid4())
    other = thread + '-other'
    try:
        with tracing_context(enabled=False), patch('src.agents.yavinist.py.py.create_agent', side_effect=test_graph), patch.object(
            __import__('src.agents.agent', fromlist=['_retrieval_knowledge']), '_retrieval_knowledge', return_value=[SystemMessage('reference')]
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
