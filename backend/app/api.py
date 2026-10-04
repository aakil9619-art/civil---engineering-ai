from fastapi import APIRouter, UploadFile, File, Header
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
from .auth import verify_bearer, public_config
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
    """Civil-engineering news. Prefer GNews when configured; fall back to Google News RSS."""
    limit = min(max(limit, 1), 10)
    key = os.getenv("GNEWS_API_KEY", "").strip()
    query = "civil engineering infrastructure highway bridge railway dam irrigation construction environment earthquake"
    if key:
        params = urllib.parse.urlencode({"q": query, "lang": "en", "country": "in", "max": limit, "apikey": key})
        try:
            req = urllib.request.Request("https://gnews.io/api/v4/search?" + params, headers={"User-Agent": "CivilEngineeringAI/1.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            articles = [{"title": a.get("title"), "url": a.get("url"), "source": (a.get("source") or {}).get("name"), "publishedAt": a.get("publishedAt")} for a in data.get("articles", [])]
            if articles:
                return {"configured": True, "source": "GNews", "articles": articles}
        except Exception:
            pass
    try:
        rss_query = urllib.parse.quote(query + " India")
        rss_url = "https://news.google.com/rss/search?q=" + rss_query + "&hl=en-IN&gl=IN&ceid=IN:en"
        req = urllib.request.Request(rss_url, headers={"User-Agent": "CivilEngineeringAI/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            raw = response.read()
        import xml.etree.ElementTree as ET
        root = ET.fromstring(raw)
        articles = []
        for item in root.findall("./channel/item")[:limit]:
            title = item.findtext("title") or "Untitled"
            url = item.findtext("link") or ""
            pub = item.findtext("pubDate") or ""
            source = item.findtext("source") or "Google News"
            articles.append({"title": title, "url": url, "source": source, "publishedAt": pub})
        return {"configured": bool(key), "source": "GNews" if key else "Google News RSS", "articles": articles, "fallback": not bool(key)}
    except Exception as exc:
        return {"configured": bool(key), "source": "GNews" if key else "Google News RSS", "articles": [], "error": "News providers temporarily unavailable.", "detail": type(exc).__name__}


@router.get("/global-updates")
def global_updates(limit: int = 8):
    """Global engineering news + recent research + major project updates."""
    limit = min(max(limit, 1), 8)
    result = {"news": [], "research": [], "projects": [], "sources": ["Google News RSS", "OpenAlex"]}
    key = os.getenv("GNEWS_API_KEY", "").strip()
    queries = {
        "news": "engineering invention innovation construction infrastructure technology robotics materials energy water transport",
        "projects": "major infrastructure project megaproject bridge tunnel railway metro airport dam construction project",
    }
    for kind, query in queries.items():
        try:
            if key:
                params = urllib.parse.urlencode({"q": query, "lang": "en", "max": limit, "apikey": key})
                req = urllib.request.Request("https://gnews.io/api/v4/search?" + params, headers={"User-Agent": "CivilEngineeringAI/1.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                result[kind] = [{"title": a.get("title"), "url": a.get("url"), "source": (a.get("source") or {}).get("name"), "publishedAt": a.get("publishedAt")} for a in data.get("articles", [])]
            if not result[kind]:
                rss_query = urllib.parse.quote(query)
                rss_url = "https://news.google.com/rss/search?q=" + rss_query + "&hl=en&gl=US&ceid=US:en"
                req = urllib.request.Request(rss_url, headers={"User-Agent": "CivilEngineeringAI/1.0"})
                with urllib.request.urlopen(req, timeout=12) as response:
                    raw = response.read()
                import xml.etree.ElementTree as ET
                root = ET.fromstring(raw)
                result[kind] = [{"title": item.findtext("title") or "Untitled", "url": item.findtext("link") or "", "source": item.findtext("source") or "Google News", "publishedAt": item.findtext("pubDate") or ""} for item in root.findall("./channel/item")[:limit]]
        except Exception:
            result[kind] = []
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


@router.get("/vacancies")
def vacancies(limit: int = 30):
    """Fresh recruitment/vacancy alerts for Civil Engineering and major JE/AE exams."""
    limit=min(max(limit,5),40)
    import datetime as dt
    from email.utils import parsedate_to_datetime
    queries=[
        '"Junior Engineer" Civil recruitment vacancy India',
        '"Assistant Engineer" Civil recruitment vacancy India',
        '"Civil Engineer" recruitment government India',
        'SSC JE recruitment notification',
        'RRB JE Civil recruitment notification',
        'HPPSC Civil Engineer recruitment',
        'HPRCA JE Civil recruitment',
        'UPSC Engineering Services Civil notification',
        'CPWD Civil Engineer recruitment',
        'NHAI Civil Engineer recruitment',
        'NHPC Civil Engineer recruitment',
        'BRO Civil Engineer recruitment'
    ]
    official_domains={
        "SSC":"ssc.gov.in","UPSC":"upsc.gov.in","HPPSC":"hppsc.hp.gov.in",
        "RRB":"indianrailways.gov.in","HPRCA":"hprca.hp.gov.in"
    }
    seen=set(); items=[]
    today=dt.datetime.now(dt.timezone(dt.timedelta(hours=5,minutes=30))).date()
    import xml.etree.ElementTree as ET
    for query in queries:
        try:
            rss_url="https://news.google.com/rss/search?q="+urllib.parse.quote(query)+"&hl=en-IN&gl=IN&ceid=IN:en"
            req=urllib.request.Request(rss_url,headers={"User-Agent":"CivilEngineeringAI/1.0"})
            with urllib.request.urlopen(req,timeout=8) as response:
                root=ET.fromstring(response.read())
            for item in root.findall("./channel/item")[:8]:
                title=item.findtext("title") or ""
                url=item.findtext("link") or ""
                source=item.findtext("source") or "News"
                pub=item.findtext("pubDate") or ""
                if not title or not url: continue
                key=(title.strip().lower(),url)
                if key in seen: continue
                seen.add(key)
                try: published=parsedate_to_datetime(pub)
                except Exception: published=None
                local_date=published.astimezone(dt.timezone(dt.timedelta(hours=5,minutes=30))).date() if published else None
                text=(title+" "+source).lower()
                if not any(k in text for k in ["recruit","vacan","vacancy","notification","engineer","junior engineer","assistant engineer","apprentice"]): continue
                authority=next((k for k,v in official_domains.items() if v in url or v in source.lower()),None)
                items.append({"title":title,"url":url,"source":source,"publishedAt":pub,"date":str(local_date) if local_date else "","released_today":bool(local_date==today),"authority":authority or "Secondary source"})
        except Exception:
            continue
    items.sort(key=lambda x:(x["released_today"],x["publishedAt"]),reverse=True)
    return {
        "updated_at":dt.datetime.now(dt.timezone.utc).isoformat(),
        "today":str(today),
        "same_day_alerts":[x for x in items if x["released_today"]][:limit],
        "upcoming_or_active":[x for x in items if not x["released_today"]][:limit],
        "official_sources":[
            {"name":"SSC","url":"https://ssc.gov.in/"},
            {"name":"UPSC","url":"https://www.upsc.gov.in/recruitment/recruitment-advertisement"},
            {"name":"HPPSC","url":"https://hppsc.hp.gov.in/"},
            {"name":"Indian Railways / RRB","url":"https://indianrailways.gov.in/"}
        ],
        "note":"Alerts are checked from public feeds. Same-day display depends on when the recruiting authority publishes a public notice/feed."
    }

@router.get("/diagnostics")
def diagnostics():
    """Safe deployment diagnostics; never returns secret values."""
    return {
        "status": "ok",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
        "gnews_configured": bool(os.getenv("GNEWS_API_KEY")),
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "python": __import__("sys").version.split()[0],
    }

from .platform import research_roadmap, project_blueprint
from .knowledge import KNOWLEDGE_MODULES
from .test_catalog import TEST_CATEGORIES, list_tests, get_test

@router.get("/tests/categories")
def test_categories():
    return {"categories": TEST_CATEGORIES, "total_tests": sum(len(list_tests(c)) for c in TEST_CATEGORIES)}

@router.get("/tests")
def tests(category: str = "", test_type: str = ""):
    return {"category": category or "All", "test_type": test_type or "All", "tests": list_tests(category, test_type)}

@router.get("/tests/detail")
def test_detail(category: str, name: str):
    item = get_test(category, name)
    return item if item else {"error": "Test not found", "available_categories": TEST_CATEGORIES}

@router.get("/platform/modules")
def platform_modules():
    return {"modules": KNOWLEDGE_MODULES}

@router.get("/research/roadmap")
def research_path(topic: str, level: str = "B.Tech", budget: str = "Low", duration: str = "4 months"):
    return research_roadmap(topic, level, budget, duration)

@router.get("/projects/blueprint")
def project_path(title: str, level: str = "B.Tech", budget: str = "Low", duration: str = "4 months"):
    return project_blueprint(title, level, budget, duration)

from .workspace import student, update_student, list_workspace, add_project, add_research, add_bookmark, set_progress, add_mock, ensure_student

class StudentRequest(BaseModel):
    student_id: str | None = None
    name: str = ""
    goal: str = ""

class ProjectSaveRequest(BaseModel):
    student_id: str
    title: str
    level: str = "B.Tech"
    status: str = "idea"
    data: dict = Field(default_factory=dict)

class ResearchSaveRequest(BaseModel):
    student_id: str
    topic: str
    status: str = "exploring"
    data: dict = Field(default_factory=dict)

class BookmarkRequest(BaseModel):
    student_id: str
    title: str
    url: str = ""
    kind: str = "resource"

class ProgressRequest(BaseModel):
    student_id: str
    key: str
    value: float
    meta: dict = Field(default_factory=dict)

class MockHistoryRequest(BaseModel):
    student_id: str
    exam: str
    score: float
    accuracy: float
    attempted: int
    total: int

@router.get("/auth/config")
def auth_config():
    return public_config()

@router.get("/auth/me")
def auth_me(authorization: str = Header(default="")):
    user=verify_bearer(authorization)
    uid=user["uid"]
    sid=uid
    ensure_student(sid, user.get("name",""), "", uid)
    return {"uid":uid,"phone":user.get("phone_number",""),"name":user.get("name",""),"student_id":sid}

@router.post("/workspace/student")
def workspace_student(req: StudentRequest, authorization: str = Header(default="")):
    user=verify_bearer(authorization); sid=user["uid"]
    ensure_student(sid, req.name or user.get("name",""), req.goal)
    return student(sid)

@router.get("/workspace")
def workspace(student_id: str):
    return list_workspace(student_id)

@router.post("/workspace/projects")
def workspace_project(req: ProjectSaveRequest, authorization: str = Header(default="")):
    user=verify_bearer(authorization); return add_project(user["uid"], req.title, req.level, req.status, req.data)

@router.post("/workspace/research")
def workspace_research(req: ResearchSaveRequest, authorization: str = Header(default="")):
    user=verify_bearer(authorization); return add_research(user["uid"], req.topic, req.status, req.data)

@router.post("/workspace/bookmarks")
def workspace_bookmark(req: BookmarkRequest, authorization: str = Header(default="")):
    user=verify_bearer(authorization); return add_bookmark(user["uid"], req.title, req.url, req.kind)

@router.post("/workspace/progress")
def workspace_progress(req: ProgressRequest, authorization: str = Header(default="")):
    user=verify_bearer(authorization); return set_progress(user["uid"], req.key, req.value, req.meta)

@router.post("/workspace/mock-history")
def workspace_mock(req: MockHistoryRequest, authorization: str = Header(default="")):
    user=verify_bearer(authorization); return add_mock(user["uid"], req.exam, req.score, req.accuracy, req.attempted, req.total)
