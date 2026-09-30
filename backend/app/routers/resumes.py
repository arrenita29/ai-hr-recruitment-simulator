from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import get_current_user
from app.services.resume_parser import extract_text, parse_resume
from app.services.matcher import match_resume_to_job

router = APIRouter(prefix="/resumes", tags=["Resumes"])
MAX_SIZE = 5 * 1024 * 1024  # 5 MB

@router.post("/upload", response_model=schemas.ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")
    try:
        text = extract_text(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this PDF")
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text found. Is it a scanned image PDF?")

    resume = models.Resume(
        user_id=user.id,
        file_name=file.filename,
        raw_text=text,
        parsed_json=parse_resume(text),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume

@router.get("/me", response_model=list[schemas.ResumeOut])
def my_resumes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(models.Resume)
        .filter(models.Resume.user_id == user.id)
        .order_by(models.Resume.uploaded_at.desc())
        .all()
    )

@router.get("/{resume_id}/matches", response_model=list[schemas.JobMatch])
def job_matches(resume_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Rank every open job against this resume - best match first."""
    resume = db.get(models.Resume, resume_id)
    if not resume or (resume.user_id != user.id and user.role != "hr"):
        raise HTTPException(status_code=404, detail="Resume not found")
    matches = []
    for job in db.query(models.Job).all():
        result = match_resume_to_job(resume.raw_text or "", job)
        matches.append(schemas.JobMatch(job_id=job.id, title=job.title, **result))
    matches.sort(key=lambda m: m.match_score, reverse=True)
    return matches


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    resume = db.get(models.Resume, resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    if db.query(models.Application).filter(models.Application.resume_id == resume_id).first():
        raise HTTPException(status_code=400, detail="This resume is used in an application")
    db.delete(resume)
    db.commit()
