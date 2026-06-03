"""
RAG — Chunking Module
Uses LangChain RecursiveCharacterTextSplitter
Spec: chunk_size=500, chunk_overlap=100
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str) -> list[str]:
    """
    Split raw document text into overlapping chunks.
    Returns list of chunk strings.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    return [c.strip() for c in chunks if c.strip()]
