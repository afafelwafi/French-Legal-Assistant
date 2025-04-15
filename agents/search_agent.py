# agents/search_agent.py
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
from config import SERPAPI_API_KEY


def create_search_tool():
    """
    Create a SerpAPI search tool.

    Returns:
        Tool for Google search
    """
    # Initialize SerpAPI wrapper
    search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)

    # Create search tool
    search_tool = Tool(
        name="google_search",
        func=search.run,
        description="Recherche Google pour des informations juridiques externes et récentes.",
    )

    return search_tool
