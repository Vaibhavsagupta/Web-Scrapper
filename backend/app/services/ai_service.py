from typing import Any, Dict, List, Optional
from app.ai.ai_client import AIClient
from app.models.lead import Lead

class AIService:
    def __init__(self):
        self.ai_client = AIClient()

    async def analyze_full_lead(self, lead: Lead) -> Dict[str, Any]:
        """Runs the entire AI enrichment pipeline for a single lead."""
        # 1. Prepare data for context
        context = {
            "name": lead.company_name,
            "website": lead.website,
            "about": lead.about_text or "No detailed description available.",
            "services": ", ".join(lead.services) if lead.services else "Unknown",
        }
        
        # 2. Generate Analysis and Outreach in a single efficient call (saves costs)
        analysis_prompt = f"""
        Analyze the following business:
        Name: {context['name']}
        Website: {context['website']}
        Initial Info: {context['about']}
        Key Services: {context['services']}
        
        Generate the following in JSON format:
        1. ai_summary: A concise 1-2 sentence description.
        2. industry: Classify the business into a specific niche (e.g., Coaching Clinic, CA Firm).
        3. target_segment: Who are their main customers?
        4. pain_points: A list of 2-3 likely business problems.
        5. recommended_pitch: A one-sentence value proposition for an automation service.
        6. ai_relevance_score: A score from 0 to 50 based on how clear the business value is.
        7. outreach_email: A cold email draft (include a subject line).
        8. outreach_whatsapp: A short message for WhatsApp.
        9. outreach_linkedin: A brief professional LinkedIn pitch.
        10. followup_message: A short follow-up note.
        """
        
        system_instruction = "You are an expert sales strategist and business analyst."
        
        try:
            full_analysis = await self.ai_client.call_llm_json(analysis_prompt, system_instruction)
            
            # 3. Qualification Logic (Heuristic based on score)
            score = full_analysis.get("ai_relevance_score", 0)
            qualification = "High Potential" if score > 35 else "Medium Potential" if score > 20 else "Low Potential"
            full_analysis["qualification_label"] = qualification
            
            return full_analysis
        except Exception as e:
            print(f"AI Enrichment Failed: {e}")
            return {"error": "AI processing error"}

    def calculate_final_score(self, rule_score: int, ai_score: int) -> Dict[str, Any]:
        """Combines rule-based and AI scores for final ranking."""
        final_score = min(100, rule_score + ai_score)
        
        if final_score >= 85:
            priority = "High Priority"
        elif final_score >= 65:
            priority = "Medium Priority"
        elif final_score >= 40:
            priority = "Low Priority"
        else:
            priority = "Weak Lead"
            
        return {
            "final_score": final_score,
            "priority": priority
        }
