def generate_quiz(topic):
    return [{
        "question": f"What is {topic}?",
        "options": ["Definition", "Law", "Formula", "Theory"],
        "answer": "Definition",
        "difficulty": "Easy"
    }]
