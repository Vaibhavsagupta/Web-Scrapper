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

    def find_leads(self, keyword: str, location: str, count: int = 10) -> List[str]:
        """Finds true lead URLs using DuckDuckGo Lite, excluding directory aggregators."""
        # Force the engine to give us actual businesses by excluding common directories
        anti_directory_terms = "-justdial -sulekha -indiamart -magicbricks -99acres -housing.com -quikr -olx -glassdoor -linkedin -facebook -yelp -yellowpages"
        query = f"{keyword} {location} {anti_directory_terms}"
        
        try:
            # Send POST to DuckDuckGo Lite version which has no JS/captcha requirements
            response = requests.post(
                self.SEARCH_URL,
                data={"q": query},
                headers=self.HEADERS,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"DEBUG DISCOVERY: Search failed with status {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            blocked_domains = [
                "google", "gstatic", "youtube", "facebook", "linkedin", "instagram", 
                "justdial", "sulekha", "indiamart", "duckduckgo", "magicbricks", 
                "99acres", "housing.com", "goodfirms.co", "realestateindia"
            ]
            
            # Extract all links that lead to actual domain names
            for a in soup.find_all('a', href=True):
                url = a['href']
                
                # Cleanup DuckDuckGo redirect prefixes if they exist
                if url.startswith('//duckduckgo.com/l/?') or url.startswith('/l/?'):
                    continue
                    
                # Ensure it has http/https and isn't blocked list
                if url.startswith("http") and "duckduckgo.com" not in url:
                    if not any(d in url.lower() for d in blocked_domains):
                        links.append(url)
                        if len(links) >= count:
                            break
            
            # If no real links found, return empty list (No mocks allowed)
            if not links:
                print(f"DEBUG DISCOVERY: No real links found for {keyword} in {location}")
                return []
                
            return list(set(links))                
            return list(set(links))
        except Exception as e:
            print(f"Discovery error: {e}")
            return []
