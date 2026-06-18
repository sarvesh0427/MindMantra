# data/seed_db.py
import pandas as pd
import ast
import os
import sys
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, select
from backend.db.models import Illness, Symptom, Question, Precaution

# Load environment variables
# load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def seed_database():
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        print("Loading CSV files...")
        # Read datasets
        illness_df = pd.read_csv("data/raw_csvs/illness_dataset.csv")
        precaution_df = pd.read_csv("data/raw_csvs/precaution_dataset.csv")
        followup_df = pd.read_csv("data/raw_csvs/followup_dataset.csv")
        
        # 1. Process Illnesses and Symptoms from illness_dataset.csv
        print("Seeding Illnesses and Symptoms...")
        symptom_columns = [col for col in illness_df.columns if col != 'Disease']
        
        # Create all symptoms first
        symptom_objects = {}
        for sym_name in symptom_columns:
            sym = Symptom(name=sym_name.strip())
            session.add(sym)
            symptom_objects[sym_name] = sym
        session.commit() # Save symptoms to get their IDs
        
        # Create illnesses and link them
        illness_objects = {}
        for _, row in illness_df.iterrows():
            disease_name = row['Disease'].strip()
            illness = Illness(name=disease_name)
            
            # Find which symptoms are 1 for this disease
            for sym_name in symptom_columns:
                if row[sym_name] == 1:
                    illness.symptoms.append(symptom_objects[sym_name])
            
            session.add(illness)
            illness_objects[disease_name] = illness
        session.commit()
        
        # 2. Process Precautions
        print("Seeding Precautions...")
        for _, row in precaution_df.iterrows():
            disease_name = str(row['Disease']).strip()
            precaution_text = str(row['Precaution']).strip()
            
            # Get the illness from our dictionary
            illness = illness_objects.get(disease_name)
            if illness and precaution_text != 'nan':
                prec = Precaution(text=precaution_text, illness_id=illness.id)
                session.add(prec)
        session.commit()

        # 3. Process Follow-up Questions
        print("Seeding Follow-up Questions...")
        for _, row in followup_df.iterrows():
            disease_name = str(row['predicted_condition']).strip()
            questions_str = str(row['followup_questions'])
            
            illness = illness_objects.get(disease_name)
            if illness and questions_str != 'nan':
                try:
                    # Convert string representation of list to actual Python list
                    questions_list = ast.literal_eval(questions_str)
                    for q_text in questions_list:
                        # Avoid duplicate questions for the same illness
                        existing_q = session.exec(select(Question).where(Question.text == q_text, Question.illness_id == illness.id)).first()
                        if not existing_q:
                            q = Question(text=q_text, illness_id=illness.id)
                            session.add(q)
                except Exception as e:
                    print(f"Error parsing questions for {disease_name}: {e}")
        session.commit()

    print("Database seeding complete! Phase 1 is done.")

if __name__ == "__main__":
    # Make sure backend package is discoverable
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    seed_database()