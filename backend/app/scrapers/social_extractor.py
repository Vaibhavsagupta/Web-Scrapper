import re
from typing import Dict, Optional, List

class SocialExtractor:
    SOCIAL_PLATFORMS = {
        'linkedin': r'(https?://(www\.)?linkedin\.com/(company|in)/[A-Za-z0-9_-]+)',
        'instagram': r'(https?://(www\.)?instagram\.com/[A-Za-z0-9_.-]+)',
        'facebook': r'(https?://(www\.)?facebook\.com/[A-Za-z0-9.]+)',
        'twitter': r'(https?://(www\.)?(twitter|x)\.com/[A-Za-z0-9_]+)',
        'youtube': r'(https?://(www\.)?youtube\.com/(channel|user|@)?[A-Za-z0-9_-]+)'
    }

    @staticmethod
    def extract_social_links(html_content: str) -> Dict[str, Optional[str]]:
        results = {
            'linkedin_url': None,
            'instagram_url': None,
            'facebook_url': None,
            'twitter_url': None,
            'youtube_url': None
        }

        # Look for links in href attributes or raw text
        for platform, regex in SocialExtractor.SOCIAL_PLATFORMS.items():
            matches = re.findall(regex, html_content)
            if matches:
                # Get the first match (usually the most relevant)
                url = matches[0][0]
                results[f'{platform}_url'] = url.rstrip('/')

        return results
