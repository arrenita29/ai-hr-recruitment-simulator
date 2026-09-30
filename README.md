# 🤖 AI HR Recruitment Simulator

An AI-powered hiring platform that automates the recruitment pipeline — from resume screening to interview scoring and candidate ranking.

🌐 **Live Demo:** https://hr-simulator-app.onrender.com
📘 **API Docs:** https://hr-simulator-api.onrender.com/docs

> ⏳ Hosted on a free plan — the first load may take ~50 seconds while the server wakes up.

---

## ✨ Features

**For Candidates**
- 📄 Upload a PDF resume — AI extracts name, contact, education, experience and skills
- 🎯 See every open job ranked by match %, with matched and missing skills
- 🎤 Take an AI interview with role-specific questions
- 📊 Get an instant score with question-by-question feedback

**For HR / Recruiters**
- 📝 Post jobs with required skills
- 🏆 View AI-ranked candidates per job (Final = 60% resume match + 40% interview)
- 👀 Review each candidate's skills and interview answers
- ✅ Shortlist, hire or reject in one click
- 📈 Dashboard with hiring statistics

---

## 🔄 How It Works

```
Register → Upload Resume → NLP Parsing → Job Matching → AI Interview → Scoring & Ranking → HR Dashboard
```

1. **Resume parsing** – `pdfplumber` extracts text; NLP rules detect skills, education, experience, email, phone and links
2. **Job matching** – combines skill overlap (70%) with text similarity (30%) between resume and job description
3. **AI interview** – generates questions from the job's required skills (GPT when an OpenAI key is set, rule-based otherwise)
4. **Answer scoring** – evaluates detail, relevance and use of concrete skills, with feedback per answer
5. **Ranking** – combines match and interview scores so HR sees the best candidates first

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, React Router |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| Auth | JWT (python-jose), bcrypt password hashing |
| AI / NLP | pdfplumber, rule-based NLP, OpenAI GPT (optional) |
| Deployment | Render (Blueprint: database + API + static site) |

---

## 📁 Project Structure

```
ai-hr-recruitment-simulator/
├── backend/app/
│   ├── main.py            # FastAPI app & routes
│   ├── models.py          # Database tables
│   ├── schemas.py         # Request/response models
│   ├── security.py        # JWT auth & roles
│   ├── routers/           # auth, jobs, resumes, applications, interviews, dashboard
│   └── services/          # resume_parser, matcher, ai (interview engine)
├── frontend/src/
│   ├── pages/             # Login, CandidateHome, Interview, Result, HrDashboard, JobDetail
│   └── api.js             # API client
├── requirements.txt
└── render.yaml            # One-click deployment config
```

---

## 🚀 Run Locally

**Prerequisites:** Python 3.13, Node.js 20+, PostgreSQL

**1. Backend**
```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/hr_simulator
SECRET_KEY=<any-long-random-text>
OPENAI_API_KEY=            # optional - enables GPT interviews
```

```bash
cd backend
uvicorn app.main:app --reload
```
API runs at http://127.0.0.1:8000 (docs at `/docs`)

**2. Frontend**
```bash
cd frontend
npm install
npm run dev
```
App runs at http://localhost:5173

---

## 🔮 Future Improvements

- 🎙️ Voice interviews with speech-to-text (Whisper)
- 🧠 Semantic matching with Sentence Transformers + ChromaDB
- 💬 HR Copilot chat using RAG over candidate data
- 📧 Email notifications for status updates

---

## 👩‍💻 Author

**A R Renita** — B.Tech CSE (Big Data Analytics), SRM Institute of Science and Technology
GitHub: [@arrenita29](https://github.com/arrenita29)