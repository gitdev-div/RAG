<div align="center">

# 🤖 RAG Agent — Dynamic Retrieval-Augmented Generation

### Isolated Sessions · Multi-Format Support · Multilingual (EN/HE/RU)

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.13.0-005571?style=flat-square&logo=elasticsearch&logoColor=white)](https://www.elastic.co/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

A professional RAG pipeline featuring **Zero-Contamination architecture**.  
Upload any document and instantly chat with it using high-precision vector search and sliding-window context preservation.

[Quick Start](#-quick-start) · [Advanced RAG](#-advanced-rag-capabilities) · [Architecture](#-architecture) · [Deployment](#-deployment)

</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| 📄 **Universal Ingestion** | PDF, DOCX, **CSV**, and TXT support with real-time indexing |
| 🔍 **Semantic Search** | Elasticsearch kNN vector search using `all-MiniLM-L6-v2` |
| 🧠 **LLM Gateway** | OpenRouter API — **Gemini 2.0 Flash** |
| 🌍 **Trilingual Support** | English, Hebrew, Russian + RTL UI |
| 🔐 **Secure Key Storage** | OS-level keyring (no plaintext secrets) |
| 🏠 **Privacy-First** | Local embeddings and parsing |
| 🐳 **Docker Ready** | Containerized deployment |

---

## 🏗️ Architecture

```mermaid
graph TD
    User((User)) -->|Question| UI[Frontend Toggle: EN/HE/RU]
    UI -->|Query + Lang| App[Flask Backend]

    subgraph Vector_Engine
        App -->|Embed| Embedder[all-MiniLM-L6-v2]
        Embedder -->|Vector| ES[(Elasticsearch kNN)]
        ES -->|Top-10| Context[Context Builder]
    end

    subgraph LLM_Layer
        Context -->|Prompt| LLM[Gemini 2.0 Flash]
        LLM -->|Response| App
    end

    App -->|Answer| User
🧠 Advanced RAG Capabilities
Capability	Technical Implementation	Benefit
♻️ Zero-Contamination	Index reset on upload & restart	Prevents data leakage
🧩 Sliding Window	1200 chars + 200 overlap	Preserves context
🔎 Deep Retrieval	TOP_K = 10 (~12k tokens)	Better accuracy
🌐 Multilingual Logic	Cross-language prompts	Ask in RU/HE → answer from EN docs
🚀 Quick Start
1 · Clone & Install
git clone https://github.com/your-username/rag-agent.git
cd rag-agent
pip install -r requirements.txt
2 · Start Elasticsearch
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.0
3 · Store API Key
python -c "import keyring; keyring.set_password('openrouter', 'api_key', 'YOUR_KEY_HERE')"
4 · Run App
flask run

Open: http://localhost:5000

⚙️ Configuration (config.py)
Variable	Value	Description
CHUNK_SIZE	1200	Text chunk size
CHUNK_OVERLAP	200	Context overlap
TOP_K_RESULTS	10	Retrieved chunks
EMBEDDING_MODEL	all-MiniLM-L6-v2	Vector model
🧪 Quality Assurance
✅ Isolation Test
Upload file → restart server
Expected: no memory
✅ Multilingual Test
Ask Hebrew/Russian on English doc
Expected: correct answer
✅ Format Test
Upload CSV
Ask for data
Expected: structured retrieval
🚀 Deployment
Docker Compose
version: "3.9"

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  app:
    build: .
    ports:
      - "5000:5000"
docker-compose up --build
🛡️ Security
No plaintext API keys
Local document processing
.gitignore protects sensitive data
<div align="center">

Made with ❤️ ·
<a href="https://github.com/gitdev-div/RAG/issues">Report a Bug</a> ·
<a href="https://github.com/gitdev-div/RAG/issues">Request a Feature</a>

</div> ```