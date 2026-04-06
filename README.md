<div align="center">

# 🤖 RAG Agent

### Retrieval-Augmented Generation · Chat with Your Documents

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.13.0-005571?style=flat-square&logo=elasticsearch&logoColor=white)](https://www.elastic.co/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)


A local, privacy-first RAG pipeline that lets you **chat with your own documents** (PDF, DOCX, TXT) using Elasticsearch for vector search and OpenRouter as the LLM gateway.

[Getting Started](#-quick-start) · [Architecture](#️-architecture) · [Features](#-features) · [Deployment](#-deployment)

</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| 📄 **Document Support** | PDF, DOCX, TXT ingestion with automatic chunking |
| 🔍 **Semantic Search** | Elasticsearch kNN vector search (`all-MiniLM-L6-v2`) |
| 🧠 **LLM Gateway** | OpenRouter API — Gemini 2.0 Flash with Claude / GPT fallback chain |
| 🌍 **Multilingual** | Hebrew, English, or Auto-detect; ask in one language, get answers in another |
| 🔐 **Secure Key Storage** | OS-level keyring — no plaintext API keys |
| 🏠 **Privacy-First** | Embeddings and parsing run fully locally |
| 🖥️ **Web UI** | Responsive Flask interface styled with Tailwind CSS |
| 🐳 **Docker Ready** | One-command deployment with Docker Compose |

---

## 🏗️ Architecture

```
User Question
      │
      ▼
┌─────────────┐
│   Embedder  │  all-MiniLM-L6-v2  →  query vector
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  Elasticsearch kNN   │  →  top-k relevant document chunks
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Prompt Builder     │  "Context: {chunks}\n\nQuestion: {query}"
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  OpenRouter LLM      │  Gemini 2.0 Flash  →  answer
└──────────┬───────────┘
           │
           ▼
     Response to User
```

### Project Structure

```
RAG_AGENT/
├── assets/           # Architecture diagrams & UI screenshots
├── data/             # Local document storage (git-ignored)
├── templates/        # Flask Web UI (HTML + Tailwind CSS)
├── app.py            # Main web server & API logic
├── config.py         # Centralized configuration (ES, models)
├── ingest_data.py    # Document processing & indexing pipeline
├── rag_agent.py      # CLI chat loop for terminal testing
├── requirements.txt  # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker Desktop
- [OpenRouter API key](https://openrouter.ai/)

### 1 · Clone & Install

```bash
git clone https://github.com/your-username/rag-agent.git
cd rag-agent
pip install -r requirements.txt
```

### 2 · Start Elasticsearch

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.0
```

### 3 · Store Your API Key

```bash
python -c "import keyring; keyring.set_password('openrouter', 'api_key', 'sk-or-v1-YOUR_KEY_HERE')"
```

> **Why keyring?** Your key is stored in the OS credential vault (Keychain on macOS, Windows Credential Manager, libsecret on Linux) — never in plaintext files.

### 4 · Ingest Documents

Place your files in the `data/` folder, then run:

```bash
python ingest_data.py
```

### 5 · Launch the App

```bash
flask run
```

Open **http://localhost:5000** in your browser.

---

## ⚙️ Configuration

All settings live in `config.py`. Key options:

| Variable | Default | Description |
|---|---|---|
| `ES_HOST` | `localhost:9200` | Elasticsearch endpoint |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-Transformers model |
| `LLM_MODEL` | `google/gemini-2.0-flash-001` | Default LLM via OpenRouter |
| `TOP_K` | `5` | Number of chunks to retrieve |

---

## 🌍 Multilingual Support

The UI includes a language toggle for **Hebrew**, **English**, or **Auto-detect**.

- Ask a question in Hebrew → receive an answer in Hebrew
- Works seamlessly across mixed-language document collections
- Prompt templates adapt automatically to the selected language

---

## 🚢 Deployment

### Docker Compose (Recommended)

**`docker-compose.yml`**

```yaml
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
```

**`Dockerfile`**

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
```

```bash
docker-compose up --build
```

---

### ☁️ Render

| Setting | Value |
|---|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `flask run --host=0.0.0.0 --port=10000` |

> ⚠️ Render does not support local Docker. Use [Elastic Cloud](https://www.elastic.co/cloud/) as your Elasticsearch backend.

---

### ☁️ AWS EC2

```bash
sudo apt update && sudo apt install docker.io docker-compose -y

git clone https://github.com/your-username/rag-agent.git
cd rag-agent
docker-compose up --build -d
```

Access at `http://YOUR_EC2_IP:5000`. Remember to open port `5000` in your security group.

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| Web Framework | Flask 3.0.2 |
| Vector Store | Elasticsearch 8.13.0 |
| Embeddings | `sentence-transformers` · `all-MiniLM-L6-v2` |
| LLM Gateway | OpenRouter (Gemini 2.0 Flash, Claude, GPT fallback) |
| Frontend | Tailwind CSS |
| Infrastructure | Docker / Docker Compose |

---

## 📋 Requirements

```
elasticsearch==8.13.0
sentence-transformers==2.7.0
PyPDF2==3.0.1
python-docx==1.1.2
python-dotenv==1.0.1
flask==3.0.2
requests==2.31.0
keyring==24.3.0
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## 🛡️ Security

- **No plaintext keys** — API credentials are stored via the OS keyring
- **Local processing** — Embeddings and document parsing never leave your machine
- **Gitignored data** — `data/` and `.env` are excluded from version control by default

---

## 🤝 Contributing

Contributions are welcome! Please open an issue to discuss what you'd like to change, then submit a pull request.

1. Fork the repository
2. Create your branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---



<div align="center">
Made with ❤️ · <a href="https://github.com/gitdev-div/RAG/issues">Report a Bug</a> · <a href="https://github.com/gitdev-div/RAG/issues">Request a Feature</a>
</div>
