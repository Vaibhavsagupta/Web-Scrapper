from typing import Any, Dict, Optional
from app.scrapers.static_scraper import StaticScraper
from app.schemas.lead_schema import LeadCreate
from app.services.clean_service import CleanService
from app.services.validation_service import ValidationService
from datetime import datetime

from typing import Any, Dict, Optional, Tuple

class ScrapeService:
    def __init__(self):
        self.static_scraper = StaticScraper()
        self.clean_service = CleanService()

    def scrape_website(self, url: str) -> Tuple[Optional[LeadCreate], Optional[str]]:
        """Main entry point for scraping a single website."""
        # 1. Scrape Homepage
        result = self.static_scraper.parse_homepage(url)
        if result["status"] == "failed":
            print(f"DEBUG SCRAPE: FAILED to fetch homepage for {url}")
            return None, "Failed to fetch homepage HTML (blocked or down)"
        
        # 2. Extract internal links
        internal_links = result.get("internal_links", {})
        
        # 3. Scrape discovered internal pages for enrichment
        extra_data = self.static_scraper.scrape_internal_pages(internal_links)
        
        # 4. Sources Tracking (Part D, E)
        scraped_pages = [url]
        for link in internal_links.values():
            if link: scraped_pages.append(link)
            
        source_platform = "Official Website"
        if "directory" in url or "listing" in url:
            source_platform = "Business Directory"

        # 5. Combine and Clean Data
        combined_data = {
            "company_name": result.get("company_name", url),
            "website": url,
            "source_url": url,
            "email": (result.get("emails", []) + extra_data.get("emails", []))[0] if (result.get("emails") or extra_data.get("emails")) else None,
            "phone": (result.get("phones", []) + extra_data.get("phones", []))[0] if (result.get("phones") or extra_data.get("phones")) else None,
            "city": None,
            "industry": None,
            "about_text": extra_data.get("about_text", result.get("h1")),
            "services": list(set(result.get("services", []) + extra_data.get("services", []))),
            "linkedin_url": result.get("socials", {}).get("linkedin_url"),
            "instagram_url": result.get("socials", {}).get("instagram_url"),
            "facebook_url": result.get("socials", {}).get("facebook_url"),
            "twitter_url": result.get("socials", {}).get("twitter_url"),
            "youtube_url": result.get("socials", {}).get("youtube_url"),
            "contact_page": internal_links.get("contact_page"),
            "about_page": internal_links.get("about_page"),
            "score": self.calculate_completeness(result, extra_data),
            "data_completeness": self.calculate_completeness(result, extra_data),
            "scrape_status": "success",
            
            # Phase 4: Provenance
            "source_platform": source_platform,
            "source_url": url,
            "discovery_source": "Search Engine (Direct Link Discovery)",
            "discovery_url": url,
            "scraped_pages": scraped_pages[:10], # Limit to avoid large DB blob
            "scraped_at": datetime.utcnow()
        }
        
        # Clean the data
        cleaned_lead = self.clean_service.normalize_lead_data(combined_data)
        
        # 6. Authenticity Validation (Part F, G)
        auth_status, auth_reason = ValidationService.assign_authenticity_status(cleaned_lead)
        cleaned_lead["authenticity_status"] = auth_status
        cleaned_lead["authenticity_reason"] = auth_reason
        
        if ValidationService.is_placeholder_lead(cleaned_lead):
            reason = f"Placeholder / Fake Data Detected"
            print(f"DEBUG REJECT: Lead rejected as a placeholder (Company: {cleaned_lead.get('company_name')})")
            return None, reason
            
        is_real, reason = ValidationService.is_real_lead(cleaned_lead)
        if not is_real:
            print(f"DEBUG REJECT: Lead rejected as not real ({reason})")
            return None, reason
            
        return LeadCreate(**cleaned_lead), None

    def calculate_completeness(self, homepage_res: Dict[str, Any], extra_res: Dict[str, Any]) -> int:
        score = 0
        if homepage_res.get("emails") or extra_res.get("emails"): score += 25
        if homepage_res.get("phones") or extra_res.get("phones"): score += 20
        if homepage_res.get("socials"): score += 15
        if extra_res.get("about_text"): score += 15
        if homepage_res.get("services") or extra_res.get("services"): score += 15
        if homepage_res.get("internal_links", {}).get("contact_page"): score += 10
        return min(score, 100)
