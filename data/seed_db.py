import pandas as pd
import ast
import os
from dotenv import load_dotenv
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine, select

# Ensure parent directory is in sys.path so backend is discoverable
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.models import Illness, Symptom, Question, Precaution

# Load environment variables
dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    print(f"Error: DATABASE_URL not found! Searched at: {dotenv_path.absolute()}")
    exit(1)

engine = create_engine(DATABASE_URL)

# Standardization map to bridge spelling differences across datasets
STANDARDIZATION_MAP = {
    'Sepration Anxiety Disorder': 'Separation Anxiety Disorder',
    'Dissocative Amnesia': 'Dissociative Amnesia',
    'Substance use disorder': 'Substance Use Disorder',
    'Attention Defict Hyperactivity Disorder (ADHD)': 'ADHD (Attention Deficit Hyperactivity Disorder)',
    'Dissocative Identity Disorder (DID)': 'Dissociative Identity Disorder',
    'insomnia': 'Insomnia',
    'Anxiety ': 'Anxiety',
    'Persistant Depressive Disorder': 'Persistent Depressive Disorder'
}

def clean_disease_name(name):
    """Standardizes spelling differences across dataset CSV files."""
    if pd.isna(name):
        return None
    name_str = str(name).strip()
    return STANDARDIZATION_MAP.get(name_str, name_str)

def seed_database():
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        print("Reading CSV files...")
        illness_df = pd.read_csv("data/raw_csvs/illness_dataset.csv")
        precaution_df = pd.read_csv("data/raw_csvs/precaution_dataset.csv")
        followup_df = pd.read_csv("data/raw_csvs/followup_dataset.csv")
        
        # 1. Seed Symptoms
        print("Seeding Symptoms...")
        symptom_columns = [col for col in illness_df.columns if col != 'Disease']
        
        symptom_objects = {}
        for sym_name in symptom_columns:
            clean_sym = sym_name.strip()
            # Double check we do not create duplicate symptom rows in postgres
            symptom = session.exec(select(Symptom).where(Symptom.name == clean_sym)).first()
            if not symptom:
                symptom = Symptom(name=clean_sym)
                session.add(symptom)
            symptom_objects[clean_sym] = symptom
        session.commit()
        
        # 2. Seed Illnesses and link with Symptoms
        print("Seeding Illnesses and mapping Symptoms...")
        illness_objects = {}
        for _, row in illness_df.iterrows():
            disease_raw = row['Disease']
            disease_name = clean_disease_name(disease_raw)
            if not disease_name:
                continue
                
            illness = session.exec(select(Illness).where(Illness.name == disease_name)).first()
            if not illness:
                illness = Illness(name=disease_name)
                session.add(illness)
            
            # Map associated symptoms
            for sym_name in symptom_columns:
                clean_sym = sym_name.strip()
                if row[sym_name] == 1:
                    target_symptom = symptom_objects.get(clean_sym)
                    if target_symptom and target_symptom not in illness.symptoms:
                        illness.symptoms.append(target_symptom)
            
            session.add(illness)
            illness_objects[disease_name] = illness
        session.commit()
        
        # 3. Seed Precautions
        print("Seeding Precautions...")
        for _, row in precaution_df.iterrows():
            disease_raw = row['Disease']
            disease_name = clean_disease_name(disease_raw)
            precaution_text = str(row['Precaution']).strip()
            
            if not disease_name or precaution_text == 'nan' or not precaution_text:
                continue
                
            illness = illness_objects.get(disease_name)
            if illness:
                # Avoid duplicate precautions
                existing_p = session.exec(
                    select(Precaution).where(Precaution.text == precaution_text, Precaution.illness_id == illness.id)
                ).first()
                if not existing_p:
                    prec = Precaution(text=precaution_text, illness_id=illness.id)
                    session.add(prec)
        session.commit()

        # 4. Seed Follow-up Questions
        print("Seeding Follow-up Questions...")
        for _, row in followup_df.iterrows():
            disease_raw = row['predicted_condition']
            disease_name = clean_disease_name(disease_raw)
            questions_str = str(row['followup_questions'])
            
            if not disease_name or questions_str == 'nan' or not questions_str:
                continue
                
            illness = illness_objects.get(disease_name)
            if illness:
                try:
                    questions_list = ast.literal_eval(questions_str)
                    for q_text in questions_list:
                        q_clean = q_text.strip()
                        # Verify we do not insert duplicate questions
                        existing_q = session.exec(
                            select(Question).where(Question.text == q_clean, Question.illness_id == illness.id)
                        ).first()
                        if not existing_q:
                            q = Question(text=q_clean, illness_id=illness.id)
                            session.add(q)
                except Exception as e:
                    print(f"Skipping malformed questions for {disease_name}: {e}")
        session.commit()

    print("\nDatabase seeding complete! Phase 1 is fully done.")

if __name__ == "__main__":
    seed_database()
