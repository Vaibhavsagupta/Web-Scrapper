from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime

class LeadBase(BaseModel):
    company_name: str
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    industry: Optional[str] = None

class LeadCreate(LeadBase):
    source_url: Optional[str] = None
    about_text: Optional[str] = None
    services: Optional[List[str]] = []
    linkedin_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    youtube_url: Optional[str] = None
    contact_page: Optional[str] = None
    about_page: Optional[str] = None
    score: Optional[int] = 0
    data_completeness: Optional[int] = 0
    scrape_status: Optional[str] = "pending"
    
    # Source Tracking (Phase 4)
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    discovery_source: Optional[str] = None
    discovery_url: Optional[str] = None
    scraped_pages: Optional[List[str]] = []
    scraped_at: Optional[datetime] = None
    authenticity_status: Optional[str] = "Verified Public Source"
    authenticity_reason: Optional[str] = None

class LeadResponse(LeadCreate):
    id: int
    search_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class SearchRequestCreate(BaseModel):
    keyword: str
    location: str
    lead_count: Optional[int] = 50
    owner_id: Optional[str] = None

class SearchRequestResponse(SearchRequestCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
