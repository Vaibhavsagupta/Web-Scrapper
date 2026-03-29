import re
from typing import Dict, Any, List

class CleanService:
    @staticmethod
    def normalize_lead_data(lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize messy extracted data into a cleaner lead object."""
        result = lead_data.copy()

        # 1. Normalize Email
        if result.get("email"):
            result["email"] = result["email"].strip().lower()

        # 2. Normalize Phone (Remove junk characters, spaces, and format +91 if missing)
        if result.get("phone"):
            raw_phone = re.sub(r'[^\d+]', '', result["phone"])
            if len(raw_phone) == 10 and not raw_phone.startswith('+'):
                result["phone"] = f"+91{raw_phone}"
            else:
                result["phone"] = raw_phone

        # 3. Clean Company Name (Remove .com, .in, and unwanted suffixes)
        if result.get("company_name"):
            name = result["company_name"]
            # Basic cleanup of common title tags suffixes
            name = re.sub(r'\s*\|\s*.*$', '', name)
            name = re.sub(r'\s*-\s*.*$', '', name)
            # Remove domain name if it looks like one
            if '.' in name and not ' ' in name:
                name = name.split('.')[0].capitalize()
            result["company_name"] = name.strip()

        # 4. Filter Services (Remove very short or non-relevant strings)
        if result.get("services"):
            services = [s.strip() for s in result["services"] if len(s.strip()) > 5]
            result["services"] = list(set(services))

        # 5. Normalize Website URL (Strip trailing slashes)
        if result.get("website"):
            result["website"] = result["website"].rstrip('/')

        # 6. Normalize Social URLs
        for key in ["linkedin_url", "instagram_url", "facebook_url", "twitter_url", "youtube_url"]:
            if result.get(key):
                result[key] = result[key].rstrip('/')

        # 7. Placeholder for City Inference (Phase 3 will handle this more robustly)
        # For now, look for city names in About Text or Address (Basic)
        cities = ["Bhopal", "Indore", "Delhi", "Mumbai", "Indore", "Bangalore"]
        for city in cities:
            if result.get("about_text") and city.lower() in result["about_text"].lower():
                result["city"] = city
                break
        
        return result
