# data/loader.py
import json
import os
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from config import FOLDER_NAME


class LegalDataLoader:
    """Loader that loads legal documents from JSON files in the legifrance directory."""

    def __init__(self, law_code_name: str):
        """
        Initialize with the name of the law code to load.

        Args:
            law_code_name: Name of the law code file to load (without .json extension)
        """
        self.law_code_name = law_code_name.replace(" ", "_").lower()
        self.base_path = os.path.join(os.path.dirname(__file__), FOLDER_NAME)
        self.file_path = os.path.join(self.base_path, f"{self.law_code_name}.json")

    def extract_articles_from_node(self, node, path=None):
        path = path or []
        documents = []

        # Get current path
        title = node.get("section_data", {}).get("title")
        if title:
            path = path + [title]

        # Extract articles
        for article in node.get("articles", []):
            if article.get("content"):
                metadata = {
                    "pathTitle": " > ".join(path),
                    "num": article.get("num"),
                    "etat": article.get("etat"),
                }
                documents.append(
                    Document(page_content=article["content"], metadata=metadata)
                )

        # Recurse into subsections
        for subsection in node.get("subsections", []):
            documents.extend(self.extract_articles_from_node(subsection, path))

        return documents

    async def load(self) -> List[Document]:
        """
        Load documents from the JSON file for the specified law code.

        Returns:
            List of Document objects
        """
        documents = []

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Law code file not found: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Process each article in the JSON data
        # Adapt this part based on the actual structure of your JSON files
        for item in data.get("content", []):
            # Extract article ID and content
            documents.extend(self.extract_articles_from_node(item))

        return documents

    @staticmethod
    async def load_all(law_codes: List[str] = None) -> Dict[str, List[Document]]:
        """
        Load documents from all available law codes or from a specified list.

        Args:
            law_codes: Optional list of law code names to load

        Returns:
            Dictionary mapping law code names to lists of documents
        """
        base_path = os.path.join(os.path.dirname(__file__), "legifrance")

        # If no law codes specified, load all available ones
        if law_codes is None:
            law_codes = [
                os.path.splitext(f)[0]
                for f in os.listdir(base_path)
                if f.endswith(".json")
            ]

        result = {}
        for law_code in law_codes:
            loader = LegalDataLoader(law_code)
            try:
                documents = await loader.load()
                result[law_code] = documents
            except FileNotFoundError:
                print(f"Warning: Law code file not found for {law_code}")
                continue

        return result

    @staticmethod
    def list_available_law_codes() -> List[str]:
        """
        List all available law codes in the legifrance directory.

        Returns:
            List of available law code names (without .json extension)
        """
        base_path = os.path.join(os.path.dirname(__file__), "legifrance")
        if not os.path.exists(base_path):
            return []

        return [
            os.path.splitext(f)[0] for f in os.listdir(base_path) if f.endswith(".json")
        ]
