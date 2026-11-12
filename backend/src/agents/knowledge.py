"""Load the two shared documents from Notion, with local files on outage."""
import logging
from src.constants import BASE_KNOWLEDGE_PATH

# from notion_client import Client

LOG = logging.getLogger(__name__)
LOCAL = {
    "manifesto": BASE_KNOWLEDGE_PATH / "manifestos/SOLARPUNK_MANIFESTO.md",
    "research_project": BASE_KNOWLEDGE_PATH / "institutional/PROJETO_DE_PESQUISA_YAVIN.md",
}


def retrieval_knowledge() -> list[str]:
    print("Retrieving knowledge locally...")
    LOG.warning("Retrieving knowledge locally...")

    base_knowledge_paths = [BASE_KNOWLEDGE_PATH / "manifestos", BASE_KNOWLEDGE_PATH / "institutional"]
    messages: list[str] = []
    try:
        for b in base_knowledge_paths:
            if b.exists():
                if b.is_dir():
                    for f in b.iterdir():
                        if f.is_file() and f.suffix.lower() == ".md":
                            with open(f, "r") as f_:
                                content = f_.read()
                                messages.append(content)
                        else:
                            print(
                                f"{f.name} is not a file (needs recursive iteration)"
                            )
                elif b.is_file():
                    with open(b, "r") as f:
                        content = f.read()
                        messages.append(content)
    except Exception as e:  # noqa: BLE001
        print(e)
        return []

    return messages


# def _block_text(client: Client, block_id: str) -> str:
#     lines: list[str] = []
#     cursor: str | None = None
#     while True:
#         response = client.blocks.children.list(block_id=block_id, start_cursor=cursor, page_size=100) if cursor else client.blocks.children.list(block_id=block_id, page_size=100)
#         for block in response["results"]:
#             kind = block["type"]
#             payload = block.get(kind, {})
#             rich_text = payload.get("rich_text", [])
#             line = "".join(part.get("plain_text", "") for part in rich_text)
#             if kind == "child_page":
#                 line = payload.get("title", "")
#             if line.strip():
#                 lines.append(line)
#             if block.get("has_children"):
#                 nested = _block_text(client, block["id"])
#                 if nested:
#                     lines.append(nested)
#         if not response.get("has_more"):
#             break
#         cursor = response.get("next_cursor")
#         if not cursor:
#             raise ValueError("Notion pagination ended without a cursor")
#     return "\n".join(lines)

# def load_general_documents(pages: dict[str, str]) -> list[str]:
#     token = os.getenv("NOTION_TOKEN")
#     client = Client(auth=token) if token else None
#     documents: list[str] = []
#     for kind in ("manifesto", "research_project"):
#         page = pages.get(kind)
#         if not page:
#             raise ValueError(f"Required document is missing: {kind}")
#         try:
#             if client is None:
#                 raise ConnectionError("Notion is not configured")
#             content = _block_text(client, page)
#             if not content.strip():
#                 raise ValueError(f"Notion document is empty: {kind}")
#             LOG.info("Knowledge document %s loaded from Notion", kind)
#         except Exception as exc:
#             LOG.warning("Notion document %s unavailable; using local copy: %s", kind, type(exc).__name__)
#             content = LOCAL[kind].read_text(encoding="utf-8")
#             if not content.strip():
#                 raise ValueError(f"Required local document is empty: {kind}") from exc
#         documents.append(f"[{kind}]\n{content}")
#     return documents