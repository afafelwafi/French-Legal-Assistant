# tests/test_agents.py
import pytest
from unittest.mock import patch, MagicMock
from agents.search_agent import create_search_tool
from agents.rag_agent import create_rag_tool
from agents.multi_agent import create_multi_agent


@patch("agents.search_agent.SerpAPIWrapper")
def test_create_search_tool(mock_serpapi):
    """Test that create_search_tool returns a tool with the right name and description."""
    # Set up mock
    mock_serpapi_instance = MagicMock()
    mock_serpapi.return_value = mock_serpapi_instance

    # Call the function
    tool = create_search_tool()

    # Assertions
    assert tool.name == "google_search"
    assert "Recherche Google" in tool.description
    assert tool.func == mock_serpapi_instance.run


@patch("agents.rag_agent.GroqLLM")
@patch("agents.rag_agent.VectorstoreManager")
@patch("agents.rag_agent.RetrievalQA")
def test_create_rag_tool(mock_retrieval_qa, mock_vectorstore_manager, mock_groq_llm):
    """Test that create_rag_tool returns a tool with the right name and properties."""
    # Set up mocks
    mock_llm = MagicMock()
    mock_groq_llm.return_value = mock_llm

    mock_vectorstore = MagicMock()
    mock_retriever = MagicMock()
    mock_vectorstore.as_retriever.return_value = mock_retriever

    mock_manager = MagicMock()
    mock_manager.get_vectorstore.return_value = mock_vectorstore
    mock_vectorstore_manager.return_value = mock_manager

    mock_chain = MagicMock()
    mock_retrieval_qa.from_chain_type.return_value = mock_chain

    # Call the function
    tool = create_rag_tool("civil", [])

    # Assertions
    assert tool.name == "civil_rag"
    assert "Recherche juridique" in tool.description
    assert "civil" in tool.description
    assert tool.func == mock_chain.run

    # Verify interactions
    mock_groq_llm.assert_called_once()
    mock_vectorstore_manager.assert_called_once_with("civil")
    mock_vectorstore.as_retriever.assert_called_once()
    mock_retrieval_qa.from_chain_type.assert_called_once()


@patch("agents.multi_agent.GroqLLM")
@patch("agents.multi_agent.initialize_agent")
def test_create_multi_agent(mock_initialize_agent, mock_groq_llm):
    """Test that create_multi_agent returns an agent with the right properties."""
    # Set up mocks
    mock_llm = MagicMock()
    mock_groq_llm.return_value = mock_llm

    mock_agent = MagicMock()
    mock_initialize_agent.return_value = mock_agent

    # Create some mock tools
    mock_tools = [MagicMock(), MagicMock()]

    # Call the function
    agent = create_multi_agent(mock_tools, True)

    # Assertions
    assert agent == mock_agent

    # Verify interactions
    mock_groq_llm.assert_called_once()
    mock_initialize_agent.assert_called_once_with(
        mock_tools,
        mock_llm,
        agent=mock_initialize_agent.call_args[1]["agent"],
        verbose=True,
    )
