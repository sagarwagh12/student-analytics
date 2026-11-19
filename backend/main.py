import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parents[1]
FRONTEND = BASE / "frontend"

app = FastAPI(title="Student Performance Analytics API", version="2.0.0")
app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")


def connect():
    # Database details come from environment variables (never written in code)
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "studentdb"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ["DB_PASSWORD"],
        row_factory=dict_row,
        connect_timeout=10,
    )


def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY, name TEXT NOT NULL, class_name TEXT NOT NULL,
            section TEXT NOT NULL DEFAULT 'A', email TEXT DEFAULT '')""")
        con.execute("""CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
            student_id TEXT NOT NULL REFERENCES students(student_id),
            subject TEXT NOT NULL, exam TEXT NOT NULL,
            marks DOUBLE PRECISION NOT NULL, attendance DOUBLE PRECISION NOT NULL,
            record_date TEXT NOT NULL, created_at TEXT NOT NULL)""")
        count = con.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
        if count == 0:
            seed = [
                ("S001", "Aarav Patil", "BSc Cloud Computing", "A", "aarav@example.com"),
                ("S002", "Ananya Shah", "BSc Cloud Computing", "A", "ananya@example.com"),
                ("S003", "Vivaan Kulkarni", "BSc Cloud Computing", "A", "vivaan@example.com"),
                ("S004", "Isha Joshi", "BSc Cloud Computing", "B", "isha@example.com"),
                ("S005", "Reyansh More", "BSc Cloud Computing", "B", "reyansh@example.com"),
                ("S006", "Sara Deshmukh", "BSc Cloud Computing", "B", "sara@example.com"),
            ]
            sample = [
                ("S001", "Cloud Computing", "Internal 1", 82, 94), ("S002", "Cloud Computing", "Internal 1", 76, 91),
                ("S003", "Cloud Computing", "Internal 1", 68, 86), ("S004", "Cloud Computing", "Internal 1", 91, 97),
                ("S005", "Cloud Computing", "Internal 1", 54, 78), ("S006", "Cloud Computing", "Internal 1", 88, 96),
                ("S001", "Python", "Internal 1", 89, 94), ("S002", "Python", "Internal 1", 73, 91),
                ("S003", "Python", "Internal 1", 62, 86), ("S004", "Python", "Internal 1", 93, 97),
                ("S005", "Python", "Internal 1", 58, 78), ("S006", "Python", "Internal 1", 84, 96),
            ]
            now = datetime.now(timezone.utc).isoformat()
            today = datetime.now().date().isoformat()
            with con.cursor() as cur:
                cur.executemany(
                    "INSERT INTO students (student_id,name,class_name,section,email) VALUES (%s,%s,%s,%s,%s)",
                    seed)
                cur.executemany(
                    """INSERT INTO records (student_id,subject,exam,marks,attendance,record_date,created_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    [(a, b, c, d, e, today, now) for a, b, c, d, e in sample])


@app.on_event("startup")
def startup():
    init_db()


class LoginRequest(BaseModel):
    username: str
    password: str


class RecordIn(BaseModel):
    student_id: str
    subject: str = Field(min_length=1, max_length=60)
    exam: str = Field(min_length=1, max_length=60)
    marks: float = Field(ge=0, le=100)
    attendance: float = Field(ge=0, le=100)
    record_date: Optional[str] = None


@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/health")
def health():
    with connect() as con:
        con.execute("SELECT 1")
    return {"status": "ok", "database": "Amazon RDS PostgreSQL"}


@app.post("/api/login")
def login(body: LoginRequest):
    users = {
        "teacher": ("Teacher123", "teacher"),
        "admin": ("Admin123", "admin"),
    }
    item = users.get(body.username)
    if not item or item[0] != body.password:
        raise HTTPException(status_code=401, detail="Username or password is incorrect")
    return {"ok": True, "username": body.username, "role": item[1]}


@app.get("/api/students")
def students():
    with connect() as con:
        rows = con.execute("SELECT * FROM students ORDER BY student_id").fetchall()
    return [dict(r) for r in rows]


@app.get("/api/records")
def records():
    with connect() as con:
        rows = con.execute("""SELECT r.*, s.name, s.class_name, s.section
            FROM records r JOIN students s ON s.student_id = r.student_id
            ORDER BY r.id DESC LIMIT 100""").fetchall()
    return [dict(r) for r in rows]


@app.post("/api/records")
def add_record(body: RecordIn):
    with connect() as con:
        exists = con.execute("SELECT 1 FROM students WHERE student_id = %s", (body.student_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Student ID not found")
        now = datetime.now(timezone.utc).isoformat()
        con.execute(
            """INSERT INTO records (student_id,subject,exam,marks,attendance,record_date,created_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (body.student_id, body.subject, body.exam, body.marks, body.attendance,
             body.record_date or datetime.now().date().isoformat(), now))
    return {"ok": True, "message": "Record saved"}


@app.get("/api/summary")
def summary():
    with connect() as con:
        total_students = con.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
        row = con.execute("""SELECT AVG(marks) AS avg_marks, AVG(attendance) AS avg_attendance,
            COALESCE(SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END), 0) AS passed, COUNT(*) AS total
            FROM records""").fetchone()
        subject_rows = con.execute("""SELECT subject, ROUND(AVG(marks)::numeric, 1)::float AS average
            FROM records GROUP BY subject ORDER BY subject""").fetchall()
        class_rows = con.execute("""SELECT s.class_name, ROUND(AVG(r.marks)::numeric, 1)::float AS average
            FROM records r JOIN students s ON s.student_id = r.student_id
            GROUP BY s.class_name""").fetchall()
    total = row["total"] or 0
    return {
        "total_students": total_students,
        "total_records": total,
        "average_marks": round(float(row["avg_marks"] or 0), 1),
        "attendance_percentage": round(float(row["avg_attendance"] or 0), 1),
        "pass_percentage": round(float(row["passed"] or 0) * 100 / total, 1) if total else 0,
        "subjects": [dict(x) for x in subject_rows],
        "classes": [dict(x) for x in class_rows],
    }
