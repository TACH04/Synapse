"""
Conversation Engine for AI Patient Simulation
Handles communication with Google Gemini API to simulate patient responses
"""

import os
import json
from typing import Dict, List, Optional
import google.generativeai as genai
from datetime import datetime
from .mock_responses import get_mock_response
from .patient_scenarios import SCENARIOS

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

    def _is_greeting(self, text: str) -> bool:
        """Detect if the clinician's message is a greeting/check-in opening."""
        if not text:
            return False
        lower = text.strip().lower()
        greeting_phrases = [
            "how are you", "how are you doing", "how's it going", "hows it going",
            "how have you been", "how are we", "how are we doing",
            "hi ", "hi,", "hello", "good morning", "good afternoon", "good evening"
        ]
        return any(phrase in lower for phrase in greeting_phrases) or lower in {"hi", "hello"}

    def _generate_initial_patient_reply(self, patient_profile: Dict, awareness: str) -> str:
        """Generate a brief, realistic initial reply that does not pre-empt prognosis."""
        name = patient_profile.get("name", "Patient")
        personality = (patient_profile.get("personality") or "").lower()
        emotional_state = (patient_profile.get("emotional_state") or "").lower()

        # Base replies tuned to feel natural and conventional
        if "stoic" in personality:
            base = "I'm okay. Managing as best I can."
        elif "optimistic" in personality:
            base = "I'm doing alright today. Trying to stay positive."
        elif "warm" in personality:
            base = "I'm okay, thank you for asking. A bit tired, but hanging in there."
        else:
            base = "I'm okay. A little tired lately."

        # Light flavor from emotional state without disclosing specifics
        if "anxious" in emotional_state:
            tail = "Just a little worried about everything."
        elif "frustrated" in emotional_state:
            tail = "Some days are tougher than others."
        elif "angry" in emotional_state:
            tail = "It's been a lot to take in."
        else:
            tail = None

        reply = base if not tail else f"{base} {tail}"

        # Awareness should never introduce terminal or prognosis unprompted
        # Keep to 1–2 short sentences
        return reply

    def create_patient_prompt(self, scenario_key: str, patient_profile: Dict, scenario_data: Optional[Dict] = None) -> str:
        """Create a detailed prompt for the AI patient including knowledge boundaries."""
        details = scenario_data or SCENARIOS.get(scenario_key, {})
        title = details.get("title", scenario_key)
        description = details.get("description", "")
        initial_context = details.get("initial_context", "")
        learning_objectives = details.get("learning_objectives", [])
        awareness = details.get("patient_awareness", "unknown")
        learning_str = "\n- ".join(learning_objectives) if learning_objectives else ""

        return f"""
You are simulating a hospice/palliative care patient in a difficult conversation with their doctor.
Your role is to respond naturally and emotionally as this patient would.

PATIENT PROFILE:
- Name: {patient_profile.get('name', 'Patient')}
- Age: {patient_profile.get('age', 65)}
- Condition: {patient_profile.get('condition', 'Serious illness')}
- Personality: {patient_profile.get('personality', 'Reserved and thoughtful')}
- Emotional State: {patient_profile.get('emotional_state', 'Anxious and fearful')}
- Background: {patient_profile.get('background', 'Family-oriented with adult children')}

SCENARIO:
- Key: {scenario_key}
- Title: {title}
- Description: {description}
- Initial Context: {initial_context}
- Learning Objectives:
- {learning_str}

PATIENT KNOWLEDGE BOUNDARIES:
- Awareness level: {awareness}
- Do NOT assume or disclose terminal status, prognosis, or specific medical details unless the clinician clearly introduces them.
- If the clinician opens with a greeting or general check-in, keep your first reply very brief (1–2 short sentences), conventional, and do not steer into prognosis or end-of-life topics.
- Align your knowledge strictly with what has been stated so far in the conversation.

INSTRUCTIONS:
- Respond as this specific patient would in a real hospice/palliative care conversation.
- Show realistic emotional responses (fear, sadness, anger, acceptance, etc.) consistent with the profile.
- Consider the patient's background, personality, and current emotional state.
- Keep responses natural and conversational; usually 1–4 sentences.
- Let the clinician set the pace; do not jump ahead to conclusions.
- Reflect changes in emotional state based on the clinician's approach.

Remember: This is a training tool for doctors to practice empathetic communication. Your responses should help doctors learn effective, compassionate approaches.
"""
    
    def generate_response(self, doctor_message: str, scenario_key: str, patient_profile: Dict, scenario_data: Optional[Dict] = None) -> Dict:
        """Generate a patient response using Gemini or mock responses, with realistic openings."""
        details = scenario_data or SCENARIOS.get(scenario_key, {})
        prompt = self.create_patient_prompt(scenario_key, patient_profile, details)
        
        # Add recent conversation history (limit to last 10 entries)
        recent_history = self.conversation_history[-10:]

        # If this is the very first clinician message and it's a greeting, craft a brief initial reply
        prior_user_count = len([msg for msg in self.conversation_history if msg.get("role") == "user"])
        if prior_user_count == 0 and self._is_greeting(doctor_message):
            initial_reply = self._generate_initial_patient_reply(patient_profile, details.get("patient_awareness", "unknown"))
            self.conversation_history.append({"role": "user", "content": doctor_message})
            self.conversation_history.append({"role": "assistant", "content": initial_reply})
            return {
                "response": initial_reply,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
        
        # Use mock responses if API key is missing
        if not self.api_key:
            mock_scenario = scenario_key
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
