import os
from dotenv import load_dotenv
from pathlib import Path
from sqlmodel import create_engine, Session

# Load environment variables from .env file in to python
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables or .env file.")

# Create the engine with connection pooling settings for production
engine = create_engine(
    DATABASE_URL,                     # which database to connect
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)

def get_session():
    """Dependency generator for FastAPI routes to manage database sessions safely."""
    with Session(engine) as session:
        yield session


'''
This is the step 1 of this project, this file contains the engine. This engine is like a bridge or a pipeline connecting python code to postgresql database. It uses the DATABASE_URL to find where the database lives on computer.

create_engine: creates a connection manager to database.
session: a working area for interacting with the database.Use to insert, update, delete and query
__file__: location from main file to database.py, .parent use to come out from that file.
load_dotenv: .env file reads and loads all variables into the program.
engine: central connection manager, first it manage connections and create them when needed.
pool_sizse: instead of opening a new database connection everytime, SQLachemy maintains a pool of reusable connections.
max_overflow: if all connections are busy then sqlachemy will temporarily create extra connections
pool_recycle: if connection is older then 3600 seconds then discard it and create a fresh one.
with statement ensurea that the session is automatically closed when you are done.
yield session: it temporarily hands session to fastapi.
Program starts
      │
      ▼
Load .env file
      │
      ▼
Read DATABASE_URL
      │
      ▼
If missing → raise ValueError
      │
      ▼
Create database engine
      │
      ▼
API request arrives
      │
      ▼
get_session() creates Session
      │
      ▼
Session passed to FastAPI endpoint
      │
      ▼
Endpoint performs database operations
      │
      ▼
Session closes automatically
'''