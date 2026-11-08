"""Catalog and local browser access, without application lifespan or model calls."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


class AgentCatalogTests(unittest.TestCase):
    def test_catalog_returns_only_silas_without_constructing_agent(self):
        with patch('src.services.send_message_service.py.Agent') as agent:
            response = TestClient(app).get('/agents')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'data': {'agents': [{'id': 'silas', 'name': 'Silas'}]}, 'error': None,
        })
        agent.assert_not_called()
        self.assertEqual(TestClient(app).get('/agents').json(), response.json())

    def test_get_and_post_preflights_allow_only_configured_local_origins(self):
        for origin in ('http://localhost:5173', 'http://127.0.0.1:5173'):
            for method in ('GET', 'POST'):
                with self.subTest(origin=origin, method=method):
                    response = TestClient(app).options('/agents', headers={
                        'Origin': origin, 'Access-Control-Request-Method': method,
                        'Access-Control-Request-Headers': 'Content-Type',
                    })
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.headers['access-control-allow-origin'], origin)
                    self.assertIn(method, response.headers['access-control-allow-methods'])
            response = TestClient(app).get('/agents', headers={'Origin': origin})
            self.assertEqual(response.headers['access-control-allow-origin'], origin)

    def test_other_origin_and_unapproved_method_are_not_enabled(self):
        for origin, method in [('https://unapproved.example', 'GET'), ('http://localhost:5173', 'DELETE')]:
            with self.subTest(origin=origin, method=method):
                response = TestClient(app).options('/agents', headers={
                    'Origin': origin, 'Access-Control-Request-Method': method,
                })
                self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
