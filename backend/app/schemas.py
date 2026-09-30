from typing import Literal
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["candidate", "hr"] = "candidate"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

from datetime import datetime

class JobCreate(BaseModel):
    title: str
    description: str
    skills_required: str = ""

class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    skills_required: str | None
    created_by: int | None
    created_at: datetime

class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    file_name: str
    parsed_json: dict | None
    uploaded_at: datetime

class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: int

class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    resume_id: int
    match_score: float
    status: str
    created_at: datetime

class ApplicationResult(ApplicationOut):
    matched_skills: list[str] = []
    missing_skills: list[str] = []

class RankedCandidate(BaseModel):
    rank: int
    application_id: int
    candidate_name: str
    candidate_email: str
    match_score: float
    interview_score: float | None = None
    final_score: float
    status: str

# ---------------------------------------------------------------- matching

class JobMatch(BaseModel):
    job_id: int
    title: str
    match_score: float
    matched_skills: list[str] = []
    missing_skills: list[str] = []

class ApplicationDetail(ApplicationResult):
    job_title: str
    candidate_name: str
    candidate_email: str
    interview_id: int | None = None
    interview_score: float | None = None

class StatusUpdate(BaseModel):
    status: Literal["applied", "interviewed", "shortlisted", "rejected", "hired"]


# ---------------------------------------------------------------- interviews

class InterviewStart(BaseModel):
    application_id: int
    num_questions: int = 5

class InterviewSubmit(BaseModel):
    answers: list[str]

class InterviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    questions: list[str]
    answers: list[str] | None = None
    ai_score: float | None = None
    feedback: str | None = None
    created_at: datetime

class QuestionResult(BaseModel):
    question: str
    answer: str
    score: float
    feedback: str

class InterviewResult(BaseModel):
    interview_id: int
    application_id: int
    score: float
    overall_feedback: str
    strengths: list[str] = []
    improvements: list[str] = []
    per_question: list[QuestionResult]
    evaluated_by: str


# ---------------------------------------------------------------- dashboard

class JobStats(BaseModel):
    job_id: int
    title: str
    applications: int
    interviewed: int
    avg_match_score: float | None

class DashboardStats(BaseModel):
    total_jobs: int
    total_candidates: int
    total_applications: int
    total_interviews: int
    status_counts: dict[str, int]
    jobs: list[JobStats]
