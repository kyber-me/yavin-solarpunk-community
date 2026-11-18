from typing import Literal
from dotenv import load_dotenv

from adapters import QdrantVectorStoreContainer

load_dotenv()  # Does it make the `TavilySearch` to use the Tavily API Key?

from langchain.tools import ToolRuntime, tool
from langchain_core.tools import BaseTool

from langchain_tavily import TavilySearch


def web_search(
        topic: Literal['general', 'news', 'finance'] = "general",
        domains: list[str] | None = None) -> BaseTool:

    t = TavilySearch(
        max_results=5,
        topic=topic,
        # include_answer=False,
        # include_raw_content=False,
        # include_images=False,
        # include_image_descriptions=False,
        # search_depth="basic",
        # time_range="day",
        include_domains=domains,
        # exclude_domains=None
    )

    return t.as_tool()


@tool
def get_agent_state(runtime: ToolRuntime) -> dict:
    """Return the state of an agent"""
    return runtime.state

@tool
def get_base_knowledge(vector_database: QdrantVectorStoreContainer, query: str) -> str:
    base_knowledge_retriever = vector_database.get_retriever()
    retrieved_docs = base_knowledge_retriever.invoke(query)
    # retrieved_docs is a list of documents

    return "\n\n".join([content.page_content for content in retrieved_docs])
