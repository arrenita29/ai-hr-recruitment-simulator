"""AI helpers for the interview stage.

If OPENAI_API_KEY is set in .env, questions and scoring come from GPT.
If not (or if the API call fails), a rule-based fallback is used, so the
app always works - even offline or on a free hosting plan.
"""
import json
import logging
from app.config import settings
from app.services.matcher import cosine_similarity, has_skill, tokenize

log = logging.getLogger(__name__)


def ai_available() -> bool:
    return bool(settings.OPENAI_API_KEY)


def _ask_gpt_json(prompt: str) -> dict | None:
    """Send a prompt to GPT and return the JSON it answers with (or None)."""
    if not ai_available():
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=30, max_retries=1)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert technical HR interviewer. Reply with JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as exc:  # network error, bad key, no credits...
        log.warning("OpenAI call failed, using fallback: %s", exc)
        return None


# ---------------------------------------------------------------- questions

def _fallback_questions(job_title: str, skills: list[str], count: int) -> list[str]:
    questions = [f"Tell us about yourself and why you are a good fit for the {job_title} role."]
    for skill in skills[: count - 2]:
        questions.append(f"Describe a project where you used {skill}. What problem did it solve and what was your role?")
    questions.append("Tell us about a difficult problem you faced in a project and how you solved it.")
    generic = [
        "How do you keep your technical skills up to date?",
        "How do you handle deadlines when working in a team?",
        "Where do you see yourself in the next three years?",
    ]
    for q in generic:
        if len(questions) >= count:
            break
        questions.append(q)
    return questions[:count]


def generate_questions(job, resume_skills: list[str], required_skills: list[str], count: int = 5) -> list[str]:
    prompt = (
        f"Create {count} interview questions for a candidate applying to this job.\n"
        f"Job title: {job.title}\nJob description: {job.description}\n"
        f"Required skills: {', '.join(required_skills) or 'not specified'}\n"
        f"Candidate's resume skills: {', '.join(resume_skills) or 'not specified'}\n"
        "Mix technical questions (on the required skills) with 1-2 behavioural questions. "
        'Return JSON: {"questions": ["...", "..."]}'
    )
    data = _ask_gpt_json(prompt)
    if data and isinstance(data.get("questions"), list) and data["questions"]:
        return [str(q) for q in data["questions"]][:count]
    focus = [s for s in required_skills if s in resume_skills] + [s for s in required_skills if s not in resume_skills]
    return _fallback_questions(job.title, focus or resume_skills, count)


# ---------------------------------------------------------------- scoring

def _fallback_score_answer(question: str, answer: str, skills: list[str]) -> tuple[float, str]:
    words = len(answer.split())
    if words == 0:
        return 0.0, "No answer given."

    # 1. Length / detail (0-40): full marks at ~80 words
    detail = min(words / 80, 1) * 40
    # 2. Relevance to the question (0-30)
    relevance = min(cosine_similarity(question, answer) * 3, 1) * 30
    # 3. Mentions relevant skills / concrete terms (0-30)
    mentioned = [s for s in skills if has_skill(answer, s)]
    specifics = sum(1 for w in tokenize(answer) if w in {"project", "built", "developed", "implemented",
                                                       "designed", "improved", "result", "team", "deployed"})
    concrete = min((len(mentioned) * 10) + (specifics * 5), 30)

    score = round(detail + relevance + concrete, 1)
    if score >= 75:
        tip = "Strong, detailed answer."
    elif score >= 50:
        tip = "Good answer - add a concrete example with results to make it stronger."
    elif words < 25:
        tip = "Too short - explain what you did, how, and what the outcome was."
    else:
        tip = "Try to answer the question more directly and mention specific tools or skills."
    return score, tip


def evaluate_answers(job, questions: list[str], answers: list[str], skills: list[str]) -> dict:
    qa_text = "\n\n".join(f"Q{i + 1}: {q}\nA{i + 1}: {a}" for i, (q, a) in enumerate(zip(questions, answers)))
    prompt = (
        f"Evaluate this interview for the role '{job.title}'.\n"
        f"Required skills: {', '.join(skills) or 'not specified'}\n\n{qa_text}\n\n"
        "Score each answer from 0 to 100 for correctness, depth and communication, with one line of feedback. "
        'Return JSON: {"scores": [numbers], "feedback": ["..."], "overall_feedback": "...", '
        '"strengths": ["..."], "improvements": ["..."]}'
    )
    data = _ask_gpt_json(prompt)
    if data and isinstance(data.get("scores"), list) and len(data["scores"]) == len(questions):
        scores = [max(0.0, min(100.0, float(s))) for s in data["scores"]]
        feedback = list(data.get("feedback") or [""] * len(scores))
        return {
            "score": round(sum(scores) / len(scores), 1),
            "per_question": [
                {"question": q, "answer": a, "score": s, "feedback": f}
                for q, a, s, f in zip(questions, answers, scores, feedback)
            ],
            "overall_feedback": data.get("overall_feedback", ""),
            "strengths": data.get("strengths", []),
            "improvements": data.get("improvements", []),
            "evaluated_by": "gpt",
        }

    per_question = []
    for q, a in zip(questions, answers):
        s, tip = _fallback_score_answer(q, a, skills)
        per_question.append({"question": q, "answer": a, "score": s, "feedback": tip})
    total = round(sum(p["score"] for p in per_question) / len(per_question), 1)
    strong = [p["question"] for p in per_question if p["score"] >= 70]
    weak = [p["question"] for p in per_question if p["score"] < 50]
    return {
        "score": total,
        "per_question": per_question,
        "overall_feedback": (
            "Excellent interview." if total >= 75 else
            "Good interview with room to add more detail." if total >= 50 else
            "Answers need more detail and concrete examples."
        ),
        "strengths": strong[:3],
        "improvements": weak[:3],
        "evaluated_by": "rule-based",
    }
