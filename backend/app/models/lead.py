from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(String(50), nullable=True, index=True)
    search_id = Column(Integer, ForeignKey("search_requests.id"), nullable=True)
    
    # Primary Data
    company_name = Column(String(255), index=True)
    website = Column(String(255), nullable=True)
    source_url = Column(String(2048), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    
    # Location
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    
    # Industry & Niche
    industry = Column(String(255), nullable=True)
    about_text = Column(Text, nullable=True)
    services = Column(JSON, nullable=True)
    
    # Social & Professional
    linkedin_url = Column(String(2048), nullable=True)
    instagram_url = Column(String(2048), nullable=True)
    facebook_url = Column(String(2048), nullable=True)
    twitter_url = Column(String(2048), nullable=True)
    youtube_url = Column(String(2048), nullable=True)
    
    # Enrichment Metadata
    contact_page = Column(String(2048), nullable=True)
    about_page = Column(String(2048), nullable=True)
    
    # AI Analysis & Enrichment (Phase 3)
    ai_summary = Column(Text, nullable=True)
    industry_classification = Column(String(100), nullable=True)
    target_segment = Column(String(100), nullable=True)
    pain_points = Column(JSON, nullable=True)
    recommended_pitch = Column(Text, nullable=True)
    qualification_label = Column(String(50), nullable=True)
    ai_relevance_score = Column(Integer, default=0)
    
    # Outreach Messages
    outreach_email = Column(Text, nullable=True)
    outreach_whatsapp = Column(Text, nullable=True)
    outreach_linkedin = Column(Text, nullable=True)
    followup_message = Column(Text, nullable=True)
    
    # Final Scoring
    final_lead_score = Column(Integer, default=0)
    priority_level = Column(String(50), nullable=True)
    
    # Source Tracking & Authenticity (Phase 4)
    source_platform = Column(String(255), nullable=True)
    source_url = Column(String(2048), nullable=True)
    discovery_source = Column(String(255), nullable=True)
    discovery_url = Column(String(2048), nullable=True)
    scraped_pages = Column(JSON, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    authenticity_status = Column(String(100), nullable=True)
    authenticity_reason = Column(Text, nullable=True)
    
    # Scoring & Status
    score = Column(Integer, default=0)
    data_completeness = Column(Integer, default=0)
    scrape_status = Column(String(50), default="pending")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SearchRequest(Base):
    __tablename__ = "search_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True) # Old Placeholder
    owner_id = Column(String(50), nullable=True, index=True)
    keyword = Column(String(255), index=True)
    location = Column(String(255), nullable=True)
    lead_count = Column(Integer, default=50)
    status = Column(String(50), default="pending")
    
    # Debug & Transparency Fields (Added for Forced Debugging Part C & O)
    candidate_urls = Column(JSON, default=list)
    accepted_leads = Column(Integer, default=0)
    rejected_leads = Column(Integer, default=0)
    rejection_reasons = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
