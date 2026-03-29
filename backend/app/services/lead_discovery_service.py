import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import quote_plus

class LeadDiscoveryService:
    """Discovers candidate business URLs based on keyword and location."""
    
    SEARCH_URL = "https://lite.duckduckgo.com/lite/"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    def find_leads(self, keyword: str, location: str, count: int = 10, platform: str = "all") -> List[str]:
        """Finds true lead URLs using DuckDuckGo Lite, supporting specific platforms."""
        
        # Build search query based on platform preference
        if platform.lower() == "reddit":
            query = f"{keyword} {location} on reddit.com"
        elif platform.lower() == "linkedin":
            query = f"{keyword} {location} on linkedin.com"
        else:
            # General business discovery
            query = f"{keyword} {location} (business OR company OR office)"
        
        print(f"DEBUG DISCOVERY: Searching for platform '{platform}' with query: '{query}'")
        
        try:
            # Send POST to DuckDuckGo Lite version
            response = requests.post(
                self.SEARCH_URL,
                data={"q": query},
                headers=self.HEADERS,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"DEBUG DISCOVERY: Search returned status {response.status_code}. Attempting to parse body anyway.")
                
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            # Platforms we usually block but might want now
            platform_domains = ["reddit.com", "linkedin.com"]
            
            blocked_domains = [
                "google", "gstatic", "youtube", "facebook", "instagram", 
                "justdial", "sulekha", "indiamart", "duckduckgo", "magicbricks", 
                "99acres", "housing.com", "goodfirms.co", "realestateindia"
            ]
            
            # If not searching for a specific platform, keep blocking them
            if platform.lower() == "all":
                blocked_domains.extend(platform_domains)
            
            # Extract all links that lead to actual domain names
            for a in soup.find_all('a', href=True):
                url = a['href']
                
                # Extract real URL from DuckDuckGo redirect if needed
                if 'duckduckgo.com/l/?' in url or url.startswith('/l/?'):
                    if 'uddg=' in url:
                        # Find the uddg parameter
                        from urllib.parse import unquote
                        idx = url.find('uddg=')
                        url = unquote(url[idx+5:].split('&')[0])
                
                # Ensure it has http/https and isn't blocked list
                if url.startswith("http") and "duckduckgo.com" not in url:
                    is_blocked = any(d in url.lower() for d in blocked_domains)
                    
                    # Special check: If we're looking for a platform, ensure it's that platform
                    if platform.lower() != "all" and platform.lower() != "website":
                        is_platform = platform.lower() in url.lower()
                        if not is_platform:
                            continue

                    if not is_blocked:
                        links.append(url)
                        print(f"DEBUG DISCOVERY: Found valid URL: {url}")
                        if len(links) >= count:
                            break
            
            if not links:
                print(f"DEBUG DISCOVERY: No links found for query '{query}'")
                return []
                
            return list(set(links))
        except Exception as e:
            print(f"Discovery error: {e}")
            return []
