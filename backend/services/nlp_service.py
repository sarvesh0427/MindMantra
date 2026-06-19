import numpy as np
from sentence_transformers import SentenceTransformer, util
from sqlmodel import Session, select
from backend.db.models import Symptom

class SymptomMatcher:
    def __init__(self, engine):
        self.engine = engine
        # Load a high-performing, lightweight model optimal for CPU workloads
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.symptom_names = []
        self.symptom_ids = []
        self.symptom_embeddings = None
        self.refresh_cache()

    def refresh_cache(self):
        """Fetch all symptoms from the database and generate vector embeddings."""
        with Session(self.engine) as session:
            symptoms = session.exec(select(Symptom)).all()
            if not symptoms:
                self.symptom_names = []
                self.symptom_ids = []
                self.symptom_embeddings = None
                return

            self.symptom_names = [s.name for s in symptoms]
            self.symptom_ids = [s.id for s in symptoms]
            # Create vectors for all stored symptoms
            self.symptom_embeddings = self.model.encode(
                self.symptom_names, 
                convert_to_tensor=True
            )

    def find_matches(self, user_text: str, threshold: float = 0.40):
        """
        Takes natural language input, computes embeddings, and finds the best matching
        database symptoms using cosine similarity.
        """
        if not self.symptom_names or self.symptom_embeddings is None:
            return []

        user_embedding = self.model.encode(user_text, convert_to_tensor=True)
        # Compute cosine similarities between user query and all database symptoms
        cosine_scores = util.cos_sim(user_embedding, self.symptom_embeddings)[0]

        matches = []
        for i, score in enumerate(cosine_scores):
            score_val = float(score)
            if score_val >= threshold:
                matches.append({
                    "id": self.symptom_ids[i],
                    "name": self.symptom_names[i],
                    "score": round(score_val, 4)
                })

        # Sort matches by high relevance
        return sorted(matches, key=lambda x: x["score"], reverse=True)