from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import require_hr

router = APIRouter(prefix="/dashboard", tags=["HR Dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def stats(db: Session = Depends(get_db), hr=Depends(require_hr)):
    applications = db.query(models.Application).all()
    jobs = db.query(models.Job).order_by(models.Job.created_at.desc()).all()
    interviewed_ids = {
        i.application_id for i in db.query(models.Interview).filter(models.Interview.ai_score.isnot(None)).all()
    }

    job_stats = []
    for job in jobs:
        apps = [a for a in applications if a.job_id == job.id]
        job_stats.append(schemas.JobStats(
            job_id=job.id,
            title=job.title,
            applications=len(apps),
            interviewed=sum(1 for a in apps if a.id in interviewed_ids),
            avg_match_score=round(sum(a.match_score for a in apps) / len(apps), 1) if apps else None,
        ))

    return schemas.DashboardStats(
        total_jobs=len(jobs),
        total_candidates=db.query(models.User).filter(models.User.role == "candidate").count(),
        total_applications=len(applications),
        total_interviews=len(interviewed_ids),
        status_counts=dict(Counter(a.status for a in applications)),
        jobs=job_stats,
    )
