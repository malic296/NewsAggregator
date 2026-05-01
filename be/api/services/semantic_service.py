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

    def get_similarity_percentage(self, first_embedding, second_embedding) -> float:
        cosine_score = cos_sim(first_embedding, second_embedding).item()
        percentage = max(0.0, cosine_score) * 100
        return round(percentage, 2)