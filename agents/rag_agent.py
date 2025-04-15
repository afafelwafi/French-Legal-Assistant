# agents/rag_agent.py
from langchain.chains import RetrievalQA
from langchain.tools import Tool
from models.llm import GroqLLM
from models.vectorstore import VectorstoreManager
from utils.prompts import LEGAL_RAG_PROMPT


def create_rag_tool(law_code_name: str, documents=None):
    """
    Create a RAG tool for the specified law code.

    Args:
        law_code_name: Name of the law code
        documents: Optional documents to create the vectorstore

    Returns:
        Tool for RAG-based legal research
    """
    # Initialize LLM
    llm = GroqLLM()

    # Get vectorstore and retriever
    vectorstore_manager = VectorstoreManager(law_code_name)

    try:
        # Try to load existing vectorstore first
        vectorstore = vectorstore_manager.load_vectorstore()
    except FileNotFoundError:
        # If not found and documents are provided, create new vectorstore
        if documents is None:
            raise ValueError(
                f"No existing vectorstore found for {law_code_name} and no documents provided"
            )
        vectorstore = vectorstore_manager.create_vectorstore(documents)

    retriever = vectorstore.as_retriever()

    # Create RAG chain
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever, chain_type_kwargs={"prompt": LEGAL_RAG_PROMPT}
    )

    # Create tool
    rag_tool = Tool(
        name=f"{law_code_name}_rag",
        func=rag_chain.run,
        description=f"Recherche juridique basée sur le code {law_code_name} français.",
    )

    return rag_tool
