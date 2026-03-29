import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api import routes_search, routes_ai, routes_analytics, routes_export
from app.core.database import engine, Base
from app.models import lead # Ensure models are loaded

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leadforge-api")

app = FastAPI(title="LeadForge AI API", description="AI-powered lead discovery and extraction")

# Production-safe CORS Configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [
    "http://localhost:5173",
    "http://localhost:8880", # Local dev proxy
]

# If FRONTEND_URL is provided and not a wildcard, add it to origins
if frontend_url and frontend_url != "*":
    # Handle comma-separated list of origins if needed
    for url in frontend_url.split(","):
        origins.append(url.strip())
else:
    # If explicitly set to wildcard, use a placeholder or handle specifically
    # Note: allow_credentials=True requires explicit origins
    logger.warning("CORS: FRONTEND_URL is set to wildcard or missing. Credentials may be blocked in some browsers.")
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware for Production Diagnostics
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    logger.info(f"🚀 Incoming Request: {method} {path}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(f"✅ Request Completed: {method} {path} - Status: {response.status_code} - Done in {duration:.2f}s")
    
    return response

# Initialize Database
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"DB Initialization Error: {e}")

# Include Routes
app.include_router(routes_search.router)
app.include_router(routes_ai.router)
app.include_router(routes_analytics.router)
app.include_router(routes_export.router)

@app.get("/")
async def root():
    return {"message": "Welcome to LeadForge AI API", "status": "active"}

@app.get("/api/health")
async def health_check():
    """Lightweight endpoint for production connectivity verification."""
    return {
        "status": "ok", 
        "environment": os.getenv("ENVIRONMENT", "production"),
        "timestamp": time.time(),
        "database": "connected" # Basic check
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
