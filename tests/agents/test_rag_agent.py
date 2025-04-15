# test_agents/test_rag_agent.py
import pytest
from unittest.mock import MagicMock, patch
from agents.rag_agent import create_rag_tool
from langchain.tools import Tool


@pytest.fixture
def mock_vectorstore_manager():
    with patch("agents.rag_agent.VectorstoreManager") as mock:
        # Configure the mock
        instance = mock.return_value
        instance.load_vectorstore.return_value = MagicMock()
        instance.create_vectorstore.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_llm():
    with patch("agents.rag_agent.GroqLLM") as mock:
        yield mock


@pytest.fixture
def mock_retrieval_qa():
    with patch("agents.rag_agent.RetrievalQA") as mock:
        mock.from_chain_type.return_value = MagicMock()
        yield mock


def test_create_rag_tool_existing_vectorstore(
    mock_vectorstore_manager, mock_llm, mock_retrieval_qa
):
    """Test creating a RAG tool when vectorstore exists"""
    law_code_name = "code_civil"

    # Call the function
    tool = create_rag_tool(law_code_name)

    # Assertions
    mock_vectorstore_manager.assert_called_once_with(law_code_name)
    mock_vectorstore_manager.return_value.load_vectorstore.assert_called_once()
    mock_vectorstore_manager.return_value.create_vectorstore.assert_not_called()

    # Verify tool properties
    assert isinstance(tool, Tool)
    assert tool.name == f"{law_code_name}_rag"
    assert "code_civil" in tool.description


def test_create_rag_tool_new_vectorstore(
    mock_vectorstore_manager, mock_llm, mock_retrieval_qa
):
    """Test creating a RAG tool when vectorstore doesn't exist"""
    law_code_name = "code_penal"
    documents = ["doc1", "doc2"]

    # Configure mock to raise FileNotFoundError
    mock_vectorstore_manager.return_value.load_vectorstore.side_effect = (
        FileNotFoundError
    )

    # Call the function
    tool = create_rag_tool(law_code_name, documents)

    # Assertions
    mock_vectorstore_manager.assert_called_once_with(law_code_name)
    mock_vectorstore_manager.return_value.load_vectorstore.assert_called_once()
    mock_vectorstore_manager.return_value.create_vectorstore.assert_called_once_with(
        documents
    )

    # Verify tool properties
    assert isinstance(tool, Tool)
    assert tool.name == f"{law_code_name}_rag"
    assert "code_penal" in tool.description


def test_create_rag_tool_no_vectorstore_no_docs(
    mock_vectorstore_manager, mock_llm, mock_retrieval_qa
):
    """Test creating a RAG tool when vectorstore doesn't exist and no documents provided"""
    law_code_name = "code_commerce"

    # Configure mock to raise FileNotFoundError
    mock_vectorstore_manager.return_value.load_vectorstore.side_effect = (
        FileNotFoundError
    )

    # Call should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        create_rag_tool(law_code_name)

    # Verify error message
    assert "No existing vectorstore found" in str(excinfo.value)
    assert law_code_name in str(excinfo.value)
