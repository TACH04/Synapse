#!/usr/bin/env python3
"""
Test script to verify Google Gemini responses are working
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    print(f"🔑 API Key loaded: {api_key[:15]}..." if api_key else 'No API key found')
    
    if not api_key or api_key == "your-google-gemini-api-key-here":
        print("⚠️  Still using placeholder API key")
        print("   Please update your .env file with a real Google Gemini API key")
        return
    
    print("✅ Real Google Gemini API key detected!")
    print("🧪 Testing Gemini responses...")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Create model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Test scenarios
    test_scenarios = [
        {
            "scenario": "terminal_diagnosis",
            "patient": {"name": "Margaret", "condition": "terminal cancer"},
            "message": "Hello Margaret, I wanted to talk about your recent test results."
        },
        {
            "scenario": "treatment_options", 
            "patient": {"name": "Robert", "condition": "heart failure"},
            "message": "Robert, let's discuss your treatment options."
        }
    ]
    
    for test in test_scenarios:
        print(f"\n📋 Testing scenario: {test['scenario']}")
        print(f"👥 Patient: {test['patient']['name']} - {test['patient']['condition']}")
        print(f"💬 Doctor: {test['message']}")
        
        try:
            # Create a patient context prompt
            patient_prompt = f"""You are simulating a {test['scenario'].replace('_', ' ')} patient in a difficult conversation with their doctor. 
Your role is to respond naturally and emotionally as this patient would.

PATIENT PROFILE:
- Name: {test['patient']['name']}
- Condition: {test['patient']['condition']}
- Personality: Realistic and emotional

Respond as this patient would in a real medical conversation. Keep responses natural and conversational."""
            
            response = model.generate_content(f"{patient_prompt}\n\nDoctor: {test['message']}\nPatient:")
            
            print(f"🤖 Patient Response: {response.text}")
            print("✅ Success: Gemini response generated!")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n🎉 Gemini test completed!")
    print("💡 If you see realistic patient responses above, your Gemini integration is working!")

if __name__ == '__main__':
    test_gemini()
