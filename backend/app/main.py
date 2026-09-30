from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
from app import models  # noqa: F401  (registers tables)
from app.routers import auth, jobs, resumes, applications, interviews, dashboard
from app.services.ai import ai_available

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI HR Recruitment Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(applications.router)
app.include_router(interviews.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "AI HR Recruitment Simulator API", "docs": "/docs"}


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected", "ai_mode": "gpt" if ai_available() else "rule-based"}
