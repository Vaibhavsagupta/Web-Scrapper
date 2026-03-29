from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.lead import Lead, SearchRequest
from app.schemas.lead_schema import LeadResponse, SearchRequestCreate, SearchRequestResponse
from app.services.lead_discovery_service import LeadDiscoveryService
from app.services.scrape_service import ScrapeService
import time

router = APIRouter(prefix="/api/search", tags=["Search & Lead Discovery"])
discovery_service = LeadDiscoveryService()
scrape_service = ScrapeService()

def run_lead_search_task(search_id: int, keyword: str, location: str, lead_count: int, owner_id: str, db: Session):
    """Background task to discover and scrape leads."""
    try:
        print(f"DEBUG 3: Background task started for search: {search_id}")
        
        # Step 1: Discover candidate URLs dynamically
        candidate_urls = discovery_service.find_leads(keyword, location, count=lead_count)
        
        if not candidate_urls:
            print(f"DEBUG: Real discovery failed or came back empty. Aborting extraction phase.")
        else:
            print(f"DEBUG 4: Candidate URLs discovered dynamically: {candidate_urls}")
        
        valid_count = 0
        rejected_count = 0
        rejection_reasons = []

        for url in candidate_urls:
            print(f"DEBUG 5: Scraping URL: {url}")
            # Step 2: Scrape the URL
            scraped_lead_data, rejection_reason = scrape_service.scrape_website(url)
            
            if scraped_lead_data:
                # Step 3: Save to DB
                lead_dict = scraped_lead_data.dict()
                lead_dict["search_id"] = search_id
                lead_dict["owner_id"] = owner_id
                
                print(f"DEBUG FINAL LEAD OBJECT BEFORE SAVE: {lead_dict}")
                try:
                    new_lead = Lead(**lead_dict)
                    db.add(new_lead)
                    db.commit()
                    db.refresh(new_lead)
                    valid_count += 1
                    print(f"DEBUG 8: Lead saved to DB with ID: {new_lead.id} / Name: {new_lead.company_name}")
                except Exception as e:
                    print(f"DB SAVE ERROR: {str(e)}")
                    db.rollback()
            else:
                rejected_count += 1
                if rejection_reason:
                    rejection_reasons.append(f"{url}: {rejection_reason}")
                print(f"DEBUG 7: Validation failed/rejected. Reason: {rejection_reason}")
        
        # Step 4: Update Search Request status
        search_req = db.query(SearchRequest).filter(SearchRequest.id == search_id).first()
        if search_req:
            search_req.status = "completed"
            search_req.candidate_urls = candidate_urls
            search_req.accepted_leads = valid_count
            search_req.rejected_leads = rejected_count
            search_req.rejection_reasons = list(set(rejection_reasons))
            db.commit()
            print(f"DEBUG: Search task {search_id} COMPLETED. Valid leads saved: {valid_count}, Rejected: {rejected_count}")
            
    except Exception as e:
        print(f"Background task error: {e}")
        db.rollback()

@router.post("/", response_model=SearchRequestResponse)
async def start_search(payload: SearchRequestCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Starts a new lead search campaign."""
    print("DEBUG 1: Search request received")
    
    # 1. Create search request entry
    new_search = SearchRequest(
        keyword=payload.keyword,
        location=payload.location,
        lead_count=payload.lead_count,
        owner_id=payload.owner_id,
        status="running"
    )
    db.add(new_search)
    db.commit()
    db.refresh(new_search)
    print(f"DEBUG 2: Search record created: {new_search.id}")
    
    # 2. Trigger background worker task
    background_tasks.add_task(run_lead_search_task, new_search.id, payload.keyword, payload.location, payload.lead_count, payload.owner_id, db)
    
    return SearchRequestResponse(
        id=new_search.id,
        keyword=new_search.keyword,
        location=new_search.location,
        lead_count=new_search.lead_count,
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

@router.post("/test-url")
async def test_single_url(url: str, db: Session = Depends(get_db)):
    """Diagnostic endpoint to test scraping on a single URL without a search request."""
    print(f"DEBUG: Manually testing scraping for URL: {url}")
    scraped_data, reason = scrape_service.scrape_website(url)
    
    if not scraped_data:
        return {"status": "failed", "detail": f"Scraper returned None. Reason: {reason}"}
        
    return {
        "status": "success",
        "data": scraped_data.dict()
    }
