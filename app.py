"""
app.py — Flask web interface for the RAG Agent.

Provides two endpoints:
    POST /upload   — Upload a document and ingest it into Elasticsearch
    POST /chat     — Send a message and receive an AI answer

Usage:
    python app.py
    Then open http://localhost:5000 in your browser.
"""

import os
import requests
from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from docx import Document

from config import ES_HOST, ES_INDEX, EMBEDDING_MODEL, VECTOR_DIMS, DATA_DIR
from api_keys import get_api_key

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = DATA_DIR

# ── Clients (initialised once) ────────────────────────────────────────────────
es      = Elasticsearch(ES_HOST)
model   = SentenceTransformer(EMBEDDING_MODEL)
API_KEY = get_api_key()

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_DEFAULT_MODEL  = "google/gemini-2.0-flash-001"


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text(file_path: str) -> str:
    """Extract plain text from .txt, .pdf, or .docx files."""
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

    return ""


def _language_instruction(lang_code: str) -> str:
    instructions = {
        "he": "Always answer in Hebrew (עברית).",
        "en": "Always answer in English.",
    }
    return instructions.get(lang_code, "Answer in the same language as the question.")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    """Receive a file, extract its text, embed it, and store in Elasticsearch."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename."}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    content = extract_text(file_path)
    chunks  = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 10]

    for chunk in chunks:
        vector = model.encode(chunk).tolist()
        es.index(index=ES_INDEX, document={
            "text":      chunk,
            "embedding": vector,
            "filename":  file.filename,
        })

    return jsonify({"status": "success", "filename": file.filename, "chunks": len(chunks)})


@app.route("/chat", methods=["POST"])
def chat():
    """Perform RAG: retrieve context, build prompt, call LLM, return answer."""
    body       = request.get_json(force=True)
    user_msg   = body.get("message", "").strip()
    target_lang = body.get("language", "auto")

    if not user_msg:
        return jsonify({"error": "Empty message."}), 400

    # 1 — Retrieve
    query_vector = model.encode(user_msg).tolist()
    search_res   = es.search(
        index=ES_INDEX,
        knn={
            "field":          "embedding",
            "query_vector":   query_vector,
            "k":              3,
            "num_candidates": 100,
        },
    )
    context = "\n\n".join(h["_source"]["text"] for h in search_res["hits"]["hits"])

    # 2 — Augment
    lang_note = _language_instruction(target_lang)
    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {user_msg}\n\n"
        f"{lang_note}"
    )

    # 3 — Generate
    response = requests.post(
        _OPENROUTER_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": _DEFAULT_MODEL, "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]

    return jsonify({"reply": answer})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
