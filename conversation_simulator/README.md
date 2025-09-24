# Medical Conversation Simulator

An AI-powered training tool to help medical professionals practice empathetic communication during difficult conversations, particularly in hospice and palliative care settings.

## 🎯 Purpose

This tool helps doctors, nurses, and other healthcare providers:
- Practice delivering difficult news with empathy
- Learn to recognize and respond to emotional cues
- Improve patient-centered communication
- Reduce emotional burnout through better conversation skills

## 🚀 Features

- **Realistic AI Patients**: Multiple patient personas with different backgrounds, personalities, and emotional states
- **Scenario-Based Training**: Various medical scenarios including terminal diagnosis, treatment options, family discussions, and end-of-life care
- **Real-time AI Responses**: Powered by Google Gemini for natural, context-aware conversations
- **Conversation Analysis**: AI-powered feedback on empathetic communication skills
- **Session Management**: Persistent conversation history and user state
- **Web Interface**: Clean, responsive interface accessible from any device

## 📋 Scenarios Available

1. **Terminal Diagnosis**: Delivering news about terminal illness
2. **Treatment Options**: Discussing limited treatment choices
3. **Family Meetings**: Managing discussions with patients and families
4. **End-of-Life Care**: Planning final care preferences

## 👥 Patient Profiles

- **Margaret Thompson**: 78-year-old woman with advanced lung cancer
- **Robert Chen**: 52-year-old man with ALS
- **Sarah Johnson**: 28-year-old woman with metastatic breast cancer
- **James Mitchell**: 65-year-old veteran with end-stage heart failure

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (get one at [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone and setup the project**:
   ```bash
   cd conversation_simulator
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   Create a `.env` file in `conversation_simulator/` with:
   ```bash
   GOOGLE_API_KEY=your-google-gemini-api-key-here
   SECRET_KEY=dev-secret-key-change-in-production
   # Optional
   GEMINI_MODEL=gemini-1.5-flash
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Open your browser**:
   Navigate to `http://localhost:5000`

## 🔑 Getting a Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API key"
4. Copy the key (starts with `AIza`)

## 💡 Usage

1. **Select a scenario** from the home page or choose "Random Scenario"
2. **Review the patient profile** and learning objectives
3. **Start the conversation** by typing messages to the AI patient
4. **Use the analysis tools** to get feedback on your communication
5. **Review your history** to track improvement over time

## 🎓 Training Tips

- **Listen actively** before responding
- **Acknowledge emotions** explicitly ("I can see this is difficult for you")
- **Ask open-ended questions** to understand patient concerns
- **Balance honesty with hope** when appropriate
- **Check understanding** regularly ("Does that make sense to you?")
- **Offer support** for both patient and family

## 🔧 Configuration

Edit the `.env` file to customize:
- `GOOGLE_API_KEY`: Your Google Gemini API key (required)
- `SECRET_KEY`: Flask secret key for sessions
- `GEMINI_MODEL`: AI model to use (default: gemini-1.5-flash)

## 🏗️ Architecture

- **Flask Web Framework**: Handles the web interface and API
- **Google Gemini AI**: Powers realistic patient responses
- **Session Management**: Maintains conversation state
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🚀 Future Enhancements

- **Advanced Analytics**: Detailed metrics on empathy and communication skills
- **Multi-language Support**: Training for diverse patient populations
- **Integration**: EMR system integration for real patient data
- **VR/AR Interface**: Immersive training environments
- **Voice Integration**: Speech-to-text and text-to-speech capabilities

## 🤝 Contributing

This project is part of the MAYO SYNAPSE '25-'26 program. Contributions welcome!

## 📄 License

This project is for educational and training purposes in healthcare communication.

## ⚠️ Important Notes

- This is a **training tool**, not a substitute for professional medical training
- AI responses are simulated and should not be used for actual patient care
- Always consult with qualified medical educators and follow institutional protocols
- Patient privacy and confidentiality must be maintained in real clinical settings

---

*Building better healthcare communication, one conversation at a time.*
