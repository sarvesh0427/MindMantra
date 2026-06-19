import os
from dotenv import load_dotenv
from pathlib import Path
from sqlmodel import create_engine, Session

# Load environment variables
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables or .env file.")

# Create the engine with connection pooling settings for production
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)

def get_session():
    """Dependency generator for FastAPI routes to manage database sessions safely."""
    with Session(engine) as session:
        yield session