import logging
import traceback
from app.core.celery_app import celery_app
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lead import Lead, SearchRequest
from app.services.lead_discovery_service import LeadDiscoveryService
from app.services.scrape_service import ScrapeService

# Configure logging for the worker
logger = logging.getLogger("leadforge-worker")
discovery_service = LeadDiscoveryService()
scrape_service = ScrapeService()

@celery_app.task(bind=True, name="lead_search_task", autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def run_lead_search_task(self, search_id: int, keyword: str, location: str, lead_count: int, owner_id: str, platform: str):
    """
    Celery background task to discover and scrape leads.
    Uses its own fresh DB session for production safety.
    """
    db = SessionLocal()
    logger.info(f"👷 WORKER: Task started for search ID: {search_id} | Platform: {platform}")
    
    try:
        # Step 1: Discover candidate URLs
        logger.info(f"🔎 DISCOVERY: Starting search for '{keyword}' in '{location}'")
        # discovery_service find_leads is normally async, 
        # but in a sync Celery worker we need to bridge it using an event loop
        import asyncio
        loop = asyncio.get_event_loop()
        candidate_urls = loop.run_until_complete(
            discovery_service.find_leads(keyword, location, count=lead_count, platform=platform)
        )
        
        if not candidate_urls:
            logger.warning(f"⚠️ DISCOVERY: No candidates found for {keyword}/{location}. Finalizing.")
        else:
            logger.info(f"✨ DISCOVERY: Found {len(candidate_urls)} candidate URLs.")
        
        valid_count = 0
        rejected_count = 0
        rejection_reasons = []

        # Step 2: Scrape each URL
        for url in candidate_urls:
            try:
                logger.info(f"🕷️ SCRAPER: Processing {url}")
                # scrap_service is also async
                scraped_lead_data, rejection_reason = loop.run_until_complete(
                    scrape_service.scrape_website(url)
                )
                
                if scraped_lead_data:
                    # Step 3: Save to DB
                    lead_dict = scraped_lead_data.dict()
                    lead_dict["search_id"] = search_id
                    lead_dict["owner_id"] = owner_id
                    
                    try:
                        new_lead = Lead(**lead_dict)
                        db.add(new_lead)
                        db.commit()
                        db.refresh(new_lead)
                        valid_count += 1
                        logger.info(f"✅ SAVED: {new_lead.company_name}")
                    except Exception as e:
                        logger.error(f"❌ DB ERROR: {str(e)}")
                        db.rollback()
                else:
                    rejected_count += 1
                    if rejection_reason:
                        rejection_reasons.append(f"{url}: {rejection_reason}")
                    logger.warning(f"🚫 REJECTED: {url} - Reason: {rejection_reason}")
            except Exception as e:
                logger.error(f"💥 CRASH in URL {url}: {e}")
        
        # Step 4: Finalize Search Request status
        search_req = db.query(SearchRequest).filter(SearchRequest.id == search_id).first()
        if search_req:
            search_req.status = "completed"
            search_req.candidate_urls = candidate_urls
            search_req.accepted_leads = valid_count
            search_req.rejected_leads = rejected_count
            search_req.rejection_reasons = list(set(rejection_reasons))
            db.commit()
            logger.info(f"🏁 COMPLETED: Search {search_id} - Approved: {valid_count}, Rejected: {rejected_count}")
            
    except Exception as e:
        logger.error(f"🔥 CRITICAL TASK FAILURE: {e}")
        traceback.print_exc()
        db.rollback()
        raise e # Let Celery handle retry if configured
    finally:
        db.close()
        logger.info(f"🧼 CLEANUP: Task {self.request.id} finished and DB session closed.")
