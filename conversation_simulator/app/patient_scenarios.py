"""
Patient Scenarios and Profiles for the Conversation Simulator
"""

PATIENT_PROFILES = {
    "elderly_woman": {
        "name": "Margaret Thompson",
        "age": 78,
        "condition": "Advanced lung cancer with metastasis",
        "personality": "Warm but anxious, values family deeply",
        "emotional_state": "Fearful about burdening her family, seeking reassurance",
        "background": "Widowed, three adult children, former teacher, active in community"
    },
    "middle_aged_man": {
        "name": "Robert Chen",
        "age": 52,
        "condition": "ALS (Amyotrophic Lateral Sclerosis)",
        "personality": "Stoic and practical, focuses on facts over emotions",
        "emotional_state": "Frustrated with loss of independence, concerned about family finances",
        "background": "Married with two teenage children, engineer, enjoys outdoor activities"
    },
    "young_adult": {
        "name": "Sarah Johnson",
        "age": 28,
        "condition": "Metastatic breast cancer",
        "personality": "Optimistic and determined, questions everything",
        "emotional_state": "Angry about the unfairness, worried about future plans",
        "background": "Recently engaged, career-focused marketing professional, very close to parents"
    },
    "veteran": {
        "name": "James Mitchell",
        "age": 65,
        "condition": "End-stage heart failure",
        "personality": "Direct and no-nonsense, appreciates honesty",
        "emotional_state": "Accepting of mortality, concerned about leaving family unprepared",
        "background": "Retired military, married 40+ years, has grandchildren, enjoys fishing"
    }
}

SCENARIOS = {
    "terminal_diagnosis": {
        "title": "Delivering Terminal Diagnosis",
        "description": "The patient needs to be informed that their condition is terminal and treatment options are limited",
        "initial_context": "The patient has been experiencing worsening symptoms and recent tests show the disease has progressed significantly. This is the first time you're discussing the terminal nature of their illness.",
        "learning_objectives": [
            "Balance honesty with hope",
            "Assess patient's understanding and readiness",
            "Address emotional responses appropriately",
            "Discuss goals of care and quality of life"
        ]
    },
    "treatment_options": {
        "title": "Discussing Treatment Options",
        "description": "Presenting limited treatment options for advanced disease",
        "initial_context": "The patient has been undergoing treatment but it's no longer effective. You need to discuss transitioning to palliative care.",
        "learning_objectives": [
            "Present options clearly without overwhelming",
            "Help patient weigh quality vs. quantity of life",
            "Address fears about stopping treatment",
            "Introduce palliative care positively"
        ]
    },
    "family_discussion": {
        "title": "Family Meeting About Prognosis",
        "description": "Discussing prognosis and care decisions with patient and family",
        "initial_context": "The patient has decided they want their family involved in discussions about their care and prognosis.",
        "learning_objectives": [
            "Facilitate open communication between family members",
            "Ensure patient voice is heard",
            "Manage family conflicts or differing opinions",
            "Help family prepare emotionally and practically"
        ]
    },
    "end_of_life_care": {
        "title": "Planning End-of-Life Care",
        "description": "Discussing specific end-of-life care preferences and decisions",
        "initial_context": "The patient is ready to discuss specific details about their final wishes and end-of-life care preferences.",
        "learning_objectives": [
            "Discuss death and dying openly and comfortably",
            "Explore patient's fears and hopes",
            "Document care preferences clearly",
            "Provide emotional support during difficult decisions"
        ]
    }
}

def get_random_scenario():
    """Get a random scenario for training variety"""
    import random
    return random.choice(list(SCENARIOS.values()))

def get_random_patient():
    """Get a random patient profile for training variety"""
    import random
    return random.choice(list(PATIENT_PROFILES.values()))

def get_scenario_by_key(key: str):
    """Get a specific scenario by key"""
    return SCENARIOS.get(key)

def get_patient_by_key(key: str):
    """Get a specific patient profile by key"""
    return PATIENT_PROFILES.get(key)
