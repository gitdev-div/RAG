# config.py
ES_HOST = "http://localhost:9200"
ES_INDEX = "universal_knowledge_base"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_DIMS = 384

# High-Precision Settings
CHUNK_SIZE = 1500    
CHUNK_OVERLAP = 500  
TOP_K_RESULTS = 10