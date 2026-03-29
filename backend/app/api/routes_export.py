from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import Response, FileResponse
from app.core.database import get_db
from app.models.lead import Lead
import csv
import io
import json

router = APIRouter(prefix="/api/export", tags=["Data Export"])

@router.get("/csv")
async def export_leads_csv(search_id: int = None, owner_id: str = None, db: Session = Depends(get_db)):
    """Exports leads as CSV file."""
    query = db.query(Lead)
    if search_id:
        query = query.filter(Lead.search_id == search_id)
    if owner_id:
        query = query.filter(Lead.owner_id == owner_id)
        
    leads = query.all()
    if not leads:
        raise HTTPException(status_code=404, detail="No leads to export")
        
    # Lead data columns
    columns = [
        "company_name", "website", "email", "phone", "city", 
        "industry_classification", "ai_summary", "final_lead_score", "priority_level",
        "source_platform", "source_url", "discovery_source", "discovery_url", 
        "authenticity_status", "authenticity_reason"
    ]
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    
    for lead in leads:
        writer.writerow({
            "company_name": lead.company_name,
            "website": lead.website,
            "email": lead.email,
            "phone": lead.phone,
            "city": lead.city,
            "industry_classification": lead.industry_classification,
            "ai_summary": lead.ai_summary,
            "final_lead_score": lead.final_lead_score,
            "priority_level": lead.priority_level,
            "source_platform": lead.source_platform,
            "source_url": lead.source_url,
            "discovery_source": lead.discovery_source,
            "discovery_url": lead.discovery_url,
            "authenticity_status": lead.authenticity_status,
            "authenticity_reason": lead.authenticity_reason
        })
        
    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=leadforge_export_{search_id or 'all'}.csv"
    return response

@router.get("/json")
async def export_leads_json(search_id: int = None, owner_id: str = None, db: Session = Depends(get_db)):
    """Exports leads as JSON file."""
    query = db.query(Lead)
    if search_id:
        query = query.filter(Lead.search_id == search_id)
    if owner_id:
        query = query.filter(Lead.owner_id == owner_id)
        
    leads = query.all()
    # Simple JSON dump of objects
    data = [
        {
            "id": l.id,
            "company_name": l.company_name,
            "website": l.website,
            "email": l.email,
            "phone": l.phone,
            "industry": l.industry_classification,
            "score": l.final_lead_score or l.score or 0,
            "priority": l.priority_level,
            "source_platform": l.source_platform,
            "source_url": l.source_url,
            "discovery_source": l.discovery_source,
            "discovery_url": l.discovery_url,
            "authenticity_status": l.authenticity_status,
            "authenticity_reason": l.authenticity_reason,
            "scraped_pages": l.scraped_pages,
            "scraped_at": str(l.scraped_at) if l.scraped_at else None,
            "created_at": str(l.created_at) if l.created_at else None
        } for l in leads
    ]
    
    return data
