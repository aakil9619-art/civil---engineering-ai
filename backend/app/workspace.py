import sqlite3
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

DATA_DIR = Path(os.getenv("CIVIL_AI_DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "workspace.db"

def _now():
    return datetime.now(timezone.utc).isoformat()

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT DEFAULT '',
            goal TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            title TEXT NOT NULL,
            level TEXT DEFAULT 'B.Tech',
            status TEXT DEFAULT 'idea',
            data TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS research (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            status TEXT DEFAULT 'exploring',
            data TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS bookmarks (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT DEFAULT '',
            kind TEXT DEFAULT 'resource',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS progress (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value REAL DEFAULT 0,
            meta TEXT DEFAULT '{}',
            updated_at TEXT NOT NULL,
            UNIQUE(student_id, key)
        );
        CREATE TABLE IF NOT EXISTS mock_history (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            exam TEXT NOT NULL,
            score REAL DEFAULT 0,
            accuracy REAL DEFAULT 0,
            attempted INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );
        """)

def ensure_student(student_id=None, name="", goal=""):
    init_db()
    sid = student_id or str(uuid4())
    now = _now()
    with _conn() as c:
        row = c.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
        if row:
            if name or goal:
                c.execute("UPDATE students SET name=COALESCE(NULLIF(?, ''), name), goal=COALESCE(NULLIF(?, ''), goal), updated_at=? WHERE id=?", (name, goal, now, sid))
        else:
            c.execute("INSERT INTO students VALUES (?,?,?,?,?)", (sid, name, goal, now, now))
    return sid

def student(student_id):
    sid = ensure_student(student_id)
    with _conn() as c:
        r = c.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
    return dict(r)

def update_student(student_id, name="", goal=""):
    sid = ensure_student(student_id)
    with _conn() as c:
        c.execute("UPDATE students SET name=?, goal=?, updated_at=? WHERE id=?", (name, goal, _now(), sid))
    return student(sid)

def _rows(table, sid):
    with _conn() as c:
        return [dict(r) for r in c.execute(f"SELECT * FROM {table} WHERE student_id=? ORDER BY created_at DESC", (sid,)).fetchall()]

def list_workspace(sid):
    sid = ensure_student(sid)
    return {
        "student": student(sid),
        "projects": _rows("projects", sid),
        "research": _rows("research", sid),
        "bookmarks": _rows("bookmarks", sid),
        "progress": _rows("progress", sid),
        "mock_history": _rows("mock_history", sid),
    }

def add_project(sid, title, level="B.Tech", status="idea", data=None):
    sid=ensure_student(sid); pid=str(uuid4()); now=_now()
    with _conn() as c:
        c.execute("INSERT INTO projects VALUES (?,?,?,?,?,?,?)", (pid,sid,title,level,status,json.dumps(data or {}),now,now))
    return {"id":pid,"student_id":sid,"title":title,"level":level,"status":status,"data":data or {},"created_at":now,"updated_at":now}

def add_research(sid, topic, status="exploring", data=None):
    sid=ensure_student(sid); rid=str(uuid4()); now=_now()
    with _conn() as c:
        c.execute("INSERT INTO research VALUES (?,?,?,?,?,?,?)", (rid,sid,topic,status,json.dumps(data or {}),now,now))
    return {"id":rid,"student_id":sid,"topic":topic,"status":status,"data":data or {},"created_at":now,"updated_at":now}

def add_bookmark(sid, title, url="", kind="resource"):
    sid=ensure_student(sid); bid=str(uuid4()); now=_now()
    with _conn() as c:
        c.execute("INSERT INTO bookmarks VALUES (?,?,?,?,?,?)", (bid,sid,title,url,kind,now))
    return {"id":bid,"student_id":sid,"title":title,"url":url,"kind":kind,"created_at":now}

def set_progress(sid, key, value, meta=None):
    sid=ensure_student(sid); now=_now()
    with _conn() as c:
        c.execute("""INSERT INTO progress(id,student_id,key,value,meta,updated_at)
                     VALUES(?,?,?,?,?,?)
                     ON CONFLICT(student_id,key) DO UPDATE SET value=excluded.value, meta=excluded.meta, updated_at=excluded.updated_at""",
                  (str(uuid4()),sid,key,float(value),json.dumps(meta or {}),now))
    with _conn() as c:
        return dict(c.execute("SELECT * FROM progress WHERE student_id=? AND key=?", (sid,key)).fetchone())

def add_mock(sid, exam, score, accuracy, attempted, total):
    sid=ensure_student(sid); mid=str(uuid4()); now=_now()
    with _conn() as c:
        c.execute("INSERT INTO mock_history VALUES (?,?,?,?,?,?,?,?)", (mid,sid,exam,float(score),float(accuracy),int(attempted),int(total),now))
    return {"id":mid,"student_id":sid,"exam":exam,"score":score,"accuracy":accuracy,"attempted":attempted,"total":total,"created_at":now}

init_db()
