import re
from typing import Dict, Any, Tuple

class ValidationService:
    @staticmethod
    def is_real_lead(lead: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates if a lead satisfies minimum authenticity requirements."""
        if not lead.get("company_name") or len(lead.get("company_name", "")) < 3:
            return False, "Lead missing valid company name"
            
        if not (lead.get("website") or lead.get("source_url")):
            return False, "Lead missing source attribution (URL or Website)"
            
        if not lead.get("source_platform"):
            return False, "Lead missing source platform classification"
            
        return True, "Verified"

    @staticmethod
    def is_placeholder_lead(lead: Dict[str, Any]) -> bool:
        """Rejects leads containing known placeholder or fake values."""
        fake_names = ["ABC Coaching", "Demo Company", "Test Institute", "Sample Academy", "example.com"]
        fake_domains = ["example.com", "test.com", "placeholder.com"]
        fake_email_tokens = ["test@", "demo@", "example@", "placeholder@"]

        company = (lead.get("company_name") or "").strip()
        website = (lead.get("website") or "").strip().lower()
        email = (lead.get("email") or "").strip().lower()

        if company in fake_names:
            return True
        if any(domain in website for domain in fake_domains):
            return True
        if any(token in email for token in fake_email_tokens):
            return True
            
        return False

    @staticmethod
    def assign_authenticity_status(lead: Dict[str, Any]) -> Tuple[str, str]:
        """Calculates authenticity score and status labels."""
        status = "Verified Public Source"
        reason = "Lead has valid source URL, platform, and website"

        has_source = lead.get("source_url") or lead.get("discovery_url")
        has_contact = lead.get("email") or lead.get("phone")
        
        if lead.get("source_url") and lead.get("website") and lead.get("source_platform"):
            status = "Verified Public Source"
            reason = "Full source metadata and direct website match found."
        elif has_source or lead.get("website"):
            status = "Low Confidence"
            reason = "Lead has partial source metadata or only a homepage match."
        else:
            status = "Missing Source"
            reason = "Lead missing required source metadata."
            
        if not has_contact:
            status = "Low Confidence"
            reason += " | Note: No contact information extracted."
            
        return status, reason
