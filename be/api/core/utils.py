from functools import lru_cache

from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def load_embedding_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
