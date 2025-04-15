# tests/test_llm.py
import pytest
from unittest.mock import patch, MagicMock

from models.llm import GroqLLM


@pytest.fixture
def mock_groq():
    """Mock Groq client"""
    with patch("models.llm.Groq") as mock_groq_class:
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        # Set up the nested structure of the Groq client
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_message.content = "This is a test response"
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]

        mock_client.chat.completions.create.return_value = mock_completion

        yield mock_groq_class


@pytest.fixture
def mock_config():
    """Mock config values"""
    with patch("models.llm.DEFAULT_MODEL", "test-model"), patch(
        "models.llm.DEFAULT_TEMPERATURE", 0.5
    ), patch("models.llm.DEFAULT_MAX_TOKENS", 1000), patch(
        "models.llm.GROQ_API_KEY", "test-api-key"
    ):
        yield


def test_groq_llm_initialization_with_params(mock_config):
    """Test that GroqLLM can be initialized with custom values"""
    llm = GroqLLM(
        model="custom-model", temperature=0.7, max_tokens=2000, api_key="custom-api-key"
    )

    assert llm.model == "custom-model"
    assert llm.temperature == 0.7
    assert llm.max_tokens == 2000
    assert llm.api_key == "custom-api-key"


def test_groq_llm_call(mock_groq, mock_config):
    """Test the _call method of GroqLLM"""
    llm = GroqLLM(model="test-model", temperature=0.5, max_tokens=1000)
    result = llm._call("Test prompt")

    # Check that Groq client was initialized correctly
    mock_groq.assert_called_once_with(api_key="test-api-key")

    # Check that chat.completions.create was called with the right arguments
    mock_groq.return_value.chat.completions.create.assert_called_once_with(
        messages=[{"role": "user", "content": "Test prompt"}],
        model="test-model",
        temperature=0.5,
        max_tokens=1000,
    )

    # Check the return value
    assert result == "This is a test response"


def test_groq_llm_call_with_custom_api_key(mock_groq, mock_config):
    """Test that _call uses the instance's API key when provided"""
    llm = GroqLLM(api_key="instance-api-key")
    llm._call("Test prompt")

    # Check that Groq client was initialized with the instance API key
    mock_groq.assert_called_once_with(api_key="instance-api-key")


def test_groq_llm_type():
    """Test that _llm_type returns the expected value"""
    llm = GroqLLM()
    assert llm._llm_type == "groq-llm"
