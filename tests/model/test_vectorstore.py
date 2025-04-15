# tests/test_vectorstore.py
import pytest
import os
from unittest.mock import patch, MagicMock, Mock
from langchain.schema import Document

from models.vectorstore import VectorstoreManager


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model"""
    with patch("models.vectorstore.get_embedding_model") as mock_get_embedding:
        mock_model = MagicMock()
        mock_get_embedding.return_value = mock_model
        yield mock_model


@pytest.fixture
def mock_text_splitter():
    """Mock RecursiveCharacterTextSplitter"""
    with patch(
        "models.vectorstore.RecursiveCharacterTextSplitter"
    ) as mock_splitter_class:
        mock_splitter = MagicMock()
        mock_splitter_class.return_value = mock_splitter

        # Set up the split_documents method
        mock_split_docs = [
            Document(page_content="Chunk 1", metadata={"source": "doc1"}),
            Document(page_content="Chunk 2", metadata={"source": "doc1"}),
            Document(page_content="Chunk 3", metadata={"source": "doc2"}),
        ]
        mock_splitter.split_documents.return_value = mock_split_docs

        yield mock_splitter


@pytest.fixture
def mock_faiss():
    """Mock FAISS class"""
    with patch("models.vectorstore.FAISS") as mock_faiss_class:
        mock_instance = MagicMock()
        mock_faiss_class.from_documents.return_value = mock_instance
        mock_faiss_class.load_local.return_value = mock_instance
        yield mock_faiss_class


@pytest.fixture
def mock_os_path():
    """Mock os.path functions"""
    with patch("models.vectorstore.os.path.exists") as mock_exists, patch(
        "models.vectorstore.os.path.dirname"
    ) as mock_dirname, patch("models.vectorstore.os.makedirs") as mock_makedirs:

        # Set up dirname to return a test path
        mock_dirname.return_value = "/test/path"

        yield {
            "exists": mock_exists,
            "dirname": mock_dirname,
            "makedirs": mock_makedirs,
        }


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        Document(page_content="Document 1 content", metadata={"source": "doc1"}),
        Document(page_content="Document 2 content", metadata={"source": "doc2"}),
    ]


@pytest.fixture
def mock_config():
    """Mock config values"""
    with patch("models.vectorstore.CHUNK_SIZE", 1000), patch(
        "models.vectorstore.CHUNK_OVERLAP", 100
    ):
        yield


def test_vectorstore_manager_initialization(mock_embedding_model):
    """Test initialization of VectorstoreManager"""
    manager = VectorstoreManager("test_code")

    # Check attributes
    assert manager.law_code_name == "test_code"
    assert "test_code" in manager.index_path
    assert manager.embedding_model == mock_embedding_model


def test_create_vectorstore(
    mock_embedding_model,
    mock_text_splitter,
    mock_faiss,
    mock_os_path,
    sample_documents,
    mock_config,
):
    """Test create_vectorstore method"""
    manager = VectorstoreManager("test_code")
    result = manager.create_vectorstore(sample_documents)

    # Check that text splitter was initialized correctly
    mock_text_splitter.split_documents.assert_called_once_with(sample_documents)

    # Check that FAISS.from_documents was called with the right arguments
    mock_faiss.from_documents.assert_called_once()
    args, kwargs = mock_faiss.from_documents.call_args
    assert args[0] == mock_text_splitter.split_documents.return_value
    assert args[1] == mock_embedding_model

    # Check that the vectorstore was saved
    mock_os_path["makedirs"].assert_called_once_with("/test/path", exist_ok=True)
    result.save_local.assert_called_once_with(manager.index_path)

    # Check the return value
    assert result == mock_faiss.from_documents.return_value


def test_load_vectorstore_existing(mock_embedding_model, mock_faiss, mock_os_path):
    """Test load_vectorstore when the index exists"""
    # Setup mock to indicate the index exists
    mock_os_path["exists"].return_value = True

    manager = VectorstoreManager("test_code")
    result = manager.load_vectorstore()

    # Check that exists was called with the right path
    mock_os_path["exists"].assert_called_once_with(manager.index_path)

    # Check that FAISS.load_local was called with the right arguments
    mock_faiss.load_local.assert_called_once_with(
        manager.index_path, mock_embedding_model, allow_dangerous_deserialization=True
    )

    # Check the return value
    assert result == mock_faiss.load_local.return_value


def test_load_vectorstore_not_existing(mock_embedding_model, mock_faiss, mock_os_path):
    """Test load_vectorstore when the index doesn't exist"""
    # Setup mock to indicate the index doesn't exist
    mock_os_path["exists"].return_value = False

    manager = VectorstoreManager("test_code")

    # Check that it raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        manager.load_vectorstore()

    # Check that exists was called with the right path
    mock_os_path["exists"].assert_called_once_with(manager.index_path)

    # Check that FAISS.load_local was not called
    mock_faiss.load_local.assert_not_called()


def test_get_vectorstore_existing(
    mock_embedding_model, mock_faiss, mock_os_path, sample_documents
):
    """Test get_vectorstore when the index exists"""
    # Setup mock to indicate the index exists
    mock_os_path["exists"].return_value = True

    manager = VectorstoreManager("test_code")
    # Create a spy on the load_vectorstore method
    with patch.object(
        manager, "load_vectorstore", wraps=manager.load_vectorstore
    ) as spy_load:
        with patch.object(manager, "create_vectorstore") as mock_create:
            result = manager.get_vectorstore(sample_documents)

    # Check that load_vectorstore was called
    spy_load.assert_called_once()

    # Check that create_vectorstore was not called
    mock_create.assert_not_called()

    # Check the return value
    assert result == mock_faiss.load_local.return_value


def test_get_vectorstore_not_existing_with_documents(
    mock_embedding_model, mock_faiss, mock_os_path, sample_documents
):
    """Test get_vectorstore when the index doesn't exist but documents are provided"""
    # Setup mock to indicate the index doesn't exist
    mock_os_path["exists"].return_value = False

    manager = VectorstoreManager("test_code")
    # Create spies on the methods
    with patch.object(
        manager, "load_vectorstore", side_effect=FileNotFoundError
    ) as spy_load:
        with patch.object(
            manager, "create_vectorstore", wraps=manager.create_vectorstore
        ) as spy_create:
            result = manager.get_vectorstore(sample_documents)

    # Check that load_vectorstore was called
    spy_load.assert_called_once()

    # Check that create_vectorstore was called with the right arguments
    spy_create.assert_called_once_with(sample_documents)

    # Check the return value
    assert result == mock_faiss.from_documents.return_value


def test_get_vectorstore_not_existing_without_documents(
    mock_embedding_model, mock_faiss, mock_os_path
):
    """Test get_vectorstore when the index doesn't exist and no documents are provided"""
    # Setup mock to indicate the index doesn't exist
    mock_os_path["exists"].return_value = False

    manager = VectorstoreManager("test_code")
    # Create spies on the methods
    with patch.object(manager, "load_vectorstore", side_effect=FileNotFoundError):
        # Check that it raises ValueError
        with pytest.raises(ValueError) as excinfo:
            manager.get_vectorstore()

        # Check the error message
        assert "Documents must be provided" in str(excinfo.value)
