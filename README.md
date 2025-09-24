# MAYO SYNAPSE '25-'26

Elijah Don, Tanner Hochberg, Alex Roussas, Ian Marcon, Ethan Vanderpool

## Project Overview

Our team is developing innovative solutions to improve healthcare communication and reduce physician burnout, with a focus on empathetic patient interactions during difficult conversations.

## 🏥 Medical Conversation Simulator

**An AI-powered training tool to help medical professionals practice empathetic communication during difficult conversations in hospice and palliative care settings.**

### 🎯 Key Features
- **Realistic AI Patients**: Multiple patient personas with different backgrounds and emotional states
- **Scenario-Based Training**: Terminal diagnosis, treatment options, family discussions, end-of-life care
- **Real-time Feedback**: AI analysis of conversation quality and empathetic communication
- **Progress Tracking**: Conversation history and improvement analytics

### 🚀 Quick Start
```bash
cd conversation_simulator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your OpenAI API key
python run.py
```

Visit `http://localhost:5000` to start training!

### 📁 Project Structure
```
conversation_simulator/
├── app/
│   ├── app.py                 # Main Flask application
│   ├── conversation_engine.py # OpenAI integration
│   └── patient_scenarios.py   # Patient profiles & scenarios
├── templates/                 # HTML templates
├── static/                    # CSS/JS assets
├── run.py                     # Startup script
├── requirements.txt           # Dependencies
└── README.md                  # Detailed documentation
```

## 📋 Problem Statements

### From Our Team:
- **Tanner**: "A way to address a doctors fatigue due to difficult conversations with consecutive patients in order to create more emotionally centered conversation."
- **Elijah**: "A way to provide objective feedback on empathetic communication in palliative care trainees in order to accelerate the development of their conversational skills."
- **Alex**: "A way to facilitate empathetic conversation practice for a medical practitioner to improve their conversational skills."
- **Ian**: "A way to discover a patients uncertain emotional needs in order to reach a deeper patient-doctor emotional understanding."

## 🎓 Learning Objectives

Our solution addresses:
1. **Empathetic Communication**: Training doctors to deliver difficult news with compassion
2. **Emotional Awareness**: Recognizing and responding to patient emotional cues
3. **Burnout Prevention**: Building resilience through better communication skills
4. **Patient-Centered Care**: Understanding diverse patient perspectives and needs
5. **Professional Development**: Continuous learning and improvement in communication

## 🔬 Technical Approach

- **AI-Powered Simulation**: Using OpenAI's GPT models for realistic patient interactions
- **Web-Based Interface**: Flask application for easy access and training
- **Modular Design**: Separate components for scenarios, patients, and analysis
- **Scalable Architecture**: Easy to extend with additional features and scenarios

## 🚀 Future Vision

- **Multimodal Analysis**: Voice and facial expression recognition
- **Advanced Analytics**: Detailed metrics on empathy and communication skills
- **Integration**: EMR system integration for real patient data
- **VR/AR Training**: Immersive training environments
- **Multi-language Support**: Training for diverse patient populations

## 🤝 Collaboration

This project represents a collaborative effort across multiple disciplines to address critical gaps in medical education and patient care communication.

---

*Building better healthcare communication, one conversation at a time.*
