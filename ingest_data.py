"""
ingest_data.py — Document ingestion pipeline (standalone script).

Reads every file in DATA_DIR, splits it into text chunks, encodes each
chunk into a vector, and stores everything in Elasticsearch.

Supported file types: .txt  .pdf  .docx

Usage:
    python ingest_data.py
"""

import os
from PyPDF2 import PdfReader
from docx import Document
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from config import ES_HOST, ES_INDEX, EMBEDDING_MODEL, VECTOR_DIMS, DATA_DIR

# ── Clients ──────────────────────────────────────────────────────────────────
es    = Elasticsearch(ES_HOST)
model = SentenceTransformer(EMBEDDING_MODEL)


# ── Helpers ──────────────────────────────────────────────────────────────────

def extract_text(file_path: str) -> str:
    """Extract raw text from a .txt, .pdf, or .docx file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    if ext == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if ext == ".docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    print(f"⚠️   Skipping unsupported file type: {file_path}")
    return ""


def _ensure_index() -> None:
    """Create the Elasticsearch index with the correct mapping if it doesn't exist."""
    if es.indices.exists(index=ES_INDEX):
        return

    mapping = {
        "mappings": {
            "properties": {
                "text":      {"type": "text"},
                "source":    {"type": "keyword"},
                "embedding": {
                    "type":       "dense_vector",
                    "dims":       VECTOR_DIMS,
                    "index":      True,
                    "similarity": "cosine",
                },
            }
        }
    }
    es.indices.create(index=ES_INDEX, body=mapping)
    print(f"✅  Created index '{ES_INDEX}'")


# ── Main ingestion logic ─────────────────────────────────────────────────────

def run_ingestion() -> None:
    """Ingest all documents found in DATA_DIR into Elasticsearch."""
    _ensure_index()

    files = [f for f in os.listdir(DATA_DIR) if not f.startswith(".")]
    if not files:
        print(f"ℹ️   No files found in {DATA_DIR}. Add documents and re-run.")
        return

    for filename in files:
        file_path = os.path.join(DATA_DIR, filename)
        print(f"\n📄  Processing: {filename}")

        raw_text = extract_text(file_path)
        if not raw_text.strip():
            print(f"    ⚠️  No text extracted — skipping.")
            continue

        # Split into paragraphs; discard very short fragments
        chunks = [c.strip() for c in raw_text.split("\n\n") if len(c.strip()) > 20]
        print(f"    → {len(chunks)} chunk(s) found")

        for chunk in chunks:
            vector = model.encode(chunk).tolist()
            es.index(index=ES_INDEX, document={
                "text":      chunk,
                "embedding": vector,
                "source":    filename,
            })

        print(f"    ✅  Indexed {len(chunks)} chunk(s)")

    print("\n🎉  Ingestion complete — all files stored in Elasticsearch.\n")


if __name__ == "__main__":
    run_ingestion()
