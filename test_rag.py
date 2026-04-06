import requests
import keyring
from elasticsearch import Elasticsearch
import config

print("--- RAG SYSTEM DIAGNOSTIC ---")

# 1. Test Elasticsearch
try:
    es = Elasticsearch(config.ES_HOST)
    if es.indices.exists(index=config.ES_INDEX):
        count = es.count(index=config.ES_INDEX)['count']
        print(f"✅ Elasticsearch: Index '{config.ES_INDEX}' exists with {count} chunks.")
    else:
        print(f"❌ Elasticsearch: Index '{config.ES_INDEX}' DOES NOT EXIST. (Did you upload the file?)")
except Exception as e:
    print(f"❌ Elasticsearch Error: Could not connect to {config.ES_HOST}. Is Docker/Elasticsearch running?")

# 2. Test API Key
api_key = keyring.get_password("openrouter", "api_key")
if api_key:
    print("✅ OpenRouter: API Key found in Windows Keyring.")
    
    # 3. Test API Connection
    print("⏳ Testing OpenRouter connection...")
    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": "Say 'hello'"}]}
    )
    if res.status_code == 200:
        print("✅ OpenRouter: Connection successful!")
    else:
        print(f"❌ OpenRouter Error ({res.status_code}): {res.text}")
else:
    print("❌ OpenRouter: API Key MISSING from Windows Keyring.")