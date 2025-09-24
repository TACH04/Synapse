"""
Conversation Engine for AI Patient Simulation
Handles communication with Google Gemini API to simulate patient responses
"""

import os
import json
from typing import Dict, List
import google.generativeai as genai
from datetime import datetime
from .mock_responses import get_mock_response

class ConversationEngine:
    def __init__(self, api_key: str = None):
        # Prefer GOOGLE_API_KEY, fall back to OPENAI_API_KEY for compatibility
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.client = None
        self.conversation_history = []

        # Configure Gemini if API key is present
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    def _get_client(self):
        if self.client is None:
            if self.api_key:
                genai.configure(api_key=self.api_key)
        return self.client

    def create_patient_prompt(self, scenario: str, patient_profile: Dict) -> str:
        """Create a detailed prompt for the AI patient"""
        return f"""
You are simulating a hospice patient in a difficult conversation with their doctor. 
Your role is to respond naturally and emotionally as this patient would.

PATIENT PROFILE:
- Name: {patient_profile.get('name', 'Patient')}
- Age: {patient_profile.get('age', 65)}
- Condition: {patient_profile.get('condition', 'Terminal illness')}
- Personality: {patient_profile.get('personality', 'Reserved and thoughtful')}
- Emotional State: {patient_profile.get('emotional_state', 'Anxious and fearful')}
- Background: {patient_profile.get('background', 'Family-oriented with adult children')}

SCENARIO: {scenario}

INSTRUCTIONS:
- Respond as this specific patient would in a real hospice/palliative care conversation
- Show realistic emotional responses (fear, sadness, anger, acceptance, etc.)
- Consider the patient's background, personality, and current emotional state
- Keep responses natural and conversational, not too long
- Show how the patient's emotional state might change based on the doctor's approach
- Use appropriate language for someone in this situation

Remember: This is a training tool for doctors to practice empathetic communication.
Your responses should help doctors learn what works and what doesn't in delivering difficult news.
"""
    
    def generate_response(self, doctor_message: str, scenario: str, patient_profile: Dict) -> Dict:
        """Generate a patient response using OpenAI"""
        prompt = self.create_patient_prompt(scenario, patient_profile)
        
        # Add recent conversation history (limit to last 10 entries)
        recent_history = self.conversation_history[-10:]
        
        # Use mock responses if API key is missing
        if not self.api_key:
            mock_scenario = scenario.lower().replace(" ", "_")
            # Count existing conversation history to determine response
            response_count = len([msg for msg in self.conversation_history if msg.get("role") == "user"])
            mock_response = get_mock_response(mock_scenario, response_count)
            
            self.conversation_history.append({"role": "user", "content": doctor_message})
            self.conversation_history.append({"role": "assistant", "content": mock_response})
            
            return {
                "response": mock_response,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
        
        try:
            model = genai.GenerativeModel(self.model_name)

            # Seed chat with patient prompt and prior history, mapping assistant->model
            history_for_chat = [{
                'role': 'user',
                'parts': prompt
            }]
            for msg in recent_history:
                if msg.get('role') == 'user':
                    history_for_chat.append({'role': 'user', 'parts': msg.get('content', '')})
                elif msg.get('role') == 'assistant':
                    history_for_chat.append({'role': 'model', 'parts': msg.get('content', '')})
            
            chat = model.start_chat(history=history_for_chat)
            response = chat.send_message(doctor_message)
            
            patient_response = response.text
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": doctor_message})
            self.conversation_history.append({"role": "assistant", "content": patient_response})
            
            return {
                "response": patient_response,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            return {
                "response": "I'm sorry, I'm having trouble responding right now.",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_conversation_quality(self, conversation_history: List[Dict]) -> Dict:
        """Analyze the conversation for empathetic communication quality"""
        # This is a simplified analysis - in a real system, this would be more sophisticated
        analysis_prompt = """
        Analyze this doctor-patient conversation for empathetic communication. 
        Rate the doctor's approach on a scale of 1-10 for:
        1. Empathy and emotional support
        2. Clarity of communication
        3. Patient-centered approach
        4. Overall effectiveness
        
        Provide specific feedback on what the doctor did well and what could be improved.
        """
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                f"{analysis_prompt}\n\nCONVERSATION:\n{json.dumps(conversation_history)}"
            )
            analysis = response.text
            
            return {
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            return {
                "analysis": "Unable to analyze conversation at this time.",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_conversation_history(self) -> List[Dict]:
        """Return the current conversation history"""
        return self.conversation_history
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
