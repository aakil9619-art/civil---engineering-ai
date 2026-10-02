import os

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def llm_status():
    configured = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    return {
        "provider_configured": configured,
        "provider": "gemini" if configured else "not-configured",
        "model": MODEL,
    }


def build_civil_prompt(exam, subject, topic, difficulty, question_type):
    return f"""Create an original {exam} Civil Engineering question.
Subject: {subject}; Topic: {topic}; Difficulty: {difficulty}; Type: {question_type}.
Return: question, four options, answer, rigorous solution, formula, concept, common trap and exam tip.
Never copy a known question verbatim."""


def build_tutor_prompt(subject: str, topic: str, user_question: str) -> str:
    return f"""You are Civil Engineering AI, an exam-focused tutor for SSC JE, GATE CE and AE/JE exams.

Student subject: {subject}
Student topic: {topic or "Not specified"}

Student question:
{user_question}

Answer briefly and practically. Use this structure:
1. Direct answer
2. Concept/formula
3. How to solve or approach it
4. Common exam trap
5. One quick exam tip

For numerical questions, show the essential calculation steps and units.
For conceptual questions, explain the key distinction in simple language.
Do not invent standards, numerical data, or citations. If the question is ambiguous, state the assumption.
Keep the answer focused on exam preparation."""


def generate_tutor_answer(subject: str, topic: str, user_question: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    from google import genai

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=build_tutor_prompt(subject, topic, user_question),
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text.strip()


def generate_tutor_image_answer(subject: str, topic: str, user_question: str, image_bytes: bytes, mime_type: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    import base64
    from google import genai

    client = genai.Client(api_key=api_key)
    prompt = build_tutor_prompt(subject, topic, user_question) + """

A question image is attached. Read all visible text, equations, tables and Civil Engineering diagrams.
Solve the exact question shown. If it is multiple-choice:
- identify the correct option;
- briefly explain why it is correct;
- briefly identify the key reason the other options are wrong when possible.
Do not guess unreadable values. State what is unclear and make only clearly stated assumptions.
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            prompt,
            {"inline_data": {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode("utf-8")}},
        ],
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text.strip()
