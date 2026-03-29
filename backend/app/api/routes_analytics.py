from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.lead import Lead, SearchRequest
from typing import Dict, Any

router = APIRouter(prefix="/api/analytics", tags=["Dashboard Analytics"])

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Provides high-level stats for the dashboard home."""
    total_leads = db.query(Lead).count()
    high_priority = db.query(Lead).filter(Lead.priority_level == "High Priority").count()
    total_searches = db.query(SearchRequest).count()
    outreach_generated = db.query(Lead).filter(Lead.outreach_email.isnot(None)).count()
    
    # Industry Distribution
    industries = db.query(Lead.industry_classification, func.count(Lead.id)).group_by(Lead.industry_classification).all()
    industry_data = [{"name": ind or "Unknown", "value": count} for ind, count in industries]
    
    return {
        "total_leads": total_leads,
        "high_priority": high_priority,
        "total_searches": total_searches,
        "outreach_generated": outreach_generated,
        "industry_distribution": industry_data[:5] # Top 5
    }

@router.get("/recent-activity")
async def get_recent_activity(db: Session = Depends(get_db)):
    """Fetches most recent leads and searches."""
    recent_leads = db.query(Lead).order_by(Lead.created_at.desc()).limit(5).all()
    recent_searches = db.query(SearchRequest).order_by(SearchRequest.created_at.desc()).limit(5).all()
    
    return {
        "recent_leads": recent_leads,
        "recent_searches": recent_searches
    }
