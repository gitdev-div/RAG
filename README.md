# 🤖 RAG Agent — Retrieval-Augmented Generation System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.13.0-orange)
![Docker](https://img.shields.io/badge/Docker-Required-blue)

A professional, local RAG (Retrieval-Augmented Generation) pipeline that allows you to chat with your own documents (PDF, DOCX, TXT) using Elasticsearch for vector search and OpenRouter as the LLM gateway.

---

## 🏗️ Architecture & Structure

```plaintext
RAG_AGENT/
│
├── assets/               # Architecture diagrams & UI screenshots
├── data/                 # Local document storage (Git-ignored)
├── templates/            # Flask Web UI (HTML/Tailwind CSS)
│
├── .flaskenv             # Flask environment configuration
├── .gitignore            # Professional English-only filter
├── app.py                # Main Web Server & API logic
├── config.py             # Centralized configuration (ES, Models)
├── ingest_data.py        # Script to process and index local documents
├── rag_agent.py          # CLI-based chat loop for terminal testing
├── README.md             # Project documentation
└── requirements.txt      # Project dependencies
🛠️ Tech Stack & Prerequisites
Core Technologies
Language: Python 3.9+
Database: Elasticsearch 8.13.0 (Vector Store)
Web Framework: Flask
AI Models
Embeddings: Sentence-Transformers (all-MiniLM-L6-v2)
LLM Gateway: OpenRouter API (Gemini 2.0 Flash)
Frontend
Tailwind CSS (Modern Responsive UI)
Infrastructure
Docker Desktop
🚀 Quick Start
1. Setup Environment
git clone https://github.com/your-username/rag-agent.git
cd rag-agent
pip install -r requirements.txt
2. Start Elasticsearch (Docker)
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.0
3. Store API Key Securely
python -c "import keyring; keyring.set_password('openrouter', 'api_key', 'sk-or-v1-YOUR_KEY_HERE')"
4. Launch the Application
flask run

Open in browser:
http://localhost:5000

⚙️ How It Works
User Question
      │
      ▼
[Embedder] → query vector (all-MiniLM-L6-v2)
      │
      ▼
[Elasticsearch kNN Search] → top-k relevant chunks
      │
      ▼
[Prompt Builder] → "Context: {chunks}\n\nQuestion: {user_query}"
      │
      ▼
[OpenRouter LLM] → answer (Claude / Gemini / GPT fallback chain)
      │
      ▼
Response to user
🌍 Multilingual Support

Toggle between Hebrew, English, or Auto-detect
Ask in one language, receive answers in another
Works seamlessly across mixed-language documents
🛡️ Security
No Plaintext Keys: Uses keyring for OS-level secure storage
Privacy: data/ and .env are excluded via .gitignore
Local Processing: Embeddings and parsing run locally
🚀 Deployment
🐳 Docker Compose (Recommended)

Create docker-compose.yml:

version: "3.9"

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  app:
    build: .
    container_name: rag-agent
    ports:
      - "5000:5000"
    depends_on:
      - elasticsearch
    environment:
      - FLASK_APP=app.py

Create Dockerfile:

FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]

Run:

docker-compose up --build
☁️ Render
Build: pip install -r requirements.txt
Start: flask run --host=0.0.0.0 --port=10000

⚠️ Use external Elasticsearch (Elastic Cloud)

☁️ AWS EC2
sudo apt update
sudo apt install docker.io docker-compose -y

git clone https://github.com/your-username/rag-agent.git
cd rag-agent
docker-compose up --build -d

Access:
http://YOUR_EC2_IP:5000

📜 Requirements
elasticsearch==8.13.0
sentence-transformers==2.7.0
PyPDF2==3.0.1
python-docx==1.1.2
python-dotenv==1.0.1
flask==3.0.2
requests==2.31.0
keyring==24.3.0
