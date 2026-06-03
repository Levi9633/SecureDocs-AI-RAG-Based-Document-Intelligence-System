"""
RAG — FAISS Vector Store
Persists FAISS index + metadata to disk.

FAISS stores:
  - embedding vectors (384-dim float32)
  - metadata per chunk: {document, filename, page, chunk_text}

Files on disk:
  - media/faiss_index/index.faiss  — the FAISS index binary
  - media/faiss_index/metadata.pkl — parallel list of chunk metadata dicts
"""

import os
import pickle
import numpy as np
import faiss
from django.conf import settings


def _get_index_dir() -> str:
    """Return the FAISS index directory, creating it if needed."""
    path = str(settings.FAISS_INDEX_PATH)
    os.makedirs(path, exist_ok=True)
    return path


def _index_path() -> str:
    return os.path.join(_get_index_dir(), 'index.faiss')


def _metadata_path() -> str:
    return os.path.join(_get_index_dir(), 'metadata.pkl')


def _load_index():
    """Load FAISS index from disk. Returns (index, metadata_list) or (None, [])."""
    idx_path = _index_path()
    meta_path = _metadata_path()

    if os.path.exists(idx_path) and os.path.exists(meta_path):
        index = faiss.read_index(idx_path)
        with open(meta_path, 'rb') as f:
            metadata = pickle.load(f)
        return index, metadata

    return None, []


def _save_index(index, metadata: list):
    """Persist FAISS index and metadata to disk."""
    faiss.write_index(index, _index_path())
    with open(_metadata_path(), 'wb') as f:
        pickle.dump(metadata, f)


def add_to_index(embeddings: np.ndarray, chunks: list[str], doc_metadata: dict):
    """
    Add new embeddings + chunk metadata to the FAISS index.

    Args:
        embeddings: numpy array (N, 384) float32
        chunks: list of N chunk strings
        doc_metadata: dict with keys 'filename', 'document_id'
          and optionally per-chunk 'pages' list
    """
    index, metadata = _load_index()

    dim = embeddings.shape[1]  # 384

    if index is None:
        # Create a new flat L2 index
        index = faiss.IndexFlatL2(dim)

    index.add(embeddings)

    pages = doc_metadata.get('pages', [None] * len(chunks))

    for i, chunk in enumerate(chunks):
        metadata.append({
            'document_id': doc_metadata.get('document_id'),
            'filename': doc_metadata.get('filename', ''),
            'page': pages[i] if i < len(pages) else None,
            'chunk': chunk,
        })

    _save_index(index, metadata)


def search_index(query_embedding: np.ndarray, k: int = 4) -> list[dict]:
    """
    Search the FAISS index for the top-k most similar chunks.

    Args:
        query_embedding: numpy array (1, 384) float32
        k: number of results to return (default 4 per spec)

    Returns:
        List of metadata dicts for top-k chunks (may be fewer if index is small)
    """
    index, metadata = _load_index()

    if index is None or index.ntotal == 0:
        return []

    actual_k = min(k, index.ntotal)
    distances, indices = index.search(query_embedding, actual_k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(metadata):
            results.append(metadata[idx])

    return results


def delete_document_chunks(filename: str):
    """
    Remove all chunks belonging to a specific document from the FAISS index.
    Rebuilds the index without the deleted document's vectors.
    """
    index, metadata = _load_index()

    if index is None or index.ntotal == 0:
        return

    # Identify which indices to KEEP
    keep_indices = [i for i, m in enumerate(metadata) if m.get('filename') != filename]

    if len(keep_indices) == 0:
        # Delete both files — empty index
        for path in [_index_path(), _metadata_path()]:
            if os.path.exists(path):
                os.remove(path)
        return

    # Reconstruct index from remaining vectors
    all_vectors = index.reconstruct_n(0, index.ntotal)
    kept_vectors = np.array([all_vectors[i] for i in keep_indices], dtype='float32')
    kept_metadata = [metadata[i] for i in keep_indices]

    dim = kept_vectors.shape[1]
    new_index = faiss.IndexFlatL2(dim)
    new_index.add(kept_vectors)

    _save_index(new_index, kept_metadata)


def get_index_size() -> int:
    """Return total number of vectors in the FAISS index."""
    index, _ = _load_index()
    return index.ntotal if index else 0
