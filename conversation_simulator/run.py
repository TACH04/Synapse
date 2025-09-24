#!/usr/bin/env python3
"""
Startup script for the Medical Conversation Simulator
"""

import os
import sys
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for Google Gemini API key
    if not os.getenv('GOOGLE_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: GOOGLE_API_KEY not found in environment variables")
        print("Please set your Google Gemini API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        print("Or create a .env file with GOOGLE_API_KEY=your-api-key-here")
        print("\nYou can get an API key from: https://makersuite.google.com/app/apikey")
        print("\nFor testing purposes, without an API key the app will use mock responses.\n")
    
    # Start the Flask application
    from app.app import app
    print("🚀 Starting Medical Conversation Simulator...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
