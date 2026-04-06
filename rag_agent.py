import requests
import keyring
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import config

es = Elasticsearch(config.ES_HOST)
model = SentenceTransformer(config.EMBEDDING_MODEL)
API_KEY = keyring.get_password("openrouter", "api_key")

def ask(question):
    if not es.indices.exists(index=config.ES_INDEX):
        return "No data found. Upload a file via the Web UI first."

    # Search
    vec = model.encode(question).tolist()
    res = es.search(index=config.ES_INDEX, knn={
        "field": "vector",
        "query_vector": vec,
        "k": config.TOP_K_RESULTS,
        "num_candidates": 100
    })
    
    context = "\n---\n".join([h["_source"]["text"] for h in res["hits"]["hits"]])

    # LLM Call
    api_res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "google/gemini-2.0-flash-001",
            "messages": [{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}]
        }
    )
    return api_res.json()['choices'][0]['message']['content']

if __name__ == "__main__":
    print("🚀 Versatile RAG CLI - Type 'exit' to quit.")
    while True:
        user_input = input("\nAsk anything › ")
        if user_input.lower() in ['exit', 'quit']: break
        print(f"\nAI › {ask(user_input)}")