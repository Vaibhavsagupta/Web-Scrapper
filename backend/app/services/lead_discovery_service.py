import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import quote_plus, unquote
import logging
import asyncio

logger = logging.getLogger("leadforge-discovery")

class LeadDiscoveryService:
    """Discovers candidate business URLs using Playwright with httpx fallback."""
    
    SEARCH_URL = "https://duckduckgo.com/html/?q="
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    async def find_leads(self, keyword: str, location: str, count: int = 10, platform: str = "all") -> List[str]:
        """Finds true lead URLs. Tries Playwright first, then httpx fallback."""
        
        query = self._build_query(keyword, location, platform)
        logger.info(f"🔎 DISCOVERY: Starting search for query: '{query}'")
        
        # 1. Try Playwright (Headless Browser)
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(user_agent=self.HEADERS['User-Agent'])
                await page.goto(f"{self.SEARCH_URL}{quote_plus(query)}", wait_until="domcontentloaded", timeout=20000)
                content = await page.content()
                await browser.close()
                links = self._parse_ddg_html(content, count)
                if links:
                    logger.info(f"✅ DISCOVERY: Playwright found {len(links)} leads.")
                    return links
        except Exception as e:
            logger.warning(f"⚠️ DISCOVERY: Playwright failed or not available: {e}. Trying static fallback...")

        # 2. Try Static Fallback (httpx)
        try:
            async with httpx.AsyncClient(headers=self.HEADERS, timeout=15, follow_redirects=True) as client:
                res = await client.get(f"{self.SEARCH_URL}{quote_plus(query)}")
                if res.status_code == 200:
                    links = self._parse_ddg_html(res.text, count)
                    if links:
                        logger.info(f"✅ DISCOVERY: Static fallback found {len(links)} leads.")
                        return links
                logger.error(f"❌ DISCOVERY: Static fallback failed - Status: {res.status_code}")
        except Exception as e:
            logger.error(f"🔥 DISCOVERY: All discovery methods failed: {e}")
            
        return []

    def _build_query(self, keyword: str, location: str, platform: str) -> str:
        if platform.lower() == "reddit":
            return f'"{keyword}" "{location}" site:reddit.com'
        elif platform.lower() == "linkedin":
            return f'"{keyword}" "{location}" site:linkedin.com'
        return f'"{keyword}" "{location}" business website'

    def _parse_ddg_html(self, html: str, count: int) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        blocked_domains = [
            "google", "gstatic", "youtube", "facebook", "instagram", 
            "justdial", "sulekha", "indiamart", "duckduckgo", "magicbricks", 
            "99acres", "housing.com", "goodfirms.co", "realestateindia", "glassdoor", "yelp"
        ]
        
        for a in soup.find_all('a', href=True):
            url = unquote(a['href'].strip())
            
            # Peel redirects (uddg= parameter)
            if 'uddg=' in url:
                idx = url.find('uddg=')
                url = unquote(url[idx+5:].split('&')[0])
                # Remove extra trailing garbage from DDG redirects
                if '&' in url: url = url.split('&')[0]
            elif any(x in url for x in ['/l/?', 'duckduckgo.com']):
                continue
            
            if url.startswith("http") and not any(d in url.lower() for d in blocked_domains):
                links.append(url)
                if len(links) >= count:
                    break
                    
        return list(set(links))
