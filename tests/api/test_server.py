import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import json
import time

# Import the FastAPI app from api.server
from api.server import app, cache, QueryRequest, QueryResponse

# Create a test client
client = TestClient(app)


@pytest.fixture
def mock_redis_cache():
    with patch("api.server.RedisCache") as mock_cache:
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        yield mock_cache_instance


@pytest.fixture
def mock_create_search_tool():
    with patch("api.server.create_search_tool") as mock_tool:
        mock_tool_instance = MagicMock()
        mock_tool.return_value = mock_tool_instance
        yield mock_tool


@pytest.fixture
def mock_create_rag_tool():
    with patch("api.server.create_rag_tool") as mock_tool:
        mock_tool_instance = MagicMock()
        mock_tool.return_value = mock_tool_instance
        yield mock_tool


@pytest.fixture
def mock_create_multi_agent():
    with patch("api.server.create_multi_agent") as mock_agent:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "Multi-agent response"
        mock_agent.return_value = mock_agent_instance
        yield mock_agent


@pytest.fixture
def mock_legal_data_loader():
    with patch("api.server.LegalDataLoader") as mock_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load = AsyncMock(return_value=["document1", "document2"])
        mock_loader.return_value = mock_loader_instance
        yield mock_loader


@pytest.fixture
def mock_groq_llm():
    # Patch the module-level import that happens inside the function
    with patch("models.llm.GroqLLM") as mock_llm:
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "Direct LLM response"
        mock_llm.return_value = mock_llm_instance
        yield mock_llm_instance


@pytest.fixture
def mock_time():
    with patch("api.server.time") as mock_time:
        # Configure time.time() to return increasing values for elapsed time calculation
        mock_time.time.side_effect = [100.0, 105.0]  # 5 seconds elapsed
        yield mock_time


def test_health_check():
    # Arrange
    with patch("api.server.time.time", return_value=123456789.0):
        # Act
        response = client.get("/api/health")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "timestamp": 123456789.0}


def test_flush_cache():
    # Arrange
    with patch.object(cache, "flush", return_value=10) as mock_flush:
        # Act
        response = client.post("/api/cache/flush")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "flushed": 10}
        mock_flush.assert_called_once()


def test_query_cached_response(mock_time):
    # Arrange
    query_request = {
        "query": "What is the civil code?",
        "law_codes": ["civil"],
        "use_search": True,
        "use_rag": True,
    }

    cached_response = {
        "query": "What is the civil code?",
        "direct_answer": "Cached direct answer",
        "multi_agent_answer": "Cached multi-agent answer",
        "processing_time": 2.5,
        "cached": False,
    }

    with patch.object(
        cache, "get", return_value=json.dumps(cached_response)
    ) as mock_get:
        # Act
        response = client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["query"] == query_request["query"]
        assert response_data["direct_answer"] == "Cached direct answer"
        assert response_data["multi_agent_answer"] == "Cached multi-agent answer"
        assert response_data["cached"] == True
        assert response_data["processing_time"] == 5.0  # From mock_time

        # Check cache key
        cache_key = {
            "query": query_request["query"],
            "law_codes": sorted(query_request["law_codes"]),
            "use_search": query_request["use_search"],
            "use_rag": query_request["use_rag"],
        }
        mock_get.assert_called_once_with(cache_key)


@pytest.mark.asyncio
async def test_query_new_response(
    mock_time,
    mock_create_search_tool,
    mock_create_rag_tool,
    mock_create_multi_agent,
    mock_legal_data_loader,
):
    # Arrange
    query_request = {
        "query": "What is the penal code?",
        "law_codes": ["penal"],
        "use_search": True,
        "use_rag": True,
        "verbose": True,
    }

    # Mock GroqLLM since it's imported inside the function
    with patch("models.llm.GroqLLM") as mock_llm_class:
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "Direct LLM response"
        mock_llm_class.return_value = mock_llm_instance

        with patch.object(cache, "get", return_value=None) as mock_get, patch.object(
            cache, "set"
        ) as mock_set:

            # Act
            response = client.post("/api/query", json=query_request)

            # Assert
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["query"] == query_request["query"]
            assert response_data["direct_answer"] == "Direct LLM response"
            assert response_data["multi_agent_answer"] == "Multi-agent response"
            assert response_data["cached"] == False
            assert response_data["processing_time"] == 5.0  # From mock_time

            # Verify tools and agent were created correctly
            mock_create_search_tool.assert_called_once()
            mock_create_rag_tool.assert_called_once_with(
                "penal", ["document1", "document2"]
            )
            mock_create_multi_agent.assert_called_once()

            # Verify cache operations
            mock_get.assert_called_once()
            mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_query_with_rag_only(
    mock_time, mock_create_rag_tool, mock_create_multi_agent, mock_legal_data_loader
):
    # Arrange
    query_request = {
        "query": "What is the civil code?",
        "law_codes": ["civil"],
        "use_search": False,  # No search tool
        "use_rag": True,
    }

    # Mock GroqLLM since it's imported inside the function
    with patch("models.llm.GroqLLM") as mock_llm_class:
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "Direct LLM response"
        mock_llm_class.return_value = mock_llm_instance

        with patch.object(cache, "get", return_value=None) as mock_get, patch.object(
            cache, "set"
        ) as mock_set:

            # Act
            response = client.post("/api/query", json=query_request)

            # Assert
            assert response.status_code == 200

            # Verify create_search_tool was not called
            from api.server import create_search_tool

            assert not hasattr(create_search_tool, "call_args")


@pytest.mark.asyncio
async def test_query_with_search_only(
    mock_time, mock_create_search_tool, mock_create_multi_agent
):
    # Arrange
    query_request = {
        "query": "What is recent jurisprudence?",
        "law_codes": ["civil"],
        "use_search": True,
        "use_rag": False,  # No RAG tools
    }

    # Mock GroqLLM since it's imported inside the function
    with patch("models.llm.GroqLLM") as mock_llm_class:
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "Direct LLM response"
        mock_llm_class.return_value = mock_llm_instance

        with patch.object(cache, "get", return_value=None) as mock_get, patch.object(
            cache, "set"
        ) as mock_set:

            # Act
            response = client.post("/api/query", json=query_request)

            # Assert
            assert response.status_code == 200

            # Verify create_rag_tool was not called
            from api.server import create_rag_tool

            assert not hasattr(create_rag_tool, "call_args")


@pytest.mark.asyncio
async def test_query_error_loading_law_code(mock_time, mock_legal_data_loader):
    # Arrange
    query_request = {
        "query": "What is the civil code?",
        "law_codes": ["civil"],
        "use_search": False,
        "use_rag": True,
    }

    # Make the legal data loader raise an exception
    mock_legal_data_loader.return_value.load.side_effect = Exception(
        "Failed to load documents"
    )

    with patch.object(cache, "get", return_value=None) as mock_get:
        # Act
        response = client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == 500
        assert "Error loading law code civil" in response.json()["detail"]


@pytest.mark.asyncio
async def test_query_error_in_multi_agent(
    mock_time, mock_create_rag_tool, mock_legal_data_loader
):
    # Arrange
    query_request = {
        "query": "What is the civil code?",
        "law_codes": ["civil"],
        "use_search": False,
        "use_rag": True,
    }

    # Clear or mock agent_cache to ensure our agent is used
    with patch("api.server.agent_cache", {}):
        # Create a mock agent that raises an exception when run is called
        mock_agent = MagicMock()
        mock_agent.run.side_effect = Exception("Agent error")

        # Patch create_multi_agent to return our mock agent
        with patch("api.server.create_multi_agent", return_value=mock_agent):
            # Mock GroqLLM since it's imported inside the function
            with patch("models.llm.GroqLLM") as mock_llm_class:
                mock_llm_instance = MagicMock()
                mock_llm_instance.return_value = "Direct LLM response"
                mock_llm_class.return_value = mock_llm_instance

                with patch.object(
                    cache, "get", return_value=None
                ) as mock_get, patch.object(cache, "set") as mock_set:

                    # Act
                    response = client.post("/api/query", json=query_request)

                    # Assert
                    assert response.status_code == 200
                    response_data = response.json()
                    assert "Error: Agent error" in response_data["multi_agent_answer"]
