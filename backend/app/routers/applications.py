from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import get_current_user, require_hr
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

def _detail(db: Session, application: models.Application) -> schemas.ApplicationDetail:
    job = db.get(models.Job, application.job_id)
    resume = db.get(models.Resume, application.resume_id)
    candidate = db.get(models.User, application.user_id)
    result = match_resume_to_job(resume.raw_text or "", job) if resume and job else {}
    interview = (
        db.query(models.Interview)
        .filter(models.Interview.application_id == application.id)
        .order_by(models.Interview.created_at.desc())
        .first()
    )
    return schemas.ApplicationDetail(
        **schemas.ApplicationOut.model_validate(application).model_dump(),
        matched_skills=result.get("matched_skills", []),
        missing_skills=result.get("missing_skills", []),
        job_title=job.title if job else "",
        candidate_name=candidate.name if candidate else "",
        candidate_email=candidate.email if candidate else "",
        interview_id=interview.id if interview else None,
        interview_score=interview.ai_score if interview else None,
    )


@router.get("/job/{job_id}", response_model=list[schemas.ApplicationDetail])
def applications_for_job(job_id: int, db: Session = Depends(get_db), hr=Depends(require_hr)):
    apps = db.query(models.Application).filter(models.Application.job_id == job_id).all()
    return [_detail(db, a) for a in apps]


@router.get("/{application_id}", response_model=schemas.ApplicationDetail)
def get_application(application_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    application = db.get(models.Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.user_id != user.id and user.role != "hr":
        raise HTTPException(status_code=403, detail="Not your application")
    return _detail(db, application)


@router.patch("/{application_id}/status", response_model=schemas.ApplicationOut)
def update_status(application_id: int, data: schemas.StatusUpdate,
                  db: Session = Depends(get_db), hr=Depends(require_hr)):
    application = db.get(models.Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    application.status = data.status
    db.commit()
    db.refresh(application)
    return application
