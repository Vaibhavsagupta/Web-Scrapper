from app.core.database import engine, Base
from app.models.lead import Lead, SearchRequest

try:
    print("Initializing Database...")
    Base.metadata.create_all(bind=engine)
    print("Database Initialized Successfully!")
except Exception as e:
    print(f"Error: {e}")
