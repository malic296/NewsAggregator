from sentence_transformers import SentenceTransformer

def load_embedding_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')