import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import get_current_user
from app.services.ai import generate_questions, evaluate_answers
from app.services.matcher import job_skills

router = APIRouter(prefix="/interviews", tags=["Interviews"])


def _load_application(db: Session, application_id: int, user) -> models.Application:
    application = db.get(models.Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.user_id != user.id and user.role != "hr":
        raise HTTPException(status_code=403, detail="Not your application")
    return application


@router.post("/start", response_model=schemas.InterviewOut, status_code=201)
def start_interview(data: schemas.InterviewStart, db: Session = Depends(get_db), user=Depends(get_current_user)):
    application = _load_application(db, data.application_id, user)
    if application.user_id != user.id:
        raise HTTPException(status_code=403, detail="Only the candidate can take the interview")

    existing = (
        db.query(models.Interview)
        .filter(models.Interview.application_id == application.id)
        .order_by(models.Interview.created_at.desc())
        .first()
    )
    if existing and existing.ai_score is None:
        return existing  # unfinished interview -> continue it
    if existing:
        raise HTTPException(status_code=400, detail="Interview already completed for this application")

    job = db.get(models.Job, application.job_id)
    resume = db.get(models.Resume, application.resume_id)
    resume_skills = (resume.parsed_json or {}).get("skills", []) if resume else []
    count = max(3, min(data.num_questions, 10))

    interview = models.Interview(
        application_id=application.id,
        questions=generate_questions(job, resume_skills, job_skills(job), count),
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.post("/{interview_id}/submit", response_model=schemas.InterviewResult)
def submit_interview(interview_id: int, data: schemas.InterviewSubmit,
                     db: Session = Depends(get_db), user=Depends(get_current_user)):
    interview = db.get(models.Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    application = _load_application(db, interview.application_id, user)
    if application.user_id != user.id:
        raise HTTPException(status_code=403, detail="Only the candidate can submit answers")
    if interview.ai_score is not None:
        raise HTTPException(status_code=400, detail="Interview already submitted")
    if len(data.answers) != len(interview.questions):
        raise HTTPException(status_code=400,
                            detail=f"Expected {len(interview.questions)} answers, got {len(data.answers)}")

    job = db.get(models.Job, application.job_id)
    result = evaluate_answers(job, interview.questions, data.answers, job_skills(job))

    interview.answers = data.answers
    interview.ai_score = result["score"]
    interview.feedback = json.dumps({k: result[k] for k in
                                     ("overall_feedback", "strengths", "improvements", "per_question", "evaluated_by")})
    application.status = "interviewed"
    db.commit()

    return schemas.InterviewResult(interview_id=interview.id, application_id=application.id, **result)


@router.get("/{interview_id}", response_model=schemas.InterviewOut)
def get_interview(interview_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    interview = db.get(models.Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    _load_application(db, interview.application_id, user)
    return interview


@router.get("/{interview_id}/result", response_model=schemas.InterviewResult)
def interview_result(interview_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    interview = db.get(models.Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    _load_application(db, interview.application_id, user)
    if interview.ai_score is None:
        raise HTTPException(status_code=400, detail="Interview not submitted yet")
    saved = json.loads(interview.feedback or "{}")
    return schemas.InterviewResult(
        interview_id=interview.id,
        application_id=interview.application_id,
        score=interview.ai_score,
        overall_feedback=saved.get("overall_feedback", ""),
        strengths=saved.get("strengths", []),
        improvements=saved.get("improvements", []),
        per_question=saved.get("per_question", []),
        evaluated_by=saved.get("evaluated_by", "unknown"),
    )
