import requests, keyring, io
import pandas as pd
from flask import Flask, request, render_template, jsonify
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
import config

# --- 1. INITIALIZE APP FIRST (Fixes NameError) ---
app = Flask(__name__)

# --- 2. INITIALIZE TOOLS ---
es = Elasticsearch(config.ES_HOST)
model = SentenceTransformer(config.EMBEDDING_MODEL)
API_KEY = keyring.get_password("openrouter", "api_key")

def extract_text(file):
    name = file.filename.lower()
    stream = io.BytesIO(file.read())
    
    if name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(stream)
        return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
    elif name.endswith('.docx'):
        doc = Document(stream)
        return "\n".join([p.text for p in doc.paragraphs])
    elif name.endswith('.csv'):
        df = pd.read_csv(stream)
        return df.to_string()
    else: # Default to TXT
        try: return stream.getvalue().decode('utf-8')
        except: return stream.getvalue().decode('latin-1', errors='ignore')

def get_chunks(text):
    start = 0
    while start < len(text):
        yield text[start : start + config.CHUNK_SIZE]
        start += (config.CHUNK_SIZE - config.CHUNK_OVERLAP)

# --- 3. DEFINE ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    text = extract_text(file)
    
    # Reset Elasticsearch Index
    if es.indices.exists(index=config.ES_INDEX):
        es.indices.delete(index=config.ES_INDEX)
    
    es.indices.create(index=config.ES_INDEX, body={
        "mappings": {"properties": {
            "text": {"type": "text"},
            "vector": {"type": "dense_vector", "dims": config.VECTOR_DIMS, "index": True, "similarity": "cosine"}
        }}
    })

    chunks = list(get_chunks(text))
    for chunk in chunks:
        if not chunk.strip(): continue
        vec = model.encode(chunk).tolist()
        es.index(index=config.ES_INDEX, document={"text": chunk, "vector": vec})
    
    return jsonify({"status": "success", "filename": file.filename, "chunks": len(chunks)})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get("message")
    lang = data.get("lang", "en")
    
    # Multilingual System Prompt
    prompts = {
        "en": "Answer in English based on the context.",
        "he": "ענה בעברית בלבד על סמך ההקשר המצורף. שמור על כיוון כתיבה מימין לשמאל.",
        "ru": "Отвечай строго на русском языке на основе предоставленного контекста."
    }
    sys_instr = prompts.get(lang, prompts["en"])

    vec = model.encode(msg).tolist()
    res = es.search(index=config.ES_INDEX, knn={
        "field": "vector", "query_vector": vec, 
        "k": config.TOP_K_RESULTS, "num_candidates": 100
    })
    
    context = "\n---\n".join([h["_source"]["text"] for h in res["hits"]["hits"]])
    
    api_res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "google/gemini-2.0-flash-001",
            "messages": [
                {"role": "system", "content": sys_instr},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {msg}"}
            ]
        }
    )
    return jsonify({"response": api_res.json()['choices'][0]['message']['content']})

if __name__ == '__main__':
    app.run(debug=True, port=5000)