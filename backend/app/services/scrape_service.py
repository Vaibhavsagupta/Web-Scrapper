import asyncio
from typing import Any, Dict, Optional, Tuple
from app.scrapers.static_scraper import StaticScraper
from app.scrapers.platform_scraper import PlatformScraper
from app.schemas.lead_schema import LeadCreate
from app.services.clean_service import CleanService
from app.services.validation_service import ValidationService
from datetime import datetime

class ScrapeService:
    def __init__(self):
        self.static_scraper = StaticScraper()
        self.platform_scraper = PlatformScraper()
        self.clean_service = CleanService()

    async def scrape_website(self, url: str) -> Tuple[Optional[LeadCreate], Optional[str]]:
        """Main entry point for scraping a URL, identifying if it's a website or platform."""
        
        is_platform = any(p in url.lower() for p in ["reddit.com", "linkedin.com"])
        
        if is_platform:
            print(f"DEBUG SCRAPE: Identifying URL {url} as platform. Using PlatformScraper.")
            result = await self.platform_scraper.scrape_platform_url(url)
            if result.get("status") == "failed":
                return None, f"Platform scraping failed: {result.get('error')}"
            
            combined_data = self._prepare_platform_data(url, result)
        else:
            # Original Website scraping logic
            print(f"DEBUG SCRAPE: Identifying URL {url} as business website. Using StaticScraper.")
            homepage_res = self.static_scraper.parse_homepage(url)
            if homepage_res["status"] == "failed":
                return None, "Failed to fetch homepage HTML"
            
            internal_links = homepage_res.get("internal_links", {})
            extra_data = self.static_scraper.scrape_internal_pages(internal_links)
            
            combined_data = self._prepare_website_data(url, homepage_res, extra_data, internal_links)

        # 5. Clean the data
        cleaned_lead = self.clean_service.normalize_lead_data(combined_data)
        
        # 6. Authenticity Validation
        auth_status, auth_reason = ValidationService.assign_authenticity_status(cleaned_lead)
        cleaned_lead["authenticity_status"] = auth_status
        cleaned_lead["authenticity_reason"] = auth_reason
        
        if ValidationService.is_placeholder_lead(cleaned_lead):
            return None, f"Placeholder / Fake Data Detected"
            
        is_real, reason = ValidationService.is_real_lead(cleaned_lead)
        if not is_real:
            return None, reason
            
        return LeadCreate(**cleaned_lead), None

    def _prepare_platform_data(self, url: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Maps platform scraper result to lead schema."""
        return {
            "company_name": result.get("company_name", url),
            "website": url,
            "source_url": url,
            "email": result.get("emails", [])[0] if result.get("emails") else None,
            "phone": result.get("phones", [])[0] if result.get("phones") else None,
            "city": None,
            "industry": None,
            "about_text": result.get("about_text", ""),
            "services": [],
            "linkedin_url": result.get("socials", {}).get("linkedin_url"),
            "instagram_url": result.get("socials", {}).get("instagram_url"),
            "facebook_url": result.get("socials", {}).get("facebook_url"),
            "twitter_url": result.get("socials", {}).get("twitter_url"),
            "youtube_url": result.get("socials", {}).get("youtube_url"),
            "score": self._calculate_platform_completeness(result),
            "data_completeness": self._calculate_platform_completeness(result),
            "scrape_status": "success",
            "source_platform": result.get("source_platform", "Social Media"),
            "discovery_source": f"Platform Discovery ({result.get('source_platform')})",
            "discovery_url": url,
            "scraped_pages": [url],
            "scraped_at": datetime.utcnow()
        }

    def _prepare_website_data(self, url: str, homepage_res: Dict[str, Any], extra_data: Dict[str, Any], internal_links: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Maps website scraper result to lead schema (original logic)."""
        scraped_pages = [url]
        for link in internal_links.values():
            if link: scraped_pages.append(link)
            
        source_platform = "Official Website"
        if "directory" in url or "listing" in url:
            source_platform = "Business Directory"

        return {
            "company_name": homepage_res.get("company_name", url),
            "website": url,
            "source_url": url,
            "email": (homepage_res.get("emails", []) + extra_data.get("emails", []))[0] if (homepage_res.get("emails") or extra_data.get("emails")) else None,
            "phone": (homepage_res.get("phones", []) + extra_data.get("phones", []))[0] if (homepage_res.get("phones") or extra_data.get("phones")) else None,
            "city": None,
            "industry": None,
            "about_text": extra_data.get("about_text", homepage_res.get("h1")),
            "services": list(set(homepage_res.get("services", []) + extra_data.get("services", []))),
            "linkedin_url": homepage_res.get("socials", {}).get("linkedin_url"),
            "instagram_url": homepage_res.get("socials", {}).get("instagram_url"),
            "facebook_url": homepage_res.get("socials", {}).get("facebook_url"),
            "twitter_url": homepage_res.get("socials", {}).get("twitter_url"),
            "youtube_url": homepage_res.get("socials", {}).get("youtube_url"),
            "contact_page": internal_links.get("contact_page"),
            "about_page": internal_links.get("about_page"),
            "score": self.calculate_completeness(homepage_res, extra_data),
            "data_completeness": self.calculate_completeness(homepage_res, extra_data),
            "scrape_status": "success",
            "source_platform": source_platform,
            "discovery_source": "Search Engine (Direct Link Discovery)",
            "discovery_url": url,
            "scraped_pages": scraped_pages[:10],
            "scraped_at": datetime.utcnow()
        }

    def calculate_completeness(self, homepage_res: Dict[str, Any], extra_res: Dict[str, Any]) -> int:
        score = 0
        if homepage_res.get("emails") or extra_res.get("emails"): score += 25
        if homepage_res.get("phones") or extra_res.get("phones"): score += 20
        if homepage_res.get("socials"): score += 15
        if extra_res.get("about_text"): score += 15
        if homepage_res.get("services") or extra_res.get("services"): score += 15
        if homepage_res.get("internal_links", {}).get("contact_page"): score += 10
        return min(score, 100)

    def _calculate_platform_completeness(self, result: Dict[str, Any]) -> int:
        score = 0
        if result.get("emails"): score += 40
        if result.get("phones"): score += 30
        if result.get("socials"): score += 10
        if result.get("about_text"): score += 20
        return min(score, 100)
