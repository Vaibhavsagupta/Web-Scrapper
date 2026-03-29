from bs4 import BeautifulSoup
import re
from typing import Dict, Optional, List
from urllib.parse import urljoin

class LinkFinder:
    # Priority Keywords for internal page detection
    KEYWORDS = {
        'about': ['about', 'company', 'who-we-are', 'our-story', 'about-us'],
        'contact': ['contact', 'reach-us', 'support', 'contact-us', 'location'],
        'services': ['services', 'solutions', 'what-we-do', 'our-work', 'courses', 'programs'],
        'team': ['team', 'leadership', 'founder', 'our-team', 'directors']
    }

    @staticmethod
    def extract_internal_links(base_url: str, html_content: str) -> Dict[str, Optional[str]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        found_links = {
            'about_page': None,
            'contact_page': None,
            'services_page': None,
            'team_page': None
        }

        for link in links:
            href = link['href']
            text = (link.get_text() or "").lower().strip()
            slug = href.lower().rstrip('/')
            
            # Check keywords in both text and slug
            for category, keywords in LinkFinder.KEYWORDS.items():
                if found_links[f'{category}_page']:
                    continue
                
                # If priority match found (exact slug match for common ones) or keyword in text
                if any(kw in slug or kw in text for kw in keywords):
                    # Only accept links within the same domain or relative paths
                    if not href.startswith('http') or base_url.split('/')[2] in href:
                        found_links[f'{category}_page'] = urljoin(base_url, href)

        return found_links
