# tests/test_api.py
import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.server import app

# Create test client
client = TestClient(app)

@pytest.fixture
def mock_cache():
    """Mock for RedisCache."""
    with patch('api.server.cache') as mock:
        yield mock

@pytest.fixture
def mock_create_search_tool():
    """Mock for create_search_tool."""
    with patch('api.server.create_search_tool') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_create_rag_tool():
    """Mock for create_rag_tool."""
    with patch('api.server.create_rag_tool') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_async_json_loader():
    """Mock for AsyncJSONLoader."""
    with patch('api.server.AsyncJSONLoader') as mock:
        mock_loader = MagicMock()
        mock_loader.load = MagicMock(return_value=[])
        mock.return_value = mock_loader
        yield mock

@pytest.fixture
def mock_agent():
    """Mock for create_multi_agent."""
    with patch('api.server.create_multi_