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

def extract_text(file_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        return "\n".join((page.extract_text() or "") for page in pdf.pages)

def extract_skills(text: str) -> list[str]:
    lower = text.lower()
    found = []
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, lower):
            found.append(skill)
    return found

def parse_resume(text: str) -> dict:
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    phone = re.search(r"\+?\d[\d\s-]{8,}\d", text)
    return {
        "skills": extract_skills(text),
        "email": email.group() if email else None,
        "phone": phone.group().strip() if phone else None,
        "word_count": len(text.split()),
    }