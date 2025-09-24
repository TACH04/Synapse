"""
Main Flask Application for Conversation Simulator
"""

from flask import Flask, render_template, request, jsonify, session
from .conversation_engine import ConversationEngine
from .patient_scenarios import PATIENT_PROFILES, SCENARIOS, get_random_scenario, get_random_patient
import os
import json
from datetime import datetime
app = Flask(__name__, template_folder="../templates")

app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize conversation engine
conversation_engine = ConversationEngine()

@app.route('/')
def index():
    """Main page - select scenario and patient"""
    return render_template('index.html', 
                         scenarios=SCENARIOS, 
                         patients=PATIENT_PROFILES)

@app.route('/scenario/<scenario_key>')
def scenario(scenario_key):
    """Scenario page - start a specific scenario"""
    scenario = SCENARIOS.get(scenario_key)
    if not scenario:
        return "Scenario not found", 404
    
    # Get random patient for this scenario
    patient = get_random_patient()
    
    # Store in session
    session['current_scenario'] = scenario
    session['current_patient'] = patient
    session['conversation_history'] = []
    
    return render_template('scenario.html', 
                         scenario=scenario, 
                         patient=patient)

@app.route('/random_scenario')
def random_scenario():
    """Start a random scenario with random patient"""
    scenario = get_random_scenario()
    patient = get_random_patient()
    
    # Store in session
    session['current_scenario'] = scenario
    session['current_patient'] = patient
    session['conversation_history'] = []
    
    return render_template('scenario.html', 
                         scenario=scenario, 
                         patient=patient)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    doctor_message = data.get('message', '')
    scenario_key = data.get('scenario')
    patient_key = data.get('patient')
    
    if not doctor_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get scenario and patient from session or parameters
    scenario = session.get('current_scenario', SCENARIOS.get(scenario_key))
    patient = session.get('current_patient', PATIENT_PROFILES.get(patient_key))
    
    if not scenario or not patient:
        return jsonify({'error': 'No scenario or patient selected'}), 400
    
    # Generate patient response
    scenario_key_val = next(key for key, value in SCENARIOS.items() if value == scenario)
    response = conversation_engine.generate_response(doctor_message, scenario_key_val, patient, scenario)
    
    # Update session conversation history
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    
    session['conversation_history'].append({
        'doctor': doctor_message,
        'patient': response['response'],
        'timestamp': response['timestamp'],
        'emotion': response.get('emotion')
    })
    
    return jsonify(response)

@app.route('/analyze', methods=['POST'])
def analyze_conversation():
    """Analyze the conversation for feedback"""
    conversation_history = session.get('conversation_history', [])
    
    if not conversation_history:
        return jsonify({'error': 'No conversation to analyze'}), 400
    
    analysis = conversation_engine.analyze_conversation_quality(conversation_history)
    
    return jsonify(analysis)

@app.route('/reset')
def reset_conversation():
    """Reset the current conversation"""
    session.pop('conversation_history', None)
    conversation_engine.reset_conversation()
    return jsonify({'success': True})

@app.route('/history')
def conversation_history():
    """View conversation history"""
    history = session.get('conversation_history', [])
    return render_template('history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
