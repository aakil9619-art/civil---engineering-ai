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


async def live_voice_session(websocket):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    config = {
        "response_modalities": ["AUDIO"],
        "output_audio_transcription": {},
        "system_instruction": """You are Civil Engineering AI, a friendly exam-focused voice tutor.
Help students prepare for SSC JE, GATE CE and AE/JE.
Give concise spoken explanations. For numericals, state the formula and essential calculation.
If the student asks an ambiguous question, ask a short clarification.
Prefer simple English suitable for an Indian engineering student."""
    }

    async with client.aio.live.connect(model="gemini-3.8-live", config=config) as session:
        async def forward_browser():
            while True:
                message = await websocket.receive_json()
                kind = message.get("type")
                if kind == "text":
                    await session.send_realtime_input(text=message.get("text", ""))
                elif kind == "audio":
                    import base64
                    data = base64.b64decode(message.get("data", ""))
                    await session.send_realtime_input(
                        audio=types.Blob(data=data, mime_type="audio/pcm;rate=16000")
                    )
                elif kind == "audio_end":
                    await session.send_realtime_input(audio_stream_end=True)
                elif kind == "close":
                    break

        async def forward_model():
            async for response in session.receive():
                content = response.server_content
                if not content:
                    continue
                if getattr(content, "interrupted", False):
                    await websocket.send_json({"type": "interrupted"})
                if getattr(content, "input_transcription", None):
                    await websocket.send_json({"type": "user_transcript", "text": content.input_transcription.text})
                if getattr(content, "output_transcription", None):
                    await websocket.send_json({"type": "ai_transcript", "text": content.output_transcription.text})
                turn = getattr(content, "model_turn", None)
                if turn and getattr(turn, "parts", None):
                    for part in turn.parts:
                        inline = getattr(part, "inline_data", None)
                        if inline and inline.data:
                            import base64
                            audio = inline.data
                            if isinstance(audio, str):
                                encoded = audio
                            else:
                                encoded = base64.b64encode(audio).decode("ascii")
                            await websocket.send_json({"type": "audio", "data": encoded})

        import asyncio
        sender = asyncio.create_task(forward_browser())
        receiver = asyncio.create_task(forward_model())
        done, pending = await asyncio.wait({sender, receiver}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
