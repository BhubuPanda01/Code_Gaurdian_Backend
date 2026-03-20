"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from app.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.database import engine, Base
from app.routes.user_routes import router as user_router
from app.routes.analyze_routes import router as analyze_router
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router)
app.include_router(analyze_router)


# Start worker thread on application startup (development use only)
@app.on_event("startup")
def start_analysis_worker():
    import threading
    from app.worker import run_worker

    worker_thread = threading.Thread(target=run_worker, daemon=True, name="analysis_worker")
    worker_thread.start()


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


@app.get("/")
def root():
    """
    Root endpoint
    """
    return {"message": "Welcome to Code Guardian API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
