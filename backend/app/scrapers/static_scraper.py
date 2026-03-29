import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import logging
from app.scrapers.contact_extractor import ContactExtractor
from app.scrapers.social_extractor import SocialExtractor
from app.scrapers.link_finder import LinkFinder
from urllib.parse import urlparse

logger = logging.getLogger("leadforge-scraper")

class StaticScraper:
    TIMEOUT = 10
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    async def fetch_page(self, url: str) -> Optional[str]:
        """Asynchronously fetches the HTML content of a page."""
        try:
            async with httpx.AsyncClient(headers=self.HEADERS, timeout=self.TIMEOUT, verify=False, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.text
                logger.warning(f"⚠️ Fetch failed for {url} - Status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Error fetching {url}: {e}")
            return None

    async def parse_homepage(self, url: str) -> Dict[str, Any]:
        """Orchestrates scraping of the main page and finds internal links."""
        logger.info(f"🕷️ SCRAPING: Attempting to fetch {url}")
        html = await self.fetch_page(url)
        
        if not html:
            return {"status": "failed", "error": "Could not fetch homepage"}
            
        logger.info(f"✨ SUCCESS: Fetched {url} ({len(html)} bytes)")

        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraction
        emails = ContactExtractor.extract_emails(html)
        logger.info(f"📧 Found {len(emails)} emails")
        phones = ContactExtractor.extract_phones(html)
        logger.info(f"📞 Found {len(phones)} phones")
        socials = SocialExtractor.extract_social_links(html)
        internal_links = LinkFinder.extract_internal_links(url, html)
        
        # Business Info
        company_name = soup.title.string.strip() if soup.title else urlparse(url).netloc
        h1 = soup.find('h1').text.strip() if soup.find('h1') else None
        
        # Services Extraction
        services = []
        for tag in soup.find_all(['h2', 'h3']):
            text = tag.get_text().strip()
            if 5 < len(text) < 50:
                services.append(text)

        return {
            "status": "success",
            "company_name": company_name,
            "website": url,
            "source_url": url,
            "emails": emails,
            "phones": phones,
            "socials": socials,
            "internal_links": internal_links,
            "h1": h1,
            "services": services[:10],
            "raw_html": html[:500]
        }

    async def scrape_internal_pages(self, found_links: Dict[str, Optional[str]]) -> Dict[str, List[str]]:
        """Scrapes discovered About, Contact, Services pages for more info."""
        extra_data = {
            "emails": [],
            "phones": [],
            "services": [],
            "about_text": ""
        }
        
        # We only scrape a few relevant pages to save time/resources
        target_keys = ['about', 'contact', 'services']
        tasks = []
        
        for key in target_keys:
            target_url = found_links.get(f"{key}_page")
            if target_url:
                tasks.append(self._scrape_single_internal(key, target_url, extra_data))
        
        if tasks:
            await asyncio.gather(*tasks)
                
        # Deduplication
        extra_data["emails"] = list(set(extra_data["emails"]))
        extra_data["phones"] = list(set(extra_data["phones"]))
        
        return extra_data

    async def _scrape_single_internal(self, key: str, url: str, extra_data: Dict[str, Any]):
        """Helper to scrape a single internal page asynchronously."""
        html = await self.fetch_page(url)
        if not html:
            return
            
        extra_data["emails"].extend(ContactExtractor.extract_emails(html))
        extra_data["phones"].extend(ContactExtractor.extract_phones(html))
        
        if 'about' in key:
            soup = BeautifulSoup(html, 'html.parser')
            ps = soup.find_all('p')
            extra_data["about_text"] = " ".join([p.get_text().strip() for p in ps[:5] if len(p.get_text()) > 20])
