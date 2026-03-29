from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.lead import Lead
from app.services.ai_service import AIService
from typing import Dict, Any

router = APIRouter(prefix="/api/ai", tags=["AI Enrichment & Outreach"])
ai_service = AIService()

async def run_ai_enrichment_task(lead_id: int, db: Session):
    """Background task to fully enrich a lead with AI analysis and outreach."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return
        
    try:
        # Run AI Pipeline
        full_analysis = await ai_service.analyze_full_lead(lead)
        
        import json
        
        # Helper to force strings on text columns
        def force_str(val):
            if isinstance(val, (dict, list)):
                return json.dumps(val)
            return str(val) if val is not None else ""
            
        # Handle API Errors gracefully
        if "error" in full_analysis:
            lead.ai_summary = f"API Error: {full_analysis['error']}. Please wait a minute and try again. (Rate Limit or Quota Exceeded)"
            lead.industry_classification = "N/A"
            lead.target_segment = "N/A"
            lead.pain_points = ["API Quota Exceeded"]
            lead.recommended_pitch = "N/A"
            lead.qualification_label = "Pending"
            lead.ai_relevance_score = 0
            # Set minimum outreach to stop polling loop
            lead.outreach_email = "API limit reached. Could not generate email."
            lead.outreach_whatsapp = "API limit reached."
            lead.outreach_linkedin = "API limit reached."
            lead.followup_message = ""
            
            scoring = ai_service.calculate_final_score(int(lead.data_completeness or 0), 0)
            lead.final_lead_score = scoring["final_score"]
            lead.priority_level = scoring["priority"]
            
            db.commit()
            return

        # Update Lead model with AI data
        lead.ai_summary = force_str(full_analysis.get("ai_summary", ""))
        lead.industry_classification = force_str(full_analysis.get("industry", ""))
        lead.target_segment = force_str(full_analysis.get("target_segment", ""))
        
        # Pain points is native JSON column
        pp = full_analysis.get("pain_points", [])
        lead.pain_points = pp if isinstance(pp, list) else [str(pp)]
        
        lead.recommended_pitch = force_str(full_analysis.get("recommended_pitch", ""))
        lead.qualification_label = force_str(full_analysis.get("qualification_label", "Medium Potential"))
        
        try:
            ai_score_raw = str(full_analysis.get("ai_relevance_score", 0)).replace("/50", "").replace("/100", "").strip()
            score_val = int("".join(filter(str.isdigit, ai_score_raw)) or 0)
        except:
            score_val = 0
            
        lead.ai_relevance_score = score_val
        
        # Outreach
        lead.outreach_email = force_str(full_analysis.get("outreach_email", ""))
        lead.outreach_whatsapp = force_str(full_analysis.get("outreach_whatsapp", ""))
        lead.outreach_linkedin = force_str(full_analysis.get("outreach_linkedin", ""))
        lead.followup_message = force_str(full_analysis.get("followup_message", ""))
        
        # Final Scoring (Hybrid)
        scoring = ai_service.calculate_final_score(int(lead.data_completeness or 0), score_val)
        lead.final_lead_score = scoring["final_score"]
        lead.priority_level = scoring["priority"]
        
        db.commit()
    except Exception as e:
        print(f"AI enrichment task failed: {e}")
        db.rollback()

@router.post("/analyze-lead/{lead_id}")
async def analyze_lead(lead_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers AI analysis for a single discovered lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # Clear old AI summary to ensure the frontend polling loop correctly waits for the new generated data
    lead.ai_summary = ""
    db.commit()
        
    background_tasks.add_task(run_ai_enrichment_task, lead_id, db)
    return {"status": "AI enrichment started", "lead_id": lead_id}

@router.get("/lead-insights/{lead_id}")
async def get_lead_insights(lead_id: int, db: Session = Depends(get_db)):
    """Fetches AI-enriched insights for the dashboard."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return {
        "ai_summary": lead.ai_summary,
        "industry": lead.industry_classification,
        "segment": lead.target_segment,
        "pain_points": lead.pain_points,
        "pitch": lead.recommended_pitch,
        "score": lead.ai_relevance_score,
        "qualification": lead.qualification_label,
        "outreach": {
            "email": lead.outreach_email,
            "whatsapp": lead.outreach_whatsapp,
            "linkedin": lead.outreach_linkedin,
            "followup": lead.followup_message
        }
    }
