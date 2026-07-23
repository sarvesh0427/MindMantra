from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router as api_router
from backend.db.database import engine
from sqlmodel import SQLModel

# Initialize FastAPI app
app = FastAPI(
    title="MindMantra Cognitive Inference Engine",
    description="High-performance backend API for semantic mental health symptom analysis and diagnosis helper",
    version="2.0.0"
)

# CORS config to allow frontend UI queries safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root status check
@app.get("/")
def read_root():
    return {
        "app": "MindMantra V2",
        "status": "online",
        "api_docs": "/docs"
    }

# Register all API endpoints
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # Make sure tables are generated if they do not exist
    SQLModel.metadata.create_all(engine)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)


'''
this is the entry point of server. When we type python -m backend.main, this file turns the server on, loads the routes.py and keeps the application running 24/7 listening for incoming requests. It also sets up CORS to allow the frontend to communicate with the backend safely, and provides a root endpoint for health checks and basic information about the API.
'''