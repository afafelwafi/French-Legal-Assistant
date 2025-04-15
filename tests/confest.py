# tests/conftest.py
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from langchain.schema import Document
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Load test data
@pytest.fixture
def sample_legal_documents():
    """Fixture that returns sample legal documents for testing."""
    test_data_path = os.path.join(
        os.path.dirname(__file__), "test_data", "civil_code_sample.json"
    )

    with open(test_data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert data to Document objects
    documents = []
    for item in data:
        doc = Document(
            page_content=item.get("content", ""),
            metadata={
                "source": "test_source",
                "law_code": "civil",
                "article_id": item.get("id", ""),
                "article_title": item.get("title", ""),
            },
        )
        documents.append(doc)

    return documents


@pytest.fixture
def mock_groq_response():
    """Mock Groq API response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a mock response from the LLM."
    return mock_response


@pytest.fixture
def mock_search_results():
    """Mock search results."""
    return "Mock search results from SerpAPI."


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model."""
    mock_model = MagicMock()
    # Mock the embedding function to return consistent vectors for testing
    mock_model.embed_documents = MagicMock(
        return_value=[[0.1, 0.2, 0.3, 0.4] for _ in range(10)]
    )
    mock_model.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3, 0.4])
    return mock_model


@pytest.fixture
def mock_vectorstore():
    """Mock vectorstore."""
    mock_vs = MagicMock()
    mock_vs.as_retriever.return_value = MagicMock()

    # Mock similarity search to return sample documents
    def mock_similarity_search(query, k=4):
        return [
            Document(
                page_content="Sample legal text for testing",
                metadata={"article_id": "test-123", "law_code": "civil"},
            )
        ]

    mock_vs.similarity_search = mock_similarity_search
    return mock_vs
