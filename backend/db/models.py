# backend/db/models.py
from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

class IllnessSymptomLink(SQLModel, table=True):
    illness_id: Optional[int] = Field(default=None, foreign_key="illness.id", primary_key=True)
    symptom_id: Optional[int] = Field(default=None, foreign_key="symptom.id", primary_key=True)

class Illness(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    
    # Use strings "Symptom", "Question", etc., to avoid circular import errors
    symptoms: List["Symptom"] = Relationship(back_populates="illnesses", link_model=IllnessSymptomLink)
    questions: List["Question"] = Relationship(back_populates="illness")
    precautions: List["Precaution"] = Relationship(back_populates="illness")

class Symptom(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    
    illnesses: List["Illness"] = Relationship(back_populates="symptoms", link_model=IllnessSymptomLink)

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    illness_id: Optional[int] = Field(default=None, foreign_key="illness.id")
    
    illness: Optional["Illness"] = Relationship(back_populates="questions")

class Precaution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    illness_id: Optional[int] = Field(default=None, foreign_key="illness.id")
    
    illness: Optional["Illness"] = Relationship(back_populates="precautions")


'''
This file tells sql model create these tables in Postgresql and define how they relate to each other.
SQLModel: every database table inherits from this, sql table.
Field: used to define each columns; instead of sql query like: id SERIAL PRIMARY KEY, it write: id:optional[int] = Field(primary_key=True)
Relationship: define relationship between tables; instead of writing SQL JOINS maually, it define: symptoms=Relationship(...)

'''