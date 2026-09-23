from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import require_hr

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=schemas.JobOut, status_code=201)
def create_job(data: schemas.JobCreate, db: Session = Depends(get_db), hr=Depends(require_hr)):
    job = models.Job(**data.model_dump(), created_by=hr.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=list[schemas.JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).order_by(models.Job.created_at.desc()).all()

@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/{job_id}/ranking", response_model=list[schemas.RankedCandidate])
def job_ranking(job_id: int, db: Session = Depends(get_db), hr=Depends(require_hr)):
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    rows = (
        db.query(models.Application, models.User)
        .join(models.User, models.Application.user_id == models.User.id)
        .filter(models.Application.job_id == job_id)
        .all()
    )

    ranked = []
    for application, user in rows:
        interview = (
            db.query(models.Interview)
            .filter(models.Interview.application_id == application.id)
            .order_by(models.Interview.created_at.desc())
            .first()
        )
        interview_score = interview.ai_score if interview and interview.ai_score is not None else None

        if interview_score is not None:
            final = round(0.6 * application.match_score + 0.4 * interview_score, 1)
        else:
            final = application.match_score

        ranked.append({
            "application_id": application.id,
            "candidate_name": user.name,
            "candidate_email": user.email,
            "match_score": application.match_score,
            "interview_score": interview_score,
            "final_score": final,
            "status": application.status,
        })

    ranked.sort(key=lambda r: r["final_score"], reverse=True)
    for position, row in enumerate(ranked, start=1):
        row["rank"] = position
    return ranked