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