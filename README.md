# RAG Agent

> Dynamic Retrieval-Augmented Generation with zero-contamination architecture, multilingual support, and semantic vector search.

---

## Features

| Feature | Details |
|---|---|
| Universal ingestion | PDF, DOCX, CSV, TXT with real-time indexing |
| Semantic search | Elasticsearch kNN via `all-MiniLM-L6-v2` |
| LLM gateway | OpenRouter API — Gemini 2.0 Flash |
| Trilingual support | English, Hebrew, Russian + RTL UI |
| Secure key storage | OS-level keyring — no plaintext secrets |
| Privacy-first | Local embeddings and parsing |
| Docker ready | Containerized deployment |

---

## Architecture

```
User → Frontend (EN/HE/RU toggle) → Flask Backend
                                         │
                    ┌────────────────────┴────────────────────┐
                    │ Vector Engine                            │
                    │  Query → all-MiniLM-L6-v2 → Elasticsearch kNN → Context Builder │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │ LLM Layer                               │
                    │  Context → Gemini 2.0 Flash → Response  │
                    └────────────────────┬────────────────────┘
                                         │
                                       User
```

### Advanced RAG capabilities

| Capability | Implementation | Benefit |
|---|---|---|
| Zero contamination | Index reset on upload & restart | Prevents data leakage |
| Sliding window | 1200 chars + 200 overlap | Preserves cross-chunk context |
| Deep retrieval | TOP_K = 10 (~12k tokens) | Higher answer accuracy |
| Multilingual logic | Cross-language prompts | Ask in RU/HE, retrieve from EN docs |

---

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/your-username/rag-agent.git
cd rag-agent
pip install -r requirements.txt
```

### 2. Start Elasticsearch

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.0
```

### 3. Store your API key

```bash
python -c "import keyring; keyring.set_password('openrouter', 'api_key', 'YOUR_KEY_HERE')"
```

### 4. Run the app

```bash
flask run
```

Open [http://localhost:5000](http://localhost:5000)

---

## Configuration

Edit `config.py` to tune the pipeline:

| Variable | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | `1200` | Text chunk size in characters |
| `CHUNK_OVERLAP` | `200` | Overlap between adjacent chunks |
| `TOP_K_RESULTS` | `10` | Number of chunks retrieved per query |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |

---

## Deployment

### Docker Compose

```yaml
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
```

```bash
docker-compose up --build
```

---

## Quality assurance

**Isolation test** — upload a file, restart the server. Expected: no memory of previous session.

**Multilingual test** — ask a question in Hebrew or Russian against an English document. Expected: correct answer retrieved and translated.

**Format test** — upload a CSV and ask for specific data. Expected: structured retrieval and accurate response.

---

## Security

- No plaintext API keys — stored in OS-level keyring
- Local document parsing — files never leave your machine
- `.gitignore` protects secrets and uploads

---

## Contributing

[Report a bug](https://github.com/gitdev-div/RAG/issues) · [Request a feature](https://github.com/gitdev-div/RAG/issues)
