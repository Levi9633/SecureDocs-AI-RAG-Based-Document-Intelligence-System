"""
RAG — Embeddings Module
Uses SentenceTransformer: all-MiniLM-L6-v2
Produces 384-dimensional vectors per spec
"""

import numpy as np
from sentence_transformers import SentenceTransformer

# Load model once at module level (cached after first load)
_model = None
 

def get_model() -> SentenceTransformer:
    """Lazy-load the embedding model (singleton)."""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Generate embeddings for a list of text chunks.
    Returns numpy array of shape (N, 384).
    """
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.astype('float32')


def embed_query(query: str) -> np.ndarray:
    """
    Generate embedding for a single query string.
    Returns numpy array of shape (1, 384).
    """
    model = get_model()
    embedding = model.encode([query], convert_to_numpy=True, show_progress_bar=False)
    return embedding.astype('float32')
