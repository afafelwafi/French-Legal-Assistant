# tests/test_embeddings.py
import pytest
from unittest.mock import patch, MagicMock

import torch
from models.embeddings import get_embedding_model


@pytest.fixture
def mock_huggingface_embeddings():
    """Mock HuggingFaceEmbeddings class"""
    with patch("models.embeddings.HuggingFaceEmbeddings") as mock_embeddings:
        mock_instance = MagicMock()
        mock_embeddings.return_value = mock_instance
        yield mock_embeddings


@pytest.fixture
def mock_config():
    """Mock config values"""
    with patch("models.embeddings.EMBEDDING_MODEL", "test-embedding-model"):
        yield


def test_get_embedding_model_cuda_available(mock_huggingface_embeddings, mock_config):
    """Test get_embedding_model when CUDA is available"""
    # Mock torch.cuda.is_available to return True
    with patch("torch.cuda.is_available", return_value=True):
        embedding_model = get_embedding_model()

        # Check that HuggingFaceEmbeddings was called with the right arguments
        mock_huggingface_embeddings.assert_called_once_with(
            model_name="test-embedding-model", model_kwargs={"device": "cuda"}
        )


def test_get_embedding_model_cuda_not_available(
    mock_huggingface_embeddings, mock_config
):
    """Test get_embedding_model when CUDA is not available"""
    # Mock torch.cuda.is_available to return False
    with patch("torch.cuda.is_available", return_value=False):
        embedding_model = get_embedding_model()

        # Check that HuggingFaceEmbeddings was called with the right arguments
        mock_huggingface_embeddings.assert_called_once_with(
            model_name="test-embedding-model", model_kwargs={"device": "cpu"}
        )


def test_embedding_model_return_value(mock_huggingface_embeddings, mock_config):
    """Test that get_embedding_model returns the expected embedding model"""
    mock_model = MagicMock()
    mock_huggingface_embeddings.return_value = mock_model

    result = get_embedding_model()

    assert result == mock_model
    mock_huggingface_embeddings.assert_called_once()
