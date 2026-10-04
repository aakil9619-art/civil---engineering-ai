from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel, Field
from .subjects import SUBJECTS
from .question_engine import build_blueprint
from .question_generator import generate_questions
from .tutor import tutor_prompt
from .topic_bank import SUBJECT_TOPICS
from .mock_config import get_mock_config
from .performance import performance_profile
from .diagram_engine import diagram_blueprint
from .llm import llm_status, build_civil_prompt, generate_tutor_answer, generate_tutor_image_answer
from .mock_engine import calculate_result
from .mixed_mock import build_mixed_mock
import os, json, urllib.parse, urllib.request

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
        return {"error": "The AI service could not answer right now. Check your Gemini API key and try again.", "mode": "provider_error"}

@router.post("/chat/image")
async def chat_image(subject: str, topic: str = "", question: str = "", image: UploadFile = File(...)):
    if subject not in SUBJECTS:
        return {"error": "Unknown subject", "subjects": SUBJECTS}
    if not image.content_type or not image.content_type.startswith("image/"):
        return {"error": "Please upload an image file."}
    data = await image.read()
    if len(data) > 10 * 1024 * 1024:
        return {"error": "Image is too large. Please use an image under 10 MB."}
    try:
        answer = generate_tutor_image_answer(subject, topic, question, data, image.content_type)
        return {"answer": answer, "mode": "gemini-vision", "provider": "gemini"}
    except RuntimeError as exc:
        return {"error": str(exc), "mode": "configuration_error"}
    except Exception:
        return {"error": "The AI service could not analyze this image right now.", "mode": "provider_error"}

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
    return {"exam": c.exam, "total_questions": c.total_questions, "duration_minutes": c.duration_minutes, "sections": c.sections, "negative_marking": c.negative_marking}

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

@router.get("/mock/questions")
def mixed_mock_questions(exam: str = "SSC JE 2026", technical: int = 100, reasoning: int = 50, gk: int = 50):
    if exam != "SSC JE 2026":
        return {"error": "This mixed simulator currently supports SSC JE 2026 Paper-I."}
    if technical < 1 or reasoning < 1 or gk < 1 or technical > 100 or reasoning > 50 or gk > 50:
        return {"error": "Use Technical 1-100, Reasoning 1-50 and GK 1-50."}
    questions = build_mixed_mock(technical, reasoning, gk)
    return {"exam": exam, "questions": questions, "negative_marking": 0.25, "duration_minutes": 120}

@router.get("/news")
def news(limit: int = 12):
    """Civil-engineering news feed. Uses GNews when GNEWS_API_KEY is configured."""
    key = os.getenv("GNEWS_API_KEY", "").strip()
    if not key:
        return {"configured": False, "source": "GNews", "articles": [], "message": "Add GNEWS_API_KEY in Render Environment Variables."}
    query = "civil engineering OR infrastructure OR highway OR bridge OR railway OR dam OR irrigation OR construction OR environment OR earthquake"
    params = urllib.parse.urlencode({"q": query, "lang": "en", "country": "in", "max": min(max(limit, 1), 10), "apikey": key})
    try:
        req = urllib.request.Request("https://gnews.io/api/v4/search?" + params, headers={"User-Agent": "CivilEngineeringAI/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        articles = [{"title": a.get("title"), "url": a.get("url"), "source": (a.get("source") or {}).get("name"), "publishedAt": a.get("publishedAt")} for a in data.get("articles", [])]
        return {"configured": True, "source": "GNews", "articles": articles}
    except Exception:
        return {"configured": True, "source": "GNews", "articles": [], "error": "News feed temporarily unavailable."}

@router.get("/global-updates")
def global_updates(limit: int = 8):
    """Global engineering news + recent research + major project updates."""
    limit = min(max(limit, 1), 8)
    result = {"news": [], "research": [], "projects": [], "sources": ["GNews", "OpenAlex"]}
    key = os.getenv("GNEWS_API_KEY", "").strip()
    queries = {
        "news": "engineering invention innovation construction infrastructure technology robotics materials energy water transport",
        "projects": "major infrastructure project megaproject bridge tunnel railway metro airport dam construction project",
    }
    if key:
        for kind, query in queries.items():
            try:
                params = urllib.parse.urlencode({"q": query, "lang": "en", "max": limit, "apikey": key})
                req = urllib.request.Request("https://gnews.io/api/v4/search?" + params, headers={"User-Agent": "CivilEngineeringAI/1.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                result[kind] = [{"title": a.get("title"), "url": a.get("url"), "source": (a.get("source") or {}).get("name"), "publishedAt": a.get("publishedAt")} for a in data.get("articles", [])]
            except Exception:
                result[kind] = []
    else:
        result["news_message"] = "Add GNEWS_API_KEY in Render for live global news and project headlines."
    try:
        search = urllib.parse.quote("civil engineering OR construction OR infrastructure OR structural engineering OR low carbon concrete OR construction robotics OR digital twin")
        url = f"https://api.openalex.org/works?search={search}&filter=from_publication_date:2026-01-01&sort=publication_date:desc&per-page={limit}&select=id,title,doi,publication_date,primary_location,authorships"
        req = urllib.request.Request(url, headers={"User-Agent": "CivilEngineeringAI/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
        for w in data.get("results", []):
            loc = w.get("primary_location") or {}
            source = (loc.get("source") or {}).get("display_name") if isinstance(loc.get("source"), dict) else None
            result["research"].append({"title": w.get("title"), "url": w.get("doi") or w.get("id"), "source": source or "OpenAlex", "publishedAt": w.get("publication_date")})
    except Exception:
        result["research_message"] = "Research feed temporarily unavailable."
    return result

from .platform import research_roadmap, project_blueprint
from .knowledge import KNOWLEDGE_MODULES

@router.get("/platform/modules")
def platform_modules():
    return {"modules": KNOWLEDGE_MODULES}

@router.get("/research/roadmap")
def research_path(topic: str, level: str = "B.Tech", budget: str = "Low", duration: str = "4 months"):
    return research_roadmap(topic, level, budget, duration)

@router.get("/projects/blueprint")
def project_path(title: str, level: str = "B.Tech", budget: str = "Low", duration: str = "4 months"):
    return project_blueprint(title, level, budget, duration)
