"""Mandatory context is selected by kind and survives a Notion outage."""
import unittest
from unittest.mock import MagicMock, patch

from src.agents.knowledge import load_general_documents


PAGES = {"manifesto": "manifesto-page", "research_project": "project-page"}


class MandatoryKnowledgeTests(unittest.TestCase):
    def test_notion_documents_are_used_when_available(self):
        client = MagicMock()
        client.blocks.children.list.side_effect = [
            {"results": [{"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "manifesto do Notion"}]}, "has_children": False}], "has_more": False},
            {"results": [{"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "projeto do Notion"}]}, "has_children": False}], "has_more": False},
        ]
        with patch.dict("os.environ", {"NOTION_TOKEN": "test-token"}), patch("src.agents.knowledge.Client", return_value=client):
            documents = load_general_documents(PAGES)
        self.assertIn("manifesto do Notion", documents[0])
        self.assertIn("projeto do Notion", documents[1])

    def test_local_fallback_when_notion_is_unavailable(self):
        client = MagicMock()
        client.blocks.children.list.side_effect = ConnectionError("offline")
        with patch.dict("os.environ", {"NOTION_TOKEN": "test-token"}), patch("src.agents.knowledge.Client", return_value=client):
            documents = load_general_documents(PAGES)
        self.assertIn("Manifesto Solarpunk", documents[0])
        self.assertIn("Yavin", documents[1])

    def test_missing_required_document_fails(self):
        with self.assertRaisesRegex(ValueError, "research_project"):
            load_general_documents({"manifesto": "manifesto-page"})
