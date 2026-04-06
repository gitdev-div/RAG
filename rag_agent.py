"""
rag_agent.py — Terminal-based RAG chat agent.

Retrieves relevant context from Elasticsearch, builds an enriched prompt,
and sends it to an LLM via OpenRouter. Runs as an interactive CLI loop.

Usage:
    python rag_agent.py
"""

import sys
from retriever  import search
from openrouter import send_message


# ── Prompt template ──────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a helpful assistant. Answer the user's question using ONLY the context
provided below. If the answer is not in the context, say so honestly.

Context:
{context}

User question: {question}
"""


# ── Core RAG logic ───────────────────────────────────────────────────────────

def ask(question: str) -> str:
    """
    Full RAG pipeline for a single question:
        1. Retrieve relevant chunks from Elasticsearch
        2. Build an augmented prompt
        3. Get a response from the LLM
    Returns the answer string.
    """
    # 1 — Retrieve
    hits = search(question, top_k=3)

    if hits:
        context = "\n\n".join(h["_source"]["text"] for h in hits)
    else:
        context = "No relevant information found in the knowledge base."

    # 2 — Augment
    prompt = _SYSTEM_PROMPT.format(context=context, question=question)

    # 3 — Generate
    answer, model_used = send_message(prompt)
    return answer, model_used


# ── CLI loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n" + "═" * 50)
    print("   🤖  RAG Agent — ready to answer questions")
    print("   Type 'exit' or 'quit' to stop.")
    print("═" * 50 + "\n")

    while True:
        try:
            user_input = input("You › ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋  Goodbye!")
            sys.exit(0)

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("👋  Goodbye!")
            break

        try:
            answer, model = ask(user_input)
            print(f"\nAI [{model}]\n{'─' * 40}\n{answer}\n{'─' * 40}\n")
        except Exception as exc:
            print(f"⚠️   Error: {exc}\n")


if __name__ == "__main__":
    main()
