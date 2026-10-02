from fastapi import APIRouter
from pydantic import BaseModel, Field
from .subjects import SUBJECTS
from .question_engine import build_blueprint
from .question_generator import generate_questions
from .tutor import tutor_prompt
from .topic_bank import SUBJECT_TOPICS
from .mock_config import get_mock_config
from .performance import performance_profile
from .diagram_engine import diagram_blueprint
from .llm import llm_status, build_civil_prompt, generate_tutor_answer
from .mock_engine import calculate_result

router = APIRouter(prefix="/api")

class TutorRequest(BaseModel):
    subject: str
    topic: str = ""
    question: str

class QuestionRequest(BaseModel):
    exam: str = "SSC JE"
    subject: str
    topic: str = ""
    difficulty: str = "moderate"
    question_type: str = "numerical"
    count: int = Field(default=5, ge=1, le=50)

class MockAnswer(BaseModel):
    is_correct: bool
    time_seconds: float = 0
    topic: str = ""
    selected_option: str = ""
    marked_for_review: bool = False

class MockRequest(BaseModel):
    total: int
    answers: list[MockAnswer]

@router.post("/tutor")
def tutor(req: TutorRequest):
    if req.subject not in SUBJECTS:
        return {"error": "Unknown subject", "subjects": SUBJECTS}
    return {"prompt": tutor_prompt(req.subject, req.topic, req.question)}

@router.post("/chat")
def chat(req: TutorRequest):
    if req.subject not in SUBJECTS:
        return {"error": "Unknown subject", "subjects": SUBJECTS}
    if not req.question.strip():
        return {"error": "Please enter a question."}
    try:
        answer = generate_tutor_answer(req.subject, req.topic, req.question)
        return {"answer": answer, "mode": "gemini", "provider": "gemini"}
    except RuntimeError as exc:
        return {"error": str(exc), "mode": "configuration_error"}
    except Exception:
        return {
            "error": "The AI service could not answer right now. Check your Gemini API key and try again.",
            "mode": "provider_error",
        }

@router.post("/questions/generate")
def generate(req: QuestionRequest):
    if req.subject not in SUBJECTS:
        return {"error": "Unknown subject", "subjects": SUBJECTS}
    return {"questions": generate_questions(req.exam, req.subject, req.topic, req.difficulty, req.question_type, req.count)}

@router.post("/questions/blueprint")
def question_blueprint(req: QuestionRequest):
    if req.subject not in SUBJECTS:
        return {"error": "Unknown subject", "subjects": SUBJECTS}
    return build_blueprint(req.exam, req.subject, req.topic, req.difficulty, req.question_type)

@router.post("/mock/result")
def mock_result(req: MockRequest):
    result = calculate_result(req.total, [a.model_dump() for a in req.answers])
    return result.__dict__

@router.get("/topics")
def topics(subject: str = ""):
    return {"subject": subject, "topics": SUBJECT_TOPICS.get(subject, [])} if subject else {"subjects": SUBJECT_TOPICS}

@router.get("/mock/config")
def mock_config(exam: str = "SSC JE 2026"):
    c = get_mock_config(exam)
    return {"exam": c.exam, "total_questions": c.total_questions, "duration_minutes": c.duration_minutes, "sections": c.sections}

@router.post("/performance")
def performance(req: MockRequest):
    answers = [a.model_dump() for a in req.answers]
    return {"profile": performance_profile(answers), "summary": calculate_result(req.total, answers).__dict__}

@router.get("/diagram")
def diagram(subject: str, topic: str):
    return diagram_blueprint(subject, topic)

@router.get("/ai/status")
def ai_status():
    return llm_status()

@router.get("/ai/prompt")
def ai_prompt(exam: str, subject: str, topic: str, difficulty: str="moderate", question_type: str="numerical"):
    return {"prompt": build_civil_prompt(exam, subject, topic, difficulty, question_type)}
