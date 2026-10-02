from fastapi import APIRouter
from pydantic import BaseModel, Field
from .subjects import SUBJECTS
from .question_engine import build_blueprint
from .question_generator import generate_questions
from .tutor import tutor_prompt
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

class MockRequest(BaseModel):
    total: int
    answers: list[MockAnswer]

@router.post("/tutor")
def tutor(req: TutorRequest):
    if req.subject not in SUBJECTS:
        return {"error": "Unknown subject", "subjects": SUBJECTS}
    return {"prompt": tutor_prompt(req.subject, req.topic, req.question)}

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
