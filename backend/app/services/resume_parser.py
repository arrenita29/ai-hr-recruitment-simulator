import io
import re
import pdfplumber

SKILLS = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "SQL", "MySQL", "PostgreSQL",
    "MongoDB", "HTML", "CSS", "React", "Node.js", "Express", "Django", "Flask", "FastAPI",
    "Spring Boot", "Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow", "PyTorch",
    "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Power BI", "Tableau", "Excel",
    "Statistics", "Data Analysis", "Data Visualization", "Big Data", "Hadoop", "Spark",
    "LangChain", "LLM", "Generative AI", "RAG", "OpenAI", "REST API", "Figma",
    "Communication", "Leadership", "Teamwork", "Problem Solving",
]

DEGREES = [
    "B.Tech", "B.E", "B.Sc", "BCA", "B.Com", "BBA", "M.Tech", "M.E", "M.Sc", "MCA", "MBA",
    "Ph.D", "Bachelor", "Master", "Diploma",
]

SECTION_WORDS = {"resume", "curriculum vitae", "cv", "profile", "summary", "contact"}


def extract_text(file_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        return "\n".join((page.extract_text() or "") for page in pdf.pages)


def _find(text: str, words: list[str]) -> list[str]:
    lower = text.lower()
    found = []
    for word in words:
        pattern = r"(?<![a-z0-9])" + re.escape(word.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, lower):
            found.append(word)
    return found


def extract_skills(text: str) -> list[str]:
    return _find(text, SKILLS)


def extract_name(text: str) -> str | None:
    """The name is usually the first short line with only letters."""
    for line in text.splitlines()[:5]:
        line = line.strip()
        if 1 < len(line.split()) <= 4 and re.fullmatch(r"[A-Za-z .]+", line) and line.lower() not in SECTION_WORDS:
            return line.title()
    return None


def extract_experience_years(text: str) -> float | None:
    matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)", text.lower())
    years = [float(m) for m in matches if float(m) < 50]
    return max(years) if years else None


def parse_resume(text: str) -> dict:
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    phone = re.search(r"\+?\d[\d\s-]{8,}\d", text)
    linkedin = re.search(r"linkedin\.com/in/[\w-]+", text, re.I)
    github = re.search(r"github\.com/[\w-]+", text, re.I)
    return {
        "name": extract_name(text),
        "email": email.group() if email else None,
        "phone": phone.group().strip() if phone else None,
        "linkedin": linkedin.group() if linkedin else None,
        "github": github.group() if github else None,
        "skills": extract_skills(text),
        "education": _find(text, DEGREES),
        "experience_years": extract_experience_years(text),
        "word_count": len(text.split()),
    }
