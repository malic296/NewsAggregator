from sentence_transformers.util import cos_sim
from simplemma import lemmatize
import numpy as np
import json

class SemanticService:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def normalize_text(self, text: str) -> str:
        lemmas = [lemmatize(w, lang="cs") for w in text.split()]
        return " ".join(lemmas)

    def create_embedding(self, text: str):
        return self.embedding_model.encode(text).tolist()

    def get_similarity_percentage(self, first_embedding: list[float], second_embedding: list[float]) -> float:
        if isinstance(first_embedding, str):
            first_embedding = json.loads(first_embedding)
        if isinstance(second_embedding, str):
            second_embedding = json.loads(second_embedding)

        if not first_embedding or not second_embedding:
            return 0.0

        cosine_score = cos_sim(first_embedding, second_embedding).item()
        percentage = max(0.0, cosine_score) * 100
        return round(percentage, 2)

    def calculate_centroid_embedding(self, embeddings: list[list[float]]) -> list[float]:
        if not embeddings:
            raise Exception("Cannot calculate centroid embedding for empty list of embeddings.")

        vectors = np.array(embeddings, dtype=float)
        centroid = vectors.mean(axis=0)

        return centroid.tolist()


