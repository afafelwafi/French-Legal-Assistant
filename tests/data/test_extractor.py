import os
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
import asyncio

# Import the functions to test
from data.extractor import fetch_and_save_code, main

# Test data
MOCK_CODE_NAME = "Code civil"
MOCK_FOLDER = "test_codes"
MOCK_CODE_DATA = {
    "articles": [{"id": "LEGIARTI000006419305", "content": "Test content"}]
}


@pytest.fixture
def mock_config():
    with patch("data.extractor.FOLDER_NAME", MOCK_FOLDER):
        with patch("data.extractor.CODES", ["Code civil", "Code pénal"]):
            yield


@pytest.fixture
def mock_os_makedirs():
    with patch("os.makedirs") as mock:
        yield mock


@pytest.fixture
def mock_recherche_code():
    with patch("data.extractor.recherche_CODE") as mock:
        mock.return_value = MOCK_CODE_DATA
        yield mock


@pytest.mark.asyncio
async def test_fetch_and_save_code(mock_config, mock_os_makedirs, mock_recherche_code):
    # Setup
    expected_filename = os.path.join(MOCK_FOLDER, "code_civil.json")

    # Use mock_open to mock file operations
    m = mock_open()
    with patch("builtins.open", m):
        # Execute
        await fetch_and_save_code(MOCK_CODE_NAME)

    # Assert
    mock_recherche_code.assert_called_once_with(
        code_name=MOCK_CODE_NAME, formatter=True
    )
    m.assert_called_once_with(expected_filename, "w", encoding="utf-8")
    handle = m()
    # Check that json.dump was called with the right arguments
    assert handle.write.called


@pytest.mark.asyncio
async def test_fetch_and_save_code_no_data(mock_config, mock_recherche_code):
    # Setup - research returns no data
    mock_recherche_code.return_value = None

    # Execute
    with patch("builtins.open", mock_open()) as m:
        await fetch_and_save_code(MOCK_CODE_NAME)

    # Assert
    mock_recherche_code.assert_called_once()
    # File should not be opened if there's no data
    m.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_and_save_code_exception(mock_config):
    # Setup - research raises exception
    with patch("data.extractor.recherche_CODE", side_effect=Exception("Test error")):
        # Execute
        with patch("builtins.open", mock_open()) as m:
            await fetch_and_save_code(MOCK_CODE_NAME)

        # Assert - file should not be opened if there's an exception
        m.assert_not_called()


@pytest.mark.asyncio
async def test_main(mock_config, mock_os_makedirs):
    # Setup
    with patch("data.extractor.CODES", ["Code civil", "Code pénal"]) as mock_codes:
        with patch("data.extractor.fetch_and_save_code") as mock_fetch:
            mock_fetch.return_value = asyncio.Future()
            mock_fetch.return_value.set_result(None)

            # Execute
            await main()

            # Assert
            assert mock_fetch.call_count == 2  # Two codes in the mock CODES list
            # Check it was called with the right code names
            mock_fetch.assert_any_call("Code civil")
            mock_fetch.assert_any_call("Code pénal")
