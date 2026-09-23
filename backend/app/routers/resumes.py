from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import get_current_user
from app.services.resume_parser import extract_text, parse_resume

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