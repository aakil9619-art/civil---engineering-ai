import os

def llm_status():
    return {"provider_configured": bool(os.getenv("LLM_API_KEY")), "provider": os.getenv("LLM_PROVIDER","not-configured")}

def build_civil_prompt(exam, subject, topic, difficulty, question_type):
    return f"""Create an original {exam} Civil Engineering question.
Subject: {subject}; Topic: {topic}; Difficulty: {difficulty}; Type: {question_type}.
Return: question, four options, answer, rigorous solution, formula, concept, common trap and exam tip.
Never copy a known question verbatim."""
