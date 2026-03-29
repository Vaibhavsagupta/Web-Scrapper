from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import quote_plus, unquote

class LeadDiscoveryService:
    """Discovers candidate business URLs using Playwright to bypass cloud blocks."""
    
    SEARCH_URL = "https://duckduckgo.com/html/?q="
    
    async def find_leads(self, keyword: str, location: str, count: int = 10, platform: str = "all") -> List[str]:
        """Finds true lead URLs using a headless browser to bypass anti-bot protections."""
        
        # Build search query
        if platform.lower() == "reddit":
            query = f'"{keyword}" "{location}" site:reddit.com'
        elif platform.lower() == "linkedin":
            query = f'"{keyword}" "{location}" site:linkedin.com'
        else:
            query = f'"{keyword}" "{location}" business website'
        
        print(f"DEBUG DISCOVERY: Browser-based search starting for query: '{query}'")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            
            try:
                # Go to DuckDuckGo HTML version (simpler to parse)
                await page.goto(f"{self.SEARCH_URL}{quote_plus(query)}", wait_until="networkidle", timeout=30000)
                
                # Get page content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                links = []
                blocked_domains = [
                    "google", "gstatic", "youtube", "facebook", "instagram", 
                    "justdial", "sulekha", "indiamart", "duckduckgo", "magicbricks", 
                    "99acres", "housing.com", "goodfirms.co", "realestateindia", "glassdoor", "yelp"
                ]
                
                # Extract results (HTML version uses 'result__url' or similar)
                for a in soup.find_all('a', href=True):
                    url = unquote(a['href'].strip())
                    
                    # Ignore internal DDG links or obvious junk
                    if any(x in url for x in ['/l/?', 'duckduckgo.com', 'microsoft.com', 'apple.com']):
                        # Check if it's a redirect we can peel
                        if 'uddg=' in url:
                            idx = url.find('uddg=')
                            url = unquote(url[idx+5:].split('&')[0])
                        else:
                            continue
                    
                    if url.startswith("http") and "duckduckgo.com" not in url:
                        is_blocked = any(d in url.lower() for d in blocked_domains)
                        
                        if not is_blocked:
                            links.append(url)
                            print(f"DEBUG DISCOVERY: Found candidate: {url}")
                            if len(links) >= count:
                                break
                
                await browser.close()
                return list(set(links))
                
            except Exception as e:
                print(f"Discovery browser error: {e}")
                await browser.close()
                return []
