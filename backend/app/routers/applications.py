from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import get_current_user
from app.services.matcher import match_resume_to_job

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("", response_model=schemas.ApplicationResult, status_code=201)
def apply_to_job(data: schemas.ApplicationCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    job = db.get(models.Job, data.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = db.get(models.Resume, data.resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")

    already = db.query(models.Application).filter(
        models.Application.user_id == user.id, models.Application.job_id == job.id
    ).first()
    if already:
        raise HTTPException(status_code=400, detail="You already applied to this job")

    result = match_resume_to_job(resume.raw_text or "", job)

    application = models.Application(
        user_id=user.id,
        job_id=job.id,
        resume_id=resume.id,
        match_score=result["match_score"],
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return schemas.ApplicationResult(
        **schemas.ApplicationOut.model_validate(application).model_dump(),
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
    )

@router.get("/me", response_model=list[schemas.ApplicationOut])
def my_applications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Application).filter(models.Application.user_id == user.id).all()