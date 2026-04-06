"""
config.py — Central configuration for the RAG Agent.
All settings are defined here; import from this file everywhere else.
"""

import os

# ── Elasticsearch ────────────────────────────────────────────────────────────
ES_HOST  = os.getenv("ES_HOST",  "http://localhost:9200")
ES_INDEX = os.getenv("ES_INDEX", "my_knowledge_base")

# ── Embedding model (local, no API needed) ───────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_DIMS     = 384   # Must match the model above

# ── File paths ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Create the data folder on first run
os.makedirs(DATA_DIR, exist_ok=True)
