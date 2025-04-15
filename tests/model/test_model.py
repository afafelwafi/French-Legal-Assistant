# tests/test_models.py
import pytest
from unittest.mock import patch, MagicMock
from models.llm import GroqLLM
from models.embeddings import get_embedding_model


class TestGroqLLM:
    """Tests for the GroqLLM class."""

    @patch("models.llm.Groq")
    def test_call(self, mock_groq):
        """Test that _call method returns expected content."""
        # Set up mock
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_message.content = "Test response"
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_groq.return_value = mock_client

        # Create LLM and test
        llm = GroqLLM()
        result = llm._call("Test prompt")

        # Assertions
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["messages"][0]["content"] == "Test prompt"
        assert call_kwargs["model"] == "llama3-8b-8192"

    def test_llm_type(self):
        """Test that _llm_type property returns expected value."""
        llm = GroqLLM()
        assert llm._llm_type == "groq-llm"


@patch("models.embeddings.HuggingFaceEmbeddings")
def test_get_embedding_model(mock_huggingface):
    """Test that get_embedding_model returns the expected model."""
    # Set up mock
    mock_model = MagicMock()
    mock_huggingface.return_value = mock_model

    # Call the function
    model = get_embedding_model()

    # Assertions
    assert model == mock_model
    mock_huggingface.assert_called_once()
    call_kwargs = mock_huggingface.call_args.kwargs
    assert "sentence-transformers/" in call_kwargs["model_name"]
