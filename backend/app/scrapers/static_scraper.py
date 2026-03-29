import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
from app.scrapers.contact_extractor import ContactExtractor
from app.scrapers.social_extractor import SocialExtractor
from app.scrapers.link_finder import LinkFinder
from urllib.parse import urlparse

class StaticScraper:
    TIMEOUT = 10
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=self.TIMEOUT, verify=False)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_homepage(self, url: str) -> Dict[str, Any]:
        """Orchestrates scraping of the main page and finds internal links."""
        html = self.fetch_page(url)
        print(f"DEBUG SCRAPE: Attempting to fetch {url}")
        if not html:
            print(f"DEBUG SCRAPE: FAILED to fetch {url}")
            return {"status": "failed", "error": "Could not fetch homepage"}
            
        print(f"DEBUG SCRAPE: SUCCESS! HTML Length: {len(html)}")

        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraction
        emails = ContactExtractor.extract_emails(html)
        print(f"DEBUG EXTRACTION: Found {len(emails)} emails")
        phones = ContactExtractor.extract_phones(html)
        print(f"DEBUG EXTRACTION: Found {len(phones)} phones")
        socials = SocialExtractor.extract_social_links(html)
        internal_links = LinkFinder.extract_internal_links(url, html)
        print(f"DEBUG EXTRACTION: Found internal links keys: {list(internal_links.keys())}")
        
        # Business Info
        company_name = soup.title.string.strip() if soup.title else urlparse(url).netloc
        h1 = soup.find('h1').text.strip() if soup.find('h1') else None
        
        # Services Extraction (Basic Phase 1)
        services = []
        # Find headings or lists that might be services
        for tag in soup.find_all(['h2', 'h3']):
            text = tag.get_text().strip()
            if len(text) > 5 and len(text) < 50:
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
            "services": services[:10], # Limit for now
            "raw_html": html[:1000] # For debugging
        }

    def scrape_internal_pages(self, found_links: Dict[str, Optional[str]]) -> Dict[str, List[str]]:
        """Scrapes discovered About, Contact, Services pages for more info."""
        extra_data = {
            "emails": [],
            "phones": [],
            "services": [],
            "about_text": ""
        }
        
        for key, url in found_links.items():
            if not url:
                continue
                
            html = self.fetch_page(url)
            if not html:
                continue
                
            # Accumulate data
            extra_data["emails"].extend(ContactExtractor.extract_emails(html))
            extra_data["phones"].extend(ContactExtractor.extract_phones(html))
            
            if 'about' in key:
                soup = BeautifulSoup(html, 'html.parser')
                ps = soup.find_all('p')
                # Take first 3-5 paragraphs for about text
                extra_data["about_text"] = " ".join([p.get_text().strip() for p in ps[:5] if len(p.get_text()) > 20])
                
        # Deduplication
        extra_data["emails"] = list(set(extra_data["emails"]))
        extra_data["phones"] = list(set(extra_data["phones"]))
        
        return extra_data
