"""Real HTTP services, PostgreSQL and checkpoints; only model execution is simulated."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import psycopg
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langsmith import tracing_context
from psycopg.errors import CheckViolation
from ulid import ULID

from main import app
from src.agents.infra.open_checkpointer_helper import open_checkpointer


def simulated_graph(**kwargs):
    def reply(state):
        messages = [message for message in state['messages'] if isinstance(message, HumanMessage)]
        return {'messages': [AIMessage(content=f'turn={len(messages)}; first={messages[0].content}; last={messages[-1].content}')]}

    graph = StateGraph(MessagesState)
    graph.add_node('reply', reply)
    graph.add_edge(START, 'reply')
    graph.add_edge('reply', END)
    return graph.compile(checkpointer=kwargs['checkpointer'])


@unittest.skipUnless(os.getenv('YAVIN_TEST_DB_URI'), 'Requires fresh disposable YAVIN_TEST_DB_URI')
class HttpIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.uri = os.environ['YAVIN_TEST_DB_URI']
        cls.seed_thread = str(ULID())
        with psycopg.connect(cls.uri) as connection:
            if connection.execute("SELECT to_regnamespace('yavin'), to_regclass('public.checkpoints')").fetchone() != (None, None):
                raise RuntimeError('Refusing to run: disposable database must be empty')
        # Exercise the actual situation: checkpoint data exists before the domain schema.
        with patch.dict(os.environ, {'DATABASE_URI': cls.uri}), tracing_context(enabled=False):
            with open_checkpointer() as saver:
                simulated_graph(checkpointer=saver).invoke(
                    {'messages': [HumanMessage('before schema')]},
                    {'configurable': {'thread_id': cls.seed_thread}},
                )
        with psycopg.connect(cls.uri, autocommit=True) as connection:
            connection.execute(Path('src/persistence/db/relational/migrations/001_initial_schema.sql').read_text())
            connection.execute(Path('src/persistence/db/relational/migrations/002_agents_documents.sql').read_text())
            connection.execute(Path('src/persistence/db/relational/migrations/003_agent_public_description.sql').read_text())
            connection.execute(Path('src/persistence/db/relational/migrations/004_conversation_title.sql').read_text())

    def setUp(self):
        self.sender = str(ULID())
        self.enterContext(patch.dict(os.environ, {'DATABASE_URI': self.uri}))
        self.enterContext(tracing_context(enabled=False))
        self.factory = self.enterContext(patch('src.agents.agent.create_agent', side_effect=simulated_graph))
        self.knowledge = self.enterContext(patch(
            'src.agents.agent._retrieval_knowledge', side_effect=lambda **kwargs: [SystemMessage('test reference')]
        ))

    def create(self, client, sender=None):
        self.agent_id = client.get('/agents').json()['data']['agents'][0]['id']
        response = client.post('/conversation/create', json={
            'owner_id': sender or self.sender,
            'conversation_details': {'title': 'Conversa com Silas', 'participant_id': self.agent_id},
        })
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()['data']['conversation_id']

    def talk(self, client, conversation, content, sender=None):
        return client.post('/conversation/message', json={
            'sender_id': sender or self.sender, 'conversation_id': conversation, 'message': content,
        })

    def rows(self, conversation):
        with psycopg.connect(self.uri) as connection:
            return connection.execute(
                'SELECT sender_id, content, created_at FROM yavin.messages '
                'WHERE conversation_id = %s ORDER BY created_at, id', (conversation,),
            ).fetchall()

    def test_catalog_public_description_is_nullable_and_never_exposes_identity(self):
        with TestClient(app) as client:
            initial = client.get('/agents').json()['data']['agents'][0]
            agent_id = initial['id']
            self.assertIsNone(initial['public_description'])
            self.assertEqual(set(initial), {'id', 'name', 'public_description'})
            try:
                with psycopg.connect(self.uri) as connection:
                    connection.execute('UPDATE yavin.agents SET public_description = %s WHERE id = %s',
                                       ('Investiga energia em Yavin.', agent_id))
                updated = client.get('/agents').json()['data']['agents'][0]
                self.assertEqual(updated['public_description'], 'Investiga energia em Yavin.')
                with self.assertRaises(CheckViolation), psycopg.connect(self.uri) as connection:
                    connection.execute('UPDATE yavin.agents SET public_description = %s WHERE id = %s',
                                       ('   ', agent_id))
            finally:
                with psycopg.connect(self.uri) as connection:
                    connection.execute('UPDATE yavin.agents SET public_description = NULL WHERE id = %s', (agent_id,))

    def test_full_flow_restart_isolation_and_resource_shutdown(self):
        with TestClient(app) as client:
            pool, checkpoint_connection = app.state.conversation_pool, app.state.checkpointer.conn
            self.assertEqual(client.get('/agents').json()['data']['agents'][0]['name'], 'Silas')
            conversation = self.create(client)
            renamed = client.patch(f'/conversations/{conversation}/title', json={
                'owner_id': self.sender, 'title': 'Pesquisa solar',
            })
            self.assertEqual(renamed.status_code, 200, renamed.text)
            self.assertEqual(renamed.json()['data']['title'], 'Pesquisa solar')
            self.assertEqual(client.get('/conversations', params={'sender_id': self.sender}).json()['data']['conversations'][0]['title'], 'Pesquisa solar')
            duplicate = client.post('/conversation/create', json={
                'owner_id': self.sender,
                'conversation_details': {'title': 'Conversa com Silas', 'participant_id': self.agent_id},
            })
            self.assertEqual(duplicate.status_code, 409)
            self.assertEqual(duplicate.json()['error']['details']['conversation_id'], conversation)
            first = self.talk(client, conversation, 'primeira')
            self.assertEqual(first.status_code, 200, first.text)
            self.assertEqual(first.json()['data']['content'], 'turn=1; first=primeira; last=primeira')
            self.assertEqual([row[:2] for row in self.rows(conversation)],
                             [(self.sender, 'primeira'), (self.agent_id, first.json()['data']['content'])])
        self.assertTrue(pool.closed)
        self.assertTrue(checkpoint_connection.closed)

        with TestClient(app) as client:
            second = self.talk(client, conversation, 'segunda')
            self.assertEqual(second.status_code, 200, second.text)
            self.assertEqual(second.json()['data']['content'], 'turn=2; first=primeira; last=segunda')
            other_sender = str(ULID())
            other = self.create(client, other_sender)
            isolated = self.talk(client, other, 'isolada', other_sender)
            self.assertEqual(isolated.status_code, 200, isolated.text)
            self.assertEqual(isolated.json()['data']['content'], 'turn=1; first=isolada; last=isolada')
        self.assertEqual(len(self.rows(conversation)), 4)
        self.assertTrue(all(row[2].utcoffset() is not None for row in self.rows(conversation)))
        self.assertEqual(self.knowledge.call_count, 2)

    def test_rejections_have_no_message_or_agent_effects(self):
        with TestClient(app) as client:
            unavailable = client.post('/conversation/create', json={
                'owner_id': self.sender,
                'conversation_details': {'title': 'Conversa com Silas', 'participant_id': 'missing'},
            })
            self.assertEqual(unavailable.status_code, 422)
            conversation = self.create(client)
            self.assertEqual(self.talk(client, str(ULID()), 'missing').status_code, 404)
            self.assertEqual(self.talk(client, conversation, 'forbidden', str(ULID())).status_code, 403)
            self.assertEqual(self.talk(client, conversation, '   ').status_code, 400)
            with psycopg.connect(self.uri) as connection:
                connection.execute('UPDATE yavin.conversations SET active = FALSE WHERE id = %s', (conversation,))
            self.assertEqual(self.talk(client, conversation, 'inactive').status_code, 409)
            self.assertEqual(self.rows(conversation), [])
            self.factory.assert_not_called()

    def test_persisted_lists_and_history_survive_reload_and_authorize_reads(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/conversations', params={'sender_id': self.sender}).json()['data']['conversations'], [])
            conversation = self.create(client)
            self.assertEqual(self.talk(client, conversation, 'persisted history').status_code, 200)
            listing = client.get('/conversations', params={'sender_id': self.sender, 'limit': 1})
            summary = listing.json()['data']['conversations'][0]
            self.assertEqual(summary['conversation_id'], conversation)
            self.assertEqual(summary['participant_name'], 'Silas')
            self.assertNotIn('thread_id', summary)
            path = f'/conversations/{conversation}/messages'
            first = client.get(path, params={'sender_id': self.sender, 'limit': 1}).json()['data']
            second = client.get(path, params={'sender_id': self.sender, 'limit': 1, 'offset': first['next_offset']}).json()['data']
            self.assertEqual(first['messages'][0]['content'], 'persisted history')
            self.assertEqual(second['messages'][0]['sender_id'], self.agent_id)
            self.assertIsNone(second['next_offset'])
            self.assertEqual(client.get(path, params={'sender_id': 'outsider'}).status_code, 403)
            self.assertEqual(client.get(f'/conversations/{ULID()}/messages', params={'sender_id': self.sender}).status_code, 404)
            self.assertEqual(client.get('/conversations', params={'sender_id': 'outsider'}).json()['data']['conversations'], [])
            with psycopg.connect(self.uri) as connection:
                connection.execute('UPDATE yavin.conversations SET active = FALSE WHERE id = %s', (conversation,))
            newer = self.create(client)
            page = client.get('/conversations', params={'sender_id': self.sender, 'limit': 1}).json()['data']
            self.assertEqual(page['conversations'][0]['conversation_id'], newer)
            self.assertEqual(page['next_offset'], 1)
        with TestClient(app) as client:
            listing = client.get('/conversations', params={'sender_id': self.sender}).json()['data']['conversations']
            self.assertEqual(len(listing), 2)
            self.assertFalse(next(item for item in listing if item['conversation_id'] == conversation)['active'])
            history = client.get(path, params={'sender_id': self.sender}).json()['data']['messages']
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]['id'], first['messages'][0]['id'])

    def test_agent_failure_keeps_committed_incoming_message(self):
        with TestClient(app) as client:
            conversation = self.create(client)
            self.factory.side_effect = RuntimeError('simulated model failure')
            response = self.talk(client, conversation, 'keep this')
            self.assertEqual(response.status_code, 500)
            self.assertEqual([row[:2] for row in self.rows(conversation)], [(self.sender, 'keep this')])
            self.factory.side_effect = simulated_graph
            recovered = self.talk(client, conversation, 'next')
            self.assertEqual(recovered.status_code, 200, recovered.text)
            self.assertEqual(len(self.rows(conversation)), 3)

    def test_schema_preserves_previous_checkpoints_and_rejects_prefixed_ids(self):
        with TestClient(app) as client:
            state = simulated_graph(checkpointer=app.state.checkpointer).get_state(
                {'configurable': {'thread_id': self.seed_thread}}
            )
            self.assertEqual(state.values['messages'][0].content, 'before schema')
            conversation = self.create(client)
            with self.assertRaises(CheckViolation), psycopg.connect(self.uri) as connection:
                connection.execute('UPDATE yavin.conversations SET id = %s WHERE id = %s',
                                   ('Conv_' + conversation, conversation))
            self.assertEqual(self.talk(client, conversation, 'valid').status_code, 200)
            with self.assertRaises(CheckViolation), psycopg.connect(self.uri) as connection:
                connection.execute('UPDATE yavin.messages SET id = %s WHERE conversation_id = %s',
                                   ('Mess_' + str(ULID()), conversation))


if __name__ == '__main__':
    unittest.main()
