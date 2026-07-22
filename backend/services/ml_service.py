import json
import ast
from sqlmodel import Session, select
from backend.db.models import Illness, Symptom, Question, Precaution

class DiagnosticEngine:
    def __init__(self, engine):
        self.engine = engine

    def evaluate_symptoms(self, active_symptom_ids: list[int]):
        """
        Scores illnesses dynamically based on relational symptom matches.
        Determines the top candidate illnesses and picks optimal follow-up questions
        using information gain (matching questions associated with those illnesses).
        """
        if not active_symptom_ids:
            return {"top_conditions": [], "next_questions": [], "complete": False}

        with Session(self.engine) as session:
            # Load all illnesses with their corresponding symptoms and questions
            illnesses = session.exec(select(Illness)).all()
            scored_illnesses = []

            for illness in illnesses:
                illness_symptom_ids = {s.id for s in illness.symptoms}
                matched_symptoms = [sid for sid in active_symptom_ids if sid in illness_symptom_ids]
                
                # Match score is the proportion of illness symptoms checked
                score = len(matched_symptoms) / max(1, len(illness_symptom_ids))
                scored_illnesses.append({
                    "illness_id": illness.id,
                    "illness_name": illness.name,
                    "score": round(score, 4),
                    "total_symptoms": len(illness_symptom_ids),
                    "matched_count": len(matched_symptoms)
                })

            # Sort illnesses by score descending
            scored_illnesses = sorted(scored_illnesses, key=lambda x: x["score"], reverse=True)
            
            # Grab top candidates
            top_candidates = [item for item in scored_illnesses if item["score"] > 0]
            if not top_candidates:
                return {"top_conditions": [], "next_questions": [], "complete": False}

            # Decide if prediction is stable (highest candidate has distinct high score or we hit high threshold)
            primary_candidate = top_candidates[0]
            is_complete = primary_candidate["score"] >= 0.75 or len(active_symptom_ids) >= 12

            # Gather follow-up questions for candidate conditions
            next_questions = []
            target_illness_ids = [c["illness_id"] for c in top_candidates[:2]] # Look at top 2 candidate illnesses
            
            for illness_id in target_illness_ids:
                questions = session.exec(
                    select(Question).where(Question.illness_id == illness_id)
                ).all()
                for q in questions:
                    next_questions.append({
                        "question_id": q.id,
                        "text": q.text,
                        "illness_name": q.illness.name if q.illness else "Unknown"
                    })

            # Return top conditions, list of diagnostic questions, and state
            return {
                "top_conditions": top_candidates[:3],
                "next_questions": next_questions[:6], # Keep it light so we do not overwhelm users
                "complete": is_complete
            }

    def get_precautions(self, illness_name: str):
        """Retrieves precautions for the final diagnosed illness."""
        with Session(self.engine) as session:
            illness = session.exec(select(Illness).where(Illness.name == illness_name)).first()
            if not illness:
                return []
            precautions = session.exec(
                select(Precaution).where(Precaution.illness_id == illness.id)
            ).all()
            return [p.text for p in precautions]


'''
once the nlp finds the symptoms, this file asks the sql database the question and it calculates the probability scores and figures out which follow-up questions to ask the user. It also returns the final precautions for the diagnosed illness.
'''