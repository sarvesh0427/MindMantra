import os
import torch
from sentence_transformers import SentenceTransformer, util
from sqlmodel import Session, select
from backend.db.models import Symptom

class SymptomMatcher:
    def __init__(self, engine):
        """
        Initializes the NLP engine with a lightweight transformer model.
        We use 'all-MiniLM-L6-v2' for a balance between speed and semantic accuracy.
        """
        self.engine = engine
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.symptom_names = []
        self.symptom_ids = []
        self.symptom_embeddings = None
        self.refresh_cache()

    def refresh_cache(self):
        """
        Fetches the latest symptoms from the database and updates
        the embedding vector space. This ensures new symptoms added 
        via admin scripts are immediately searchable.
        """
        with Session(self.engine) as session:
            symptoms = session.exec(select(Symptom)).all()
            if not symptoms:
                return

            self.symptom_names = [s.name for s in symptoms]
            self.symptom_ids = [s.id for s in symptoms]
            
            # Encode symptoms into vector space
            self.symptom_embeddings = self.model.encode(
                self.symptom_names, 
                convert_to_tensor=True
            )

    def find_matches(self, user_text: str, threshold: float = 0.35):
        """
        Takes natural language input, computes embeddings, and finds the best matching
        database symptoms using cosine similarity.
        
        :param user_text: The user's descriptive input.
        :param threshold: The sensitivity level (0.0 to 1.0). Lowering this 
                         makes the search 'looser' (more results).
        """
        if not self.symptom_names or self.symptom_embeddings is None:
            return []

        # 1. Encode user input
        user_embedding = self.model.encode(user_text, convert_to_tensor=True)

        # 2. Compute Cosine Similarity
        cosine_scores = util.cos_sim(user_embedding, self.symptom_embeddings)[0]

        # 3. Filter and Format Results
        matches = []
        for idx, score in enumerate(cosine_scores):
            if score >= threshold:
                matches.append({
                    "id": self.symptom_ids[idx],
                    "name": self.symptom_names[idx],
                    "score": float(score)
                })

        # Sort by best match first
        return sorted(matches, key=lambda x: x['score'], reverse=True)