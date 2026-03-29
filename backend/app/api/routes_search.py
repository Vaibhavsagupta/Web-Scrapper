from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db, SessionLocal
from app.models.lead import Lead, SearchRequest
from app.schemas.lead_schema import LeadResponse, SearchRequestCreate, SearchRequestResponse
from app.services.lead_discovery_service import LeadDiscoveryService
from app.services.scrape_service import ScrapeService
import traceback
import os
from app.tasks.lead_tasks import run_lead_search_task

@router.post("/", response_model=SearchRequestResponse)
async def start_search(payload: SearchRequestCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Starts a new lead search campaign."""
    print(f"DEBUG SEARCH: Request received for platform {payload.platform}")
    
    new_search = SearchRequest(
        keyword=payload.keyword,
        location=payload.location,
        lead_count=payload.lead_count,
        owner_id=payload.owner_id,
        platform=payload.platform,
        status="running"
    )
    db.add(new_search)
    db.commit()
    db.refresh(new_search)
    print(f"DEBUG SEARCH: New search request stored in DB (ID: {new_search.id})")
    print(f"DEBUG SEARCH: Keywords: '{payload.keyword}' | Location: '{payload.location}'")
    
    # Trigger background worker task
    # If explicitly configured for production (Render/Docker), we use Celery
    try:
        if os.getenv("REDIS_URL"):
            # Offload to Celery Worker
            run_lead_search_task.delay(new_search.id, payload.keyword, payload.location, payload.lead_count, payload.owner_id, payload.platform)
            print(f"DEBUG SEARCH: Celery task queued for search ID {new_search.id}")
        else:
            # Local development fallback for when Redis isn't running
            # We use an inline worker-like execution via BackgroundTasks
            background_tasks.add_task(run_lead_search_task, new_search.id, payload.keyword, payload.location, payload.lead_count, payload.owner_id, payload.platform)
            print(f"DEBUG SEARCH: Local BackgroundTask triggered for search ID {new_search.id}")
    except Exception as e:
        print(f"DEBUG SEARCH: Failed to trigger background task: {e}")
        # Final safety fallback
        background_tasks.add_task(run_lead_search_task, new_search.id, payload.keyword, payload.location, payload.lead_count, payload.owner_id, payload.platform)

    return SearchRequestResponse(
        id=new_search.id,
        keyword=new_search.keyword,
        location=new_search.location,
        lead_count=new_search.lead_count,
        owner_id=new_search.owner_id,
        platform=new_search.platform,
        status=new_search.status,
        created_at=new_search.created_at
    )
    
    return SearchRequestResponse(
        id=new_search.id,
        keyword=new_search.keyword,
        location=new_search.location,
        lead_count=new_search.lead_count,
        owner_id=new_search.owner_id,
        platform=new_search.platform,
        status=new_search.status,
        created_at=new_search.created_at
    )

@router.get("/{search_id}/status")
async def get_search_status(search_id: int, db: Session = Depends(get_db)):
    """Returns the status and progress of a search."""
    search_req = db.query(SearchRequest).filter(SearchRequest.id == search_id).first()
    if not search_req:
        raise HTTPException(status_code=404, detail="Search not found")
        
    leads_found = db.query(Lead).filter(Lead.search_id == search_id).count()
    
    return {
        "id": search_id,
        "status": search_req.status,
        "leads_found": leads_found
    }

@router.get("/{search_id}/leads", response_model=List[LeadResponse])
async def get_search_leads(search_id: int, db: Session = Depends(get_db)):
    """Fetches all leads discovered during a specific search."""
    leads = db.query(Lead).filter(Lead.search_id == search_id).all()
    print(f"DEBUG 9: Leads returned from API (Count: {len(leads)})")
    return leads

@router.get("/debug/{search_id}")
async def get_search_pipeline_state(search_id: int, db: Session = Depends(get_db)):
    """Diagnostic endpoint providing full breakdown for Phase N & O."""
    search_req = db.query(SearchRequest).filter(SearchRequest.id == search_id).first()
    if not search_req:
        return {"error": "Search not found"}
        
    return {
        "search_id": search_req.id,
        "query": f"{search_req.keyword} in {search_req.location}",
        "candidate_urls": search_req.candidate_urls,
        "candidate_count": len(search_req.candidate_urls or []),
        "accepted_leads": search_req.accepted_leads,
        "rejected_leads": search_req.rejected_leads,
        "rejection_reasons": search_req.rejection_reasons,
        "status": search_req.status
    }

@router.get("/{search_id}/status")
async def get_search_status(search_id: int, db: Session = Depends(get_db)):
    """Returns the status and progress of a search."""
    search_req = db.query(SearchRequest).filter(SearchRequest.id == search_id).first()
    if not search_req:
        raise HTTPException(status_code=404, detail="Search not found")
        
    leads_found = db.query(Lead).filter(Lead.search_id == search_id).count()
    
    return {
        "id": search_id,
        "status": search_req.status,
        "leads_found": leads_found
    }

@router.get("/{search_id}/leads", response_model=List[LeadResponse])
async def get_search_leads(search_id: int, db: Session = Depends(get_db)):
    """Fetches all leads discovered during a specific search."""
    leads = db.query(Lead).filter(Lead.search_id == search_id).all()
    print(f"DEBUG 9: Leads returned from API (Count: {len(leads)})")
    return leads

@router.get("/debug/{search_id}")
async def get_search_pipeline_state(search_id: int, db: Session = Depends(get_db)):
    """Diagnostic endpoint providing full breakdown for search pipeline."""
    search_req = db.query(SearchRequest).filter(SearchRequest.id == search_id).first()
    if not search_req:
        return {"error": "Search not found"}
        
    return {
        "search_id": search_req.id,
        "query": f"{search_req.keyword} in {search_req.location}",
        "candidate_urls": search_req.candidate_urls,
        "candidate_count": len(search_req.candidate_urls or []),
        "accepted_leads": search_req.accepted_leads,
        "rejected_leads": search_req.rejected_leads,
        "rejection_reasons": search_req.rejection_reasons,
        "status": search_req.status
    }

@router.post("/test-url")
async def test_single_url(url: str, db: Session = Depends(get_db)):
    """Diagnostic endpoint to test scraping on a single URL without a search request."""
    print(f"DEBUG: Manually testing scraping for URL: {url}")
    scraped_data, reason = await scrape_service.scrape_website(url)
    
    if not scraped_data:
        return {"status": "failed", "detail": f"Scraper returned None. Reason: {reason}"}
        
    return {
        "status": "success",
        "data": scraped_data.dict()
    }
