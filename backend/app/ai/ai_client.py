import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from typing import Optional, Dict, Any

load_dotenv()

class AIClient:
    def __init__(self):
        # Fallback to a mock response if no API key is set for demo purposes
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.active = True
        else:
            self.active = False
            print("GEMINI_API_KEY not found. AI features will run in Mock mode.")

    async def call_llm(self, prompt: str, system_instruction: str = "") -> str:
        """Call Gemini API and return the raw text response."""
        if not self.active:
            return self._mock_llm_response(prompt)
            
        try:
            # For Gemini 1.5, system instructions are handled in the model config
            chat = self.model.start_chat()
            full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
            response = chat.send_message(full_prompt)
            return response.text
        except Exception as e:
            print(f"LLM Call Error: {e}")
            return json.dumps({"error": f"API Request Failed: {str(e)}"})

    async def call_llm_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """Call LLM and parse the response as JSON (with error handling for formatting)."""
        # Ensure we ask for JSON in the prompt
        json_prompt = f"{prompt}\nReturn your response ONLY as a valid JSON object."
        result = await self.call_llm(json_prompt, system_instruction)
        
        try:
            # Simple cleanup to remove potential Markdown code blocks backticks
            clean_result = result.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(clean_result)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            return {"error": "AI response was not valid JSON"}

    def _mock_llm_response(self, prompt: str) -> str:
        """Mock fallback for demo when API key is missing."""
        # Simple heuristics for semi-realistic mock responses based on keywords in prompt
        if "summary" in prompt.lower():
            return json.dumps({"ai_summary": "Extracted business information successfully analyzed."})
        if "outreach" in prompt.lower():
            return json.dumps({
                "outreach_email": "Subject: Growth for your business\n\nHi team, we can help you automate your workflows.",
                "whatsapp_message": "Hi, noticed your business. We offer automation services.",
                "linkedin_message": "Hi, interested in your offerings. We help scale through AI.",
                "followup_message": "Just checking if you received my previous note."
            })
        return json.dumps({"message": "Mock AI Response active."})
