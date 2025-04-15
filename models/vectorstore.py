# models/vectorstore.py
import os
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.embeddings import get_embedding_model
from config import CHUNK_SIZE, CHUNK_OVERLAP


class VectorstoreManager:
    """Manager for creating and loading FAISS vectorstores."""

    def __init__(self, law_code_name: str):
        """
        Initialize with the name of the law code.

        Args:
            law_code_name: Name of the law code
        """
        self.law_code_name = law_code_name
        self.index_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "indices", law_code_name
        )
        self.embedding_model = get_embedding_model()

    def create_vectorstore(self, documents: List[Document]) -> FAISS:
        """
        Create a new vectorstore from the given documents.

        Args:
            documents: List of Document objects

        Returns:
            FAISS vectorstore
        """
        # Split documents into smaller chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        split_docs = splitter.split_documents(documents)

        # Create vectorstore
        vectorstore = FAISS.from_documents(split_docs, self.embedding_model)

        # Save vectorstore
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        vectorstore.save_local(self.index_path)

        return vectorstore

    def load_vectorstore(self) -> FAISS:
        """
        Load an existing vectorstore.

        Returns:
            FAISS vectorstore
        """
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"Vectorstore index not found: {self.index_path}")

        vectorstore = FAISS.load_local(
            self.index_path, self.embedding_model, allow_dangerous_deserialization=True
        )

        return vectorstore

    def get_vectorstore(self, documents: List[Document] = None) -> FAISS:
        """
        Get a vectorstore, creating it if necessary.

        Args:
            documents: List of Document objects

        Returns:
            FAISS vectorstore
        """
        try:
            return self.load_vectorstore()
        except FileNotFoundError:
            if documents is None:
                raise ValueError(
                    "Documents must be provided to create a new vectorstore"
                )
            return self.create_vectorstore(documents)
