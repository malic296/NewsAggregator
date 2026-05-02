import json

from sentence_transformers.util import cos_sim
from simplemma import lemmatize

class SemanticService:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def normalize_text(self, text: str) -> str:
        lemmas = [lemmatize(w, lang="cs") for w in text.split()]
        return " ".join(lemmas)

    def create_embedding(self, text: str):
        return self.embedding_model.encode(text).tolist()

    def coerce_embedding(self, embedding) -> list[float]:
        if embedding is None:
            return []

        if isinstance(embedding, str):
            raw = embedding.strip()
            if not raw:
                return []
            if raw.startswith("{") and raw.endswith("}"):
                raw = "[" + raw[1:-1] + "]"
            try:
                embedding = json.loads(raw)
            except json.JSONDecodeError:
                embedding = [value for value in raw.strip("[]").split(",") if value]

        return [float(value) for value in embedding]

    def get_similarity_percentage(self, first_embedding, second_embedding) -> float:
        first_embedding = self.coerce_embedding(first_embedding)
        second_embedding = self.coerce_embedding(second_embedding)
        if not first_embedding or not second_embedding:
            return 0.0

        cosine_score = cos_sim(first_embedding, second_embedding).item()
        percentage = max(0.0, cosine_score) * 100
        return round(percentage, 2)
