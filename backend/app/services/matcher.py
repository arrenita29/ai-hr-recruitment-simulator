import math
import re
from collections import Counter
from app.services.resume_parser import extract_skills

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "are", "was", "you", "your", "our",
    "from", "have", "has", "will", "can", "into", "using", "use", "work", "working",
    "able", "such", "also", "any", "all", "not", "but", "they", "their", "them",
}

def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z][a-z+#.]*", text.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]

def cosine_similarity(a: str, b: str) -> float:
    ca, cb = Counter(tokenize(a)), Counter(tokenize(b))
    dot = sum(ca[w] * cb[w] for w in set(ca) & set(cb))
    na = math.sqrt(sum(v * v for v in ca.values()))
    nb = math.sqrt(sum(v * v for v in cb.values()))
    return dot / (na * nb) if na and nb else 0.0

def has_skill(text: str, skill: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None

def job_skills(job) -> list[str]:
    if job.skills_required:
        return [s.strip() for s in job.skills_required.split(",") if s.strip()]
    return extract_skills(job.description)

def match_resume_to_job(resume_text: str, job) -> dict:
    required = job_skills(job)
    matched = [s for s in required if has_skill(resume_text, s)]
    missing = [s for s in required if s not in matched]

    skill_score = len(matched) / len(required) if required else 0
    text_score = min(cosine_similarity(resume_text, f"{job.description} {job.skills_required or ''}") * 2, 1)

    return {
        "match_score": round((0.7 * skill_score + 0.3 * text_score) * 100, 1),
        "matched_skills": matched,
        "missing_skills": missing,
    }