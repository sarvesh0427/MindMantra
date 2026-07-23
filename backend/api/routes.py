from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.db.database import get_session, engine
from backend.services.nlp_service import SymptomMatcher
from backend.services.ml_service import DiagnosticEngine
from backend.db.models import Symptom, Illness
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()
nlp_service = SymptomMatcher(engine)
ml_engine = DiagnosticEngine(engine)

class SymptomMatchRequest(BaseModel):
    user_text: str
    threshold: Optional[float] = 0.40

class DiagnosticRequest(BaseModel):
    symptom_ids: List[int]
    answered_questions: Optional[List[dict]] = [] # Track question answers

@router.get("/symptoms", response_model=List[dict])
def get_all_symptoms(session: Session = Depends(get_session)):
    """Fetch list of all 180+ symptoms currently available in database."""
    symptoms = session.exec(select(Symptom)).all()
    return [{"id": s.id, "name": s.name} for s in symptoms]

@router.post("/match-symptoms")
def match_symptoms(payload: SymptomMatchRequest):
    """Processes unstructured natural language text to discover exact database symptoms."""
    try:
        matches = nlp_service.find_matches(payload.user_text, payload.threshold)
        return {"matches": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/diagnose")
def diagnose_pipeline(payload: DiagnosticRequest):
    """
    Evaluates current list of symptom IDs.
    Returns matched conditions, dynamic follow-up questions, and active prediction state.
    """
    try:
        results = ml_engine.evaluate_symptoms(payload.symptom_ids)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/precautions")
def get_precautions_for_condition(condition: str = Query(..., description="Name of the predicted illness")):
    """Retrieves full list of evidence-based precautions for a diagnosed condition."""
    try:
        precautions = ml_engine.get_precautions(condition)
        if not precautions:
            return {"precautions": ["Consult a medical professional or counselor for guidance."]}
        return {"precautions": precautions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/refresh-nlp-cache")
def refresh_nlp_cache():
    """Forces NLP model to refresh cache if symptoms change in the database."""
    try:
        nlp_service.refresh_cache()
        return {"status": "success", "message": "Symptom vector space updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



'''
this file creates URL endpoints like api/match-symptoms or api/diagnose; it tells the waiter: if a customer asks for /diagnose, take their data, go the kitchen, run ml_service.py, and bring the answer back to the customer. It also handles errors and exceptions, returning a 500 error if something goes wrong. The endpoints are designed to be used by the frontend of the application, which will call these endpoints with user data and receive structured responses.
'''