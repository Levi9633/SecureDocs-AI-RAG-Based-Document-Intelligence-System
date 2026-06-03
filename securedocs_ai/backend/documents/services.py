"""
Documents App — Service Layer
Handles the full document processing pipeline:
  Upload → Save → Extract → Clean → Chunk → Embed → FAISS → SQLite

Error handling per spec:
  - Invalid file type
  - Empty file
  - Corrupted file
"""

import os
import re

import pdfplumber
from docx import Document as DocxDocument
from django.conf import settings

from rag.chunking import chunk_text
from rag.embeddings import embed_texts
from rag.vector_store import add_to_index, delete_document_chunks

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


# ─────────────────────────────────────────────────────────────────
# TEXT EXTRACTION
# ─────────────────────────────────────────────────────────────────

def extract_text_from_pdf(filepath: str) -> tuple[str, list]:
    """
    Extract text from PDF using pdfplumber.
    Returns (full_text, pages_list) where pages_list[i] = page_number for chunk i.
    """
    full_text = ""
    page_texts = []

    try:
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    page_texts.append((page_num, text))
                    full_text += f"\n{text}"
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")

    return full_text, page_texts


def extract_text_from_docx(filepath: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        doc = DocxDocument(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Failed to read DOCX: {str(e)}")


def extract_text_from_txt(filepath: str) -> str:
    """Extract text from plain TXT file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        raise ValueError(f"Failed to read TXT: {str(e)}")


def extract_text(filepath: str, filename: str) -> tuple[str, list]:
    """
    Route extraction to correct handler based on file extension.
    Returns (full_text, page_info) — page_info may be empty for non-PDF.
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    elif ext == '.docx':
        text = extract_text_from_docx(filepath)
        return text, []
    elif ext == '.txt':
        text = extract_text_from_txt(filepath)
        return text, []
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: PDF, DOCX, TXT")


# ─────────────────────────────────────────────────────────────────
# TEXT CLEANING
# ─────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Clean raw extracted text per spec:
    - Remove extra spaces
    - Remove tabs
    - Remove multiple consecutive newlines
    """
    # Replace tabs with space
    text = text.replace('\t', ' ')
    # Replace multiple spaces with single
    text = re.sub(r' {2,}', ' ', text)
    # Replace 3+ newlines with 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


# ─────────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────────

def validate_file(file) -> None:
    """
    Validate uploaded file. Raises ValueError for invalid files.
    Checks: file type, empty file.
    """
    if not file:
        raise ValueError("No file provided.")

    filename = file.name
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Invalid file type '{ext}'. Allowed types: PDF, DOCX, TXT"
        )

    # Check file is not empty
    if file.size == 0:
        raise ValueError("The uploaded file is empty.")


# ─────────────────────────────────────────────────────────────────
# FULL PROCESSING PIPELINE
# ─────────────────────────────────────────────────────────────────

def process_document(doc_instance) -> dict:
    """
    Full document processing pipeline per spec:
    1. Extract text (PDF/DOCX/TXT)
    2. Clean text
    3. Chunk text (chunk_size=500, overlap=100)
    4. Generate embeddings (all-MiniLM-L6-v2)
    5. Store in FAISS with metadata
    6. Return summary info

    Args:
        doc_instance: Document model instance (already saved with filepath)

    Returns:
        {'chunks': N, 'status': 'success'}
    """
    filepath = doc_instance.filepath
    filename = doc_instance.filename

    # Step 1: Extract
    raw_text, page_info = extract_text(filepath, filename)

    if not raw_text.strip():
        raise ValueError("No text could be extracted from the document. It may be empty or image-only.")

    # Step 2 & 3: Clean and Chunk
    chunks = []
    chunk_pages = []

    if page_info:
        # PDF page-by-page processing for perfect page alignment and speed
        for pnum, ptext in page_info:
            cleaned_page = clean_text(ptext)
            if cleaned_page:
                page_chunks = chunk_text(cleaned_page)
                chunks.extend(page_chunks)
                chunk_pages.extend([pnum] * len(page_chunks))
    else:
        # TXT or DOCX
        cleaned = clean_text(raw_text)
        chunks = chunk_text(cleaned)
        chunk_pages = [None] * len(chunks)

    if not chunks:
        raise ValueError("Document produced no text chunks after processing.")

    # Step 4: Generate embeddings
    embeddings = embed_texts(chunks)

    # Step 5: Store in FAISS
    add_to_index(
        embeddings=embeddings,
        chunks=chunks,
        doc_metadata={
            'document_id': doc_instance.id,
            'filename': filename,
            'pages': chunk_pages,
        }
    )

    return {'chunks': len(chunks), 'status': 'success'}


def remove_document_from_index(filename: str) -> None:
    """Remove all FAISS vectors for a given document filename."""
    delete_document_chunks(filename)
