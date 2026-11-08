from typing import Literal
from dotenv import load_dotenv

load_dotenv()  # Does it make the `TavilySearch` to use the Tavily API Key?
from langchain_core.tools import BaseTool

from langchain_tavily import TavilySearch
#from langchain import tools

def web_search(
        topic: Literal['general', 'news', 'finance'] = "general",
        domains: list[str] | None = None) -> BaseTool:

    tool = TavilySearch(
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

    return tool.as_tool()

