"""
Mock responses for testing without OpenAI API key
"""

MOCK_RESPONSES = {
    "terminal_diagnosis": [
        "I'm scared, doctor. What does this mean for me?",
        "How long do I have? I need to tell my family.",
        "What are my options? Is there anything we can do?",
        "I don't want to be a burden on my family.",
        "Thank you for being honest with me."
    ],
    "treatment_options": [
        "What are the side effects of these treatments?",
        "How will this affect my quality of life?",
        "I'd rather focus on comfort than fighting the disease.",
        "What would you recommend if I were your family member?",
        "I need time to think about this decision."
    ],
    "family_discussion": [
        "I want my family to understand my wishes.",
        "Please help me explain this to my children.",
        "I'm worried about how they'll cope without me.",
        "What should I tell them about what's coming?",
        "Thank you for including everyone in this conversation."
    ],
    "end_of_life_care": [
        "I want to die at home if possible.",
        "Please make sure I'm comfortable at the end.",
        "I don't want any heroic measures.",
        "My faith is important to me during this time.",
        "Thank you for respecting my choices."
    ]
}

def get_mock_response(scenario_key: str, message_count: int) -> str:
    """Get a mock patient response based on scenario"""
    responses = MOCK_RESPONSES.get(scenario_key, ["I'm not sure how to respond to that."])
    return responses[message_count % len(responses)]
