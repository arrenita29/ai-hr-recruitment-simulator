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