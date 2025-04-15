# tests/test_utils.py
import pytest
import json
import hashlib
from unittest.mock import patch, MagicMock
from utils.cache import RedisCache
from utils.logging import setup_logging


class TestRedisCache:
    """Tests for the RedisCache class."""

    @pytest.fixture
    def redis_mock(self):
        """Create a mock for Redis."""
        with patch("utils.cache.redis.Redis") as mock:
            yield mock.return_value

    def test_generate_key(self):
        """Test that _generate_key generates the expected key."""
        cache = RedisCache(prefix="test")
        key_params = {"a": 1, "b": "test", "c": [1, 2, 3]}

        # Generate key
        key = cache._generate_key(key_params)

        # Calculate expected key
        param_str = json.dumps(key_params, sort_keys=True)
        expected_hash = hashlib.md5(param_str.encode()).hexdigest()
        expected_key = f"test:{expected_hash}"

        assert key == expected_key

    def test_get(self, redis_mock):
        """Test that get returns the expected value."""
        # Set up mock
        redis_mock.get.return_value = "cached_value"

        # Create cache and call get
        cache = RedisCache()
        result = cache.get({"key": "value"})

        # Assertions
        assert result == "cached_value"
        redis_mock.get.assert_called_once()

    def test_set(self, redis_mock):
        """Test that set calls Redis with the right parameters."""
        # Set up mock
        redis_mock.set.return_value = True

        # Create cache and call set
        cache = RedisCache()
        cache.ttl = 3600  # Set TTL to 1 hour
        result = cache.set({"key": "value"}, "value_to_cache")

        # Assertions
        assert result is True
        redis_mock.set.assert_called_once()
        call_args = redis_mock.set.call_args
        assert call_args[0][1] == "value_to_cache"
        assert call_args[1]["ex"] == 3600

    def test_delete(self, redis_mock):
        """Test that delete calls Redis with the right parameters."""
        # Set up mock
        redis_mock.delete.return_value = 1

        # Create cache and call delete
        cache = RedisCache()
        result = cache.delete({"key": "value"})

        # Assertions
        assert result is True
        redis_mock.delete.assert_called_once()

    def test_flush(self, redis_mock):
        """Test that flush calls Redis with the right parameters."""
        # Set up mock
        redis_mock.keys.return_value = ["key1", "key2"]
        redis_mock.delete.return_value = 2

        # Create cache and call flush
        cache = RedisCache(prefix="test")
        result = cache.flush()

        # Assertions
        assert result == 2
        redis_mock.keys.assert_called_once_with("test:*")
        redis_mock.delete.assert_called_once_with("key1", "key2")


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
