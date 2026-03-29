import asyncio
from app.scrapers.platform_scraper import PlatformScraper

async def test():
    scraper = PlatformScraper()
    url = "https://www.reddit.com/r/dentistry/"
    print(f"Testing PlatformScraper for {url}...")
    result = await scraper.scrape_platform_url(url)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test())
