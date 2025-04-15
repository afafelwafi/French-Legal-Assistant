# test_agents/test_search_agent.py
import pytest
from unittest.mock import patch, MagicMock
from agents.search_agent import create_search_tool
from langchain.tools import Tool


@pytest.fixture
def mock_serpapi():
    with patch("agents.search_agent.SerpAPIWrapper") as mock:
        instance = mock.return_value
        instance.run.return_value = "Mock search results"
        yield mock


def test_create_search_tool(mock_serpapi):
    """Test creating a SerpAPI search tool"""

    # Call the function
    tool = create_search_tool()

    # Assert SerpAPIWrapper was initialized with API key
    mock_serpapi.assert_called_once()

    # Assert tool properties
    assert isinstance(tool, Tool)
    assert tool.name == "google_search"
    assert "Recherche Google" in tool.description

    # Test the tool's function
    result = tool.func("test query")
    assert result == "Mock search results"
    mock_serpapi.return_value.run.assert_called_once_with("test query")
