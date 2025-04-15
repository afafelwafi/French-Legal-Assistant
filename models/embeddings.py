# models/embeddings.py
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL


def get_embedding_model():
    """
    Create and return the embedding model.

    Returns:
        HuggingFaceEmbeddings model
    """
    # Determine the device (GPU if available, otherwise CPU)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Initialize the embedding model
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": device},
    )

    return embedding_model
