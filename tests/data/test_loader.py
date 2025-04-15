# tests/test_legal_data_loader.py
import os
import json
import pytest
from unittest.mock import patch, mock_open
from langchain.schema import Document

# Import the code to be tested (adjust the import path as needed)
from data.loader import LegalDataLoader


@pytest.fixture
def mock_folder_name():
    """Mock the FOLDER_NAME from config"""
    with patch("data.loader.FOLDER_NAME", "test_legifrance"):
        yield "test_legifrance"


@pytest.fixture
def sample_law_code_data():
    """Sample data structure for a law code"""
    return {
        "content": [
            {
                "section_data": {"title": "TITRE I"},
                "articles": [
                    {"num": "1", "content": "Article 1 content", "etat": "VIGUEUR"},
                    {"num": "2", "content": "Article 2 content", "etat": "ABROGE"},
                ],
                "subsections": [
                    {
                        "section_data": {"title": "CHAPITRE I"},
                        "articles": [
                            {
                                "num": "3",
                                "content": "Article 3 content",
                                "etat": "VIGUEUR",
                            }
                        ],
                        "subsections": [],
                    }
                ],
            }
        ]
    }


@pytest.mark.asyncio
async def test_load_single_law_code(mock_folder_name, sample_law_code_data):
    """Test loading a single law code"""
    # Setup mocks
    law_code_name = "code_civil"
    expected_file_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        mock_folder_name,
        f"{law_code_name}.json",
    )

    # Mock file opening and reading
    m = mock_open(read_data=json.dumps(sample_law_code_data))
    with patch("builtins.open", m), patch("os.path.exists", return_value=True):
        loader = LegalDataLoader(law_code_name)
        documents = await loader.load()

    # Check results
    assert len(documents) == 3

    # Check first document
    assert documents[0].page_content == "Article 1 content"
    assert documents[0].metadata["num"] == "1"
    assert documents[0].metadata["etat"] == "VIGUEUR"
    assert documents[0].metadata["pathTitle"] == "TITRE I"

    # Check nested document
    assert documents[2].page_content == "Article 3 content"
    assert documents[2].metadata["pathTitle"] == "TITRE I > CHAPITRE I"


@pytest.mark.asyncio
async def test_load_nonexistent_file(mock_folder_name):
    """Test handling of nonexistent file"""
    with patch("os.path.exists", return_value=False):
        loader = LegalDataLoader("nonexistent_code")
        with pytest.raises(FileNotFoundError):
            await loader.load()


@pytest.mark.asyncio
async def test_load_all_law_codes(mock_folder_name, sample_law_code_data):
    """Test loading multiple law codes"""
    law_codes = ["code_civil", "code_penal"]

    # Define multiple open mocks to handle different files
    def mock_open_factory(read_data):
        return mock_open(read_data=read_data)

    # Create a side effect that returns different mock objects for different file paths
    def side_effect(file_path, *args, **kwargs):
        if "code_civil.json" in file_path:
            return mock_open_factory(json.dumps(sample_law_code_data))()
        elif "code_penal.json" in file_path:
            return mock_open_factory(json.dumps(sample_law_code_data))()
        return mock_open()()

    # Mock file operations
    with patch("builtins.open", side_effect=side_effect), patch(
        "os.path.exists", return_value=True
    ):
        result = await LegalDataLoader.load_all(law_codes)

    # Check results
    assert len(result) == 2
    assert "code_civil" in result
    assert "code_penal" in result
    assert len(result["code_civil"]) == 3
    assert len(result["code_penal"]) == 3


def test_list_available_law_codes(mock_folder_name):
    """Test listing available law codes"""
    # Mock directory listing
    mock_files = ["code_civil.json", "code_penal.json", "other_file.txt"]

    with patch("os.listdir", return_value=mock_files), patch(
        "os.path.exists", return_value=True
    ):
        available_codes = LegalDataLoader.list_available_law_codes()

    # Check results
    assert len(available_codes) == 2
    assert "code_civil" in available_codes
    assert "code_penal" in available_codes
    assert "other_file" not in available_codes


def test_list_available_law_codes_empty_dir(mock_folder_name):
    """Test listing available law codes from nonexistent directory"""
    with patch("os.path.exists", return_value=False):
        available_codes = LegalDataLoader.list_available_law_codes()

    # Check results
    assert available_codes == []


def test_extract_articles_from_node():
    """Test the recursive article extraction from nodes"""
    # Create a test node
    test_node = {
        "section_data": {"title": "MAIN SECTION"},
        "articles": [
            {"num": "1", "content": "Main article content", "etat": "VIGUEUR"},
        ],
        "subsections": [
            {
                "section_data": {"title": "SUB SECTION"},
                "articles": [
                    {"num": "2", "content": "Sub article content", "etat": "VIGUEUR"},
                ],
                "subsections": [
                    {
                        "section_data": {"title": "NESTED SECTION"},
                        "articles": [
                            {
                                "num": "3",
                                "content": "Nested article content",
                                "etat": "VIGUEUR",
                            },
                        ],
                        "subsections": [],
                    }
                ],
            }
        ],
    }

    loader = LegalDataLoader("test_code")
    documents = loader.extract_articles_from_node(test_node)

    # Check results
    assert len(documents) == 3

    # Check paths
    assert documents[0].metadata["pathTitle"] == "MAIN SECTION"
    assert documents[1].metadata["pathTitle"] == "MAIN SECTION > SUB SECTION"
    assert (
        documents[2].metadata["pathTitle"]
        == "MAIN SECTION > SUB SECTION > NESTED SECTION"
    )

    # Check article numbers
    assert documents[0].metadata["num"] == "1"
    assert documents[1].metadata["num"] == "2"
    assert documents[2].metadata["num"] == "3"
