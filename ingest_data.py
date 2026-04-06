"""
ingest_data.py — Document ingestion pipeline.

Reads every file in DATA_DIR, splits it into overlapping text chunks,
encodes each chunk into a vector, and stores everything in Elasticsearch.

Supported file types: .txt  .pdf  .docx

Usage:
    python ingest_data.py
"""

import os
import fitz          # PyMuPDF — PDF parsing
import docx          # python-docx — Word parsing
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

import config

# ── Clients (initialised once at import time) ─────────────────────────────────
es    = Elasticsearch(config.ES_HOST)
model = SentenceTransformer(config.EMBEDDING_MODEL)


# ── Text extraction ───────────────────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text() + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text(file_path: str) -> str:
    """Dispatch to the correct extractor based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    if ext == ".txt":
        return extract_text_from_txt(file_path)
    return ""


# ── Chunking ──────────────────────────────────────────────────────────────────

def get_chunks(text: str, size: int = config.CHUNK_SIZE,
               overlap: int = config.CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping windows of `size` characters,
    advancing `size - overlap` characters each step.

    BUG FIX: the original version appended the final slice twice —
    once in the main loop and again in the early-exit branch.
    This version uses a clean while-loop with a single append path.
    """
    if not text:
        return []

    chunks = []
    start  = 0
    step   = size - overlap     # how far to advance each iteration

    while start < len(text):
        chunks.append(text[start : start + size])
        start += step

    return chunks


# ── Index management ──────────────────────────────────────────────────────────

def create_index() -> None:
    """Create the Elasticsearch index with the correct mapping if it doesn't exist."""
    if es.indices.exists(index=config.ES_INDEX):
        return

    mapping = {
        "mappings": {
            "properties": {
                "text":   {"type": "text"},
                "source": {"type": "keyword"},
                "vector": {
                    "type":       "dense_vector",
                    "dims":       config.VECTOR_DIMS,
                    "index":      True,
                    "similarity": "cosine",
                },
            }
        }
    }
    es.indices.create(index=config.ES_INDEX, body=mapping)
    print(f"✅  Created index '{config.ES_INDEX}'")


# ── Main ingestion ────────────────────────────────────────────────────────────

def run_ingestion() -> None:
    """Ingest all supported documents found in DATA_DIR."""
    create_index()

    files = [f for f in os.listdir(config.DATA_DIR) if not f.startswith(".")]
    if not files:
        print(f"ℹ️   No files found in {config.DATA_DIR}/. Add documents and re-run.")
        return

    for filename in files:
        file_path = os.path.join(config.DATA_DIR, filename)
        print(f"\n📄  Processing: {filename}")

        text = extract_text(file_path)
        if not text.strip():
            print("    ⚠️  No text extracted — skipping.")
            continue

        chunks = get_chunks(text)
        print(f"    → {len(chunks)} chunk(s)")

        for i, chunk in enumerate(chunks):
            vector = model.encode(chunk).tolist()
            es.index(index=config.ES_INDEX, document={
                "text":     chunk,
                "vector":   vector,
                "source":   filename,
                "chunk_id": i,
            })

        print(f"    ✅  Indexed {len(chunks)} chunk(s)")

    print("\n🎉  Ingestion complete.\n")


if __name__ == "__main__":
    run_ingestion()
