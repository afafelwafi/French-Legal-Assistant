# tests/test_utils.py
from unittest.mock import patch, MagicMock
from utils.logging import setup_logging


@patch("utils.logging.logging")
def test_setup_logging(mock_logging):
    """Test that setup_logging configures a logger with the right handlers."""
    # Set up mocks
    mock_logger = MagicMock()
    mock_logging.getLogger.return_value = mock_logger
    mock_stream_handler = MagicMock()
    mock_logging.StreamHandler.return_value = mock_stream_handler

    # Call the function
    logger = setup_logging("test_logger")

    # Assertions
    assert logger == mock_logger
    mock_logging.getLogger.assert_called_once_with("test_logger")
    mock_logger.setLevel.assert_called_once()
    mock_logging.StreamHandler.assert_called_once()
    mock_stream_handler.setFormatter.assert_called_once()
    mock_logger.addHandler.assert_called_once_with(mock_stream_handler)
