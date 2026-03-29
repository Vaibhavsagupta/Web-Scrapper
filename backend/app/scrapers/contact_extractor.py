import re
from typing import List, Optional

class ContactExtractor:
    # Regex for standard email format
    EMAIL_REGEX = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    
    # Common phone number patterns (Supports +91, 0, whitespace, dashes, parenthesized area codes)
    PHONE_REGEX = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}'

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        if not text:
            return []
        emails = re.findall(ContactExtractor.EMAIL_REGEX, text)
        # Unique and lower case
        return list(set(email.lower() for email in emails))

    @staticmethod
    def extract_phones(text: str) -> List[str]:
        if not text:
            return []
        # Find all phone number patterns safely using finditer
        matches = re.finditer(ContactExtractor.PHONE_REGEX, text)
        phones = []
        for doc_match in matches:
            raw_phone = doc_match.group(0).strip()
            # Only keep if it actually contains a reasonable amount of digits (8 to 15)
            digit_count = sum(c.isdigit() for c in raw_phone)
            if 8 <= digit_count <= 15:
                phones.append(raw_phone)
        return list(set(phones))

    @staticmethod
    def extract_from_mailto(html_content: str) -> List[str]:
        if not html_content:
            return []
        mailto_matches = re.findall(r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', html_content)
        return list(set(email.lower() for email in mailto_matches))

    @staticmethod
    def extract_from_tel(html_content: str) -> List[str]:
        if not html_content:
            return []
        tel_matches = re.findall(r'tel:([\+\d\s\-\(\)]+)', html_content)
        return list(set(tel_matches))
