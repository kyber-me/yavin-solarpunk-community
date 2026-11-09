"""Title update HTTP contract without database lifespan."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


class UpdateConversationTitleTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(app.state, 'conversation_pool', object(), create=True))
        self.repository = self.enterContext(patch(
            'src.services.update_conversation_title_service.PostgresConversationRepository'
        )).return_value
        self.repository.get_by_id.return_value = SimpleNamespace(id='conversation', sender_id='owner')
        self.repository.update_title.return_value = SimpleNamespace(id='conversation', title='Nova pesquisa')

    def test_owner_can_update_title(self):
        response = TestClient(app).patch('/conversations/conversation/title', json={
            'owner_id': 'owner', 'title': '  Nova pesquisa  ',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'], {'conversation_id': 'conversation', 'title': 'Nova pesquisa'})
        self.repository.update_title.assert_called_once_with('conversation', 'owner', 'Nova pesquisa')

    def test_missing_and_other_owner_are_rejected_without_update(self):
        self.repository.get_by_id.return_value = None
        response = TestClient(app).patch('/conversations/missing/title', json={'owner_id': 'owner', 'title': 'Nova pesquisa'})
        self.assertEqual(response.status_code, 404)
        self.repository.get_by_id.return_value = SimpleNamespace(id='conversation', sender_id='owner')
        response = TestClient(app).patch('/conversations/conversation/title', json={'owner_id': 'other', 'title': 'Nova pesquisa'})
        self.assertEqual(response.status_code, 403)
        self.repository.update_title.assert_not_called()

    def test_blank_and_long_titles_are_rejected(self):
        for title in ('  ', 'x' * 121):
            with self.subTest(title=title):
                response = TestClient(app).patch('/conversations/conversation/title', json={'owner_id': 'owner', 'title': title})
                self.assertEqual(response.status_code, 422)
        self.repository.update_title.assert_not_called()


if __name__ == '__main__':
    unittest.main()
