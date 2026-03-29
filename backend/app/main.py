from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api import routes_search, routes_ai, routes_analytics, routes_export
from app.core.database import engine, Base
from app.models import lead # Ensure models are loaded

app = FastAPI(title="LeadForge AI API", description="AI-powered lead discovery and extraction")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"DB Initialization Error (Standard for SQLite if exists): {e}")

# Include Routes
app.include_router(routes_search.router)
app.include_router(routes_ai.router)
app.include_router(routes_analytics.router)
app.include_router(routes_export.router)

@app.get("/")
async def root():
    return {"message": "Welcome to LeadForge AI API", "status": "active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
