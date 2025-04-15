# tests/data/test_loader.py

import os
import json
import pytest
import asyncio
from unittest.mock import patch, mock_open
from langchain.schema import Document
from data.loader import LegalDataLoader


@pytest.mark.asyncio
async def test_load_single_law_code(monkeypatch):
    # Sample mock data structure
    sample_json = {
        "content": [
            {
                "section_data": {"title": "Partie législative"},
                "articles": [
                    {"content": "<p>Text here</p>", "num": "L1", "etat": "VIGUEUR"}
                ],
                "subsections": [],
            }
        ]
    }

    # Patch os.path.exists to simulate file presence
    monkeypatch.setattr(os.path, "exists", lambda path: True)

    # Patch json.load and open
    m_open = mock_open(read_data=json.dumps(sample_json))
    monkeypatch.setattr("builtins.open", m_open)

    # Instantiate loader and call `load`
    loader = LegalDataLoader("dummy_law")
    documents = await loader.load()

    assert len(documents) == 1
    assert isinstance(documents[0], Document)
    assert "Text here" in documents[0].page_content
    assert documents[0].metadata["num"] == "L1"


@pytest.mark.asyncio
async def test_load_all(monkeypatch):
    files = ["code_a.json", "code_b.json"]
    law_codes = ["code_a", "code_b"]

    # Patch directory listing
    monkeypatch.setattr(os, "listdir", lambda _: files)
    monkeypatch.setattr(os.path, "exists", lambda _: True)

    sample_json = {
        "content": [
            {
                "section_data": {"title": "Section"},
                "articles": [
                    {"content": "Article content", "num": "1", "etat": "VIGUEUR"}
                ],
                "subsections": [],
            }
        ]
    }

    # Patch open and json.load
    m_open = mock_open(read_data=json.dumps(sample_json))
    monkeypatch.setattr("builtins.open", m_open)

    # Patch loader.load to avoid re-testing internals
    monkeypatch.setattr(LegalDataLoader, "load", lambda self: asyncio.Future())
    for i, code in enumerate(law_codes):
        fut = asyncio.Future()
        fut.set_result([Document(page_content=f"Content {code}", metadata={})])
        monkeypatch.setattr(LegalDataLoader(code), "load", lambda fut=fut: fut)

    result = await LegalDataLoader.load_all()

    assert len(result) == 2
    assert "code_a" in result
    assert isinstance(result["code_b"][0], Document)


def test_list_available_law_codes(monkeypatch):
    mock_files = ["code_civil.json", "code_penal.json", "README.md"]

    monkeypatch.setattr(os.path, "exists", lambda _: True)
    monkeypatch.setattr(os, "listdir", lambda _: mock_files)

    result = LegalDataLoader.list_available_law_codes()
    assert set(result) == {"code_civil", "code_penal"}
