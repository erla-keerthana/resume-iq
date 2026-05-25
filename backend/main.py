import asyncio
import os

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from file_service import process_file, fetch_profile_text
from ai_service import (
    analyze_resume,
    generate_cover_letter,
    generate_interview_questions,
    optimize_keywords,
    analyze_skill_gap,
)
from database import get_db, init_db
from models import AnalysisHistory
from auth_service import (
    create_token,
    signup_user,
    authenticate_user,
    get_current_user_required,
)
from pdf_export import generate_report_pdf

load_dotenv()

app = FastAPI(title="ResumeIQ API")

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()


# CORS
_origins_env = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()] if _origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def _read_and_validate_file(file: UploadFile) -> bytes:
    """Read uploaded file and validate size."""
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(file_bytes) // (1024*1024)} MB). Maximum is 10 MB.",
        )
    return file_bytes


async def _extract_text(file_bytes: bytes, filename: str) -> str:
    """Process file and extract text."""
    try:
        text = await asyncio.to_thread(process_file, file_bytes, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {e}")
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from the file")
    return text


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/")
def health_check():
    api_key_set = bool(os.getenv("OPENROUTER_API_KEY"))
    return {
        "status": "ok" if api_key_set else "degraded",
        "message": "ResumeIQ API is running",
        "api_key_configured": api_key_set,
    }


# ---------------------------------------------------------------------------
# Core: Resume Analysis (existing)
# ---------------------------------------------------------------------------

@app.post("/upload")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db),
):
    file_bytes = await _read_and_validate_file(file)
    resume_text = await _extract_text(file_bytes, file.filename)

    try:
        result = await asyncio.to_thread(analyze_resume, resume_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")

    # Save to history for authenticated user
    user = get_current_user_required(request, db)
    entry = AnalysisHistory(
        user_id=user.id,
        filename=file.filename or "unknown",
        job_description=job_description[:2000],
        ats_score=result.get("ats_score", 0),
        match_score=result.get("match_score", 0),
        result_json=result,
    )
    db.add(entry)
    db.commit()

    return result


# ---------------------------------------------------------------------------
# Cover Letter Generator
# ---------------------------------------------------------------------------

@app.post("/generate/cover-letter")
async def api_cover_letter(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    file_bytes = await _read_and_validate_file(file)
    resume_text = await _extract_text(file_bytes, file.filename)

    try:
        letter = await asyncio.to_thread(generate_cover_letter, resume_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"cover_letter": letter}


# ---------------------------------------------------------------------------
# Interview Questions Generator
# ---------------------------------------------------------------------------

@app.post("/generate/interview-questions")
async def api_interview_questions(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    file_bytes = await _read_and_validate_file(file)
    resume_text = await _extract_text(file_bytes, file.filename)

    try:
        questions = await asyncio.to_thread(generate_interview_questions, resume_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return questions


# ---------------------------------------------------------------------------
# Keyword Optimizer
# ---------------------------------------------------------------------------

@app.post("/generate/keyword-optimize")
async def api_keyword_optimize(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    file_bytes = await _read_and_validate_file(file)
    resume_text = await _extract_text(file_bytes, file.filename)

    try:
        result = await asyncio.to_thread(optimize_keywords, resume_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result


# ---------------------------------------------------------------------------
# Skill Gap Analysis
# ---------------------------------------------------------------------------

@app.post("/generate/skill-gap")
async def api_skill_gap(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    file_bytes = await _read_and_validate_file(file)
    resume_text = await _extract_text(file_bytes, file.filename)

    try:
        result = await asyncio.to_thread(analyze_skill_gap, resume_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result


# ---------------------------------------------------------------------------
# Export PDF Report
# ---------------------------------------------------------------------------

@app.post("/export/pdf")
async def export_pdf(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    file_bytes = await _read_and_validate_file(file)
    resume_text = await _extract_text(file_bytes, file.filename)

    try:
        result = await asyncio.to_thread(analyze_resume, resume_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    pdf_bytes = await asyncio.to_thread(generate_report_pdf, result, file.filename or "resume")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="ResumeIQ_Report.pdf"'},
    )


# ---------------------------------------------------------------------------
# LinkedIn / GitHub Profile Parsing
# ---------------------------------------------------------------------------

@app.post("/parse/profile")
async def parse_profile(
    url: str = Form(...),
    job_description: str = Form(...),
):
    try:
        profile_text = await asyncio.to_thread(fetch_profile_text, url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = await asyncio.to_thread(analyze_resume, profile_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result


# ---------------------------------------------------------------------------
# Auth: Email/Password
# ---------------------------------------------------------------------------

@app.post("/auth/signup")
def api_signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = signup_user(db, username, email, password)
    token = create_token(user.id, user.email)
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "name": user.name, "username": user.username},
    }


@app.post("/auth/login")
def api_login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, email, password)
    token = create_token(user.id, user.email)
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "name": user.name, "username": user.username},
    }


@app.get("/auth/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_required(request, db)
    return {"id": user.id, "email": user.email, "name": user.name, "username": user.username}


# ---------------------------------------------------------------------------
# Dashboard: History
# ---------------------------------------------------------------------------

@app.get("/history")
def get_history(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_required(request, db)
    entries = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.user_id == user.id)
        .order_by(AnalysisHistory.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": e.id,
            "filename": e.filename,
            "job_description": e.job_description[:200],
            "ats_score": e.ats_score,
            "match_score": e.match_score,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in entries
    ]


@app.get("/history/{entry_id}")
def get_history_detail(entry_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_required(request, db)
    entry = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.id == entry_id, AnalysisHistory.user_id == user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": entry.id,
        "filename": entry.filename,
        "job_description": entry.job_description,
        "ats_score": entry.ats_score,
        "match_score": entry.match_score,
        "result_json": entry.result_json,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


@app.delete("/history/{entry_id}")
def delete_history_entry(entry_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_required(request, db)
    entry = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.id == entry_id, AnalysisHistory.user_id == user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Analysis not found")
    db.delete(entry)
    db.commit()
    return {"ok": True}
