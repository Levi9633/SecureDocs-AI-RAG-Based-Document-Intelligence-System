"""
RAG — Retrieval Module
Workflow: Question → embed → FAISS search → top 4 chunks + metadata
Per spec: retrieve top 4 chunks with document name and page number
"""

from .embeddings import embed_query
from .vector_store import search_index


def retrieve_chunks(question: str, k: int = 4) -> list[dict]:
    """
    Full retrieval pipeline:
    1. Embed the user question
    2. Search FAISS for top-k similar chunks
    3. Return list of {chunk, filename, page} dicts

    Returns [] if no documents are indexed.
    """
    query_embedding = embed_query(question)
    results = search_index(query_embedding, k=k)
    return results


def format_retrieved_context(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a readable context block for the prompt.
    Each chunk shows: [Source: filename, Page: N]\n<chunk text>
    """
    if not chunks:
        return "No relevant document context found."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        source_line = f"[Source: {chunk.get('filename', 'Unknown')}"
        if chunk.get('page'):
            source_line += f", Page {chunk['page']}"
        source_line += "]"
        parts.append(f"{source_line}\n{chunk.get('chunk', '')}")

    return "\n\n".join(parts)


def extract_sources(chunks: list[dict]) -> list[dict]:
    """
    Extract unique source citations from retrieved chunks.
    Returns list of {filename, page} dicts for frontend display.
    """
    seen = set()
    sources = []
    for chunk in chunks:
        key = (chunk.get('filename', ''), chunk.get('page'))
        if key not in seen:
            seen.add(key)
            sources.append({
                'filename': chunk.get('filename', ''),
                'page': chunk.get('page'),
            })
    return sources
