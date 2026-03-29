import asyncio
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright
from app.scrapers.contact_extractor import ContactExtractor
from app.scrapers.social_extractor import SocialExtractor
import re

class PlatformScraper:
    """Specialized scraper for social platforms like Reddit and LinkedIn using Playwright."""
    
    def __init__(self):
        self.browser = None

    async def scrape_platform_url(self, url: str) -> Dict[str, Any]:
        """Scrapes a platform URL using Playwright to handle dynamic content."""
        async with async_playwright() as p:
            # We use a persistent context if possible or just a standard browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            
            print(f"DEBUG PLATFORM SCRAPE: Navigating to {url}")
            try:
                # Use 'domcontentloaded' instead of 'networkidle' as social platforms often have background network activity that never ends
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                
                # Allow 3 seconds for dynamic content to render after DOM is ready
                await asyncio.sleep(3)
                
                content = await page.content()
                title = await page.title()
                
                # Platform specific extraction rules
                if "reddit.com" in url:
                    data = await self._parse_reddit(page, url)
                elif "linkedin.com" in url:
                    data = await self._parse_linkedin(page, url)
                else:
                    data = await self._parse_generic(page, url)
                
                await browser.close()
                return data
            except Exception as e:
                print(f"Error scraping platform URL {url}: {e}")
                if browser:
                    await browser.close()
                return {"status": "failed", "error": str(e)}

    async def _parse_reddit(self, page, url: str) -> Dict[str, Any]:
        """Extracts lead info from a Reddit page."""
        content = await page.content()
        title = await page.title()
        
        # Try to find user/company name in title or specific selectors
        company_name = title.replace(" : reddit", "").replace(" - Reddit", "")
        
        # Emails 
        emails = ContactExtractor.extract_emails(content)
        phones = ContactExtractor.extract_phones(content)
        
        # Look for links in the "About" or sidebar
        # This is a bit complex for Reddit's ever-changing UI, so we use broad regex on content too
        socials = SocialExtractor.extract_social_links(content)
        
        # About text (post body or sidebar description)
        about_text = ""
        try:
            # Try to get the main post content or subreddit description
            desc_element = await page.query_selector("div[data-test-id='post-content'], div[id*='description']")
            if desc_element:
                about_text = await desc_element.inner_text()
        except:
            pass

        return {
            "status": "success",
            "company_name": company_name,
            "website": url,
            "source_url": url,
            "emails": emails,
            "phones": phones,
            "socials": socials,
            "about_text": about_text[:500],
            "source_platform": "Reddit"
        }

    async def _parse_linkedin(self, page, url: str) -> Dict[str, Any]:
        """Extracts lead info from a LinkedIn page."""
        content = await page.content()
        title = await page.title()
        
        # LinkedIn often shows a login wall. If 'Log In' is in the title, we are blocked.
        if "Log In" in title or "Sig In" in title:
            print(f"DEBUG PLATFORM SCRAPE: LinkedIn login wall detected for {url}")
            return {"status": "failed", "error": "LinkedIn login wall detected"}

        company_name = title.split("|")[0].strip()
        
        emails = ContactExtractor.extract_emails(content)
        phones = ContactExtractor.extract_phones(content)
        socials = SocialExtractor.extract_social_links(content)
        
        about_text = ""
        try:
            # Try to find the 'About' section
            about_element = await page.query_selector("section.about-section, .core-section-container")
            if about_element:
                about_text = await about_element.inner_text()
        except:
            pass

        return {
            "status": "success",
            "company_name": company_name,
            "website": url,
            "source_url": url,
            "emails": emails,
            "phones": phones,
            "socials": socials,
            "about_text": about_text[:500],
            "source_platform": "LinkedIn"
        }

    async def _parse_generic(self, page, url: str) -> Dict[str, Any]:
        content = await page.content()
        title = await page.title()
        
        return {
            "status": "success",
            "company_name": title,
            "website": url,
            "source_url": url,
            "emails": ContactExtractor.extract_emails(content),
            "phones": ContactExtractor.extract_phones(content),
            "socials": SocialExtractor.extract_social_links(content),
            "about_text": "",
            "source_platform": "Social Media"
        }
