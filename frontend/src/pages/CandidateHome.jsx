import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../App.jsx";
import { ErrorBox, ScoreBadge, Skills, StatusBadge, ProgressBar } from "../components/ui.jsx";

export default function CandidateHome() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [resume, setResume] = useState(null);
  const [matches, setMatches] = useState([]);
  const [apps, setApps] = useState([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const loadApps = async () => {
    const list = await api.myApplications();
    setApps(await Promise.all(list.map((a) => api.application(a.id))));
  };

  useEffect(() => {
    (async () => {
      try {
        const resumes = await api.myResumes();
        if (resumes.length) {
          setResume(resumes[0]);
          setMatches(await api.matches(resumes[0].id));
        }
        await loadApps();
      } catch (e) {
        setError(e.message);
      }
    })();
  }, []);

  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const r = await api.uploadResume(file);
      setResume(r);
      setMatches(await api.matches(r.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  };

  const apply = async (jobId) => {
    setError("");
    try {
      await api.apply(jobId, resume.id);
      await loadApps();
    } catch (err) {
      setError(err.message);
    }
  };

  const appliedJobIds = new Set(apps.map((a) => a.job_id));
  const p = resume?.parsed_json || {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Hi {user.name} 👋</h1>
        <p className="text-slate-500">Upload your resume, find matching jobs and take the AI interview.</p>
      </div>
      <ErrorBox message={error} />

      <section className="card">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h2 className="font-semibold text-lg">1. Your resume</h2>
            <p className="text-sm text-slate-500">{resume ? `Using: ${resume.file_name}` : "Upload a PDF resume to get started."}</p>
          </div>
          <label className="btn-primary">
            {busy ? "Analysing…" : resume ? "Upload new PDF" : "Upload resume (PDF)"}
            <input type="file" accept=".pdf" className="hidden" onChange={upload} disabled={busy} />
          </label>
        </div>

        {resume && (
          <div className="mt-5 grid sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <Info label="Name" value={p.name} />
            <Info label="Email" value={p.email} />
            <Info label="Education" value={p.education?.join(", ")} />
            <Info label="Experience" value={p.experience_years ? `${p.experience_years} years` : null} />
            <div className="sm:col-span-2 lg:col-span-4">
              <div className="text-slate-500 mb-1">Skills found by AI</div>
              <Skills items={p.skills} />
            </div>
          </div>
        )}
      </section>

      {resume && (
        <section className="card">
          <h2 className="font-semibold text-lg mb-4">2. Jobs matched to your resume</h2>
          {matches.length === 0 && <p className="text-sm text-slate-500">No jobs posted yet.</p>}
          <div className="space-y-3">
            {matches.map((m) => (
              <div key={m.job_id} className="rounded-xl border border-slate-200 p-4">
                <div className="flex items-center justify-between gap-3 flex-wrap">
                  <div className="font-semibold">{m.title}</div>
                  <div className="flex items-center gap-3">
                    <ScoreBadge score={m.match_score} />
                    {appliedJobIds.has(m.job_id)
                      ? <span className="text-sm text-slate-500">Applied ✓</span>
                      : <button className="btn-primary" onClick={() => apply(m.job_id)}>Apply</button>}
                  </div>
                </div>
                <div className="mt-2"><ProgressBar value={m.match_score} /></div>
                <div className="mt-3 grid sm:grid-cols-2 gap-3 text-sm">
                  <div><div className="text-slate-500 mb-1">You have</div><Skills items={m.matched_skills} tone="green" /></div>
                  <div><div className="text-slate-500 mb-1">Missing</div><Skills items={m.missing_skills} tone="red" /></div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="card">
        <h2 className="font-semibold text-lg mb-4">3. My applications & interviews</h2>
        {apps.length === 0 && <p className="text-sm text-slate-500">You haven't applied to any job yet.</p>}
        <div className="overflow-x-auto">
          {apps.length > 0 && (
            <table className="w-full text-sm">
              <thead className="text-left text-slate-500">
                <tr><th className="py-2">Job</th><th>Match</th><th>Interview</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {apps.map((a) => (
                  <tr key={a.id} className="border-t border-slate-100">
                    <td className="py-3 font-medium">{a.job_title}</td>
                    <td><ScoreBadge score={a.match_score} /></td>
                    <td><ScoreBadge score={a.interview_score} /></td>
                    <td><StatusBadge status={a.status} /></td>
                    <td className="text-right">
                      {a.interview_score != null
                        ? <Link className="btn-outline" to={`/result/${a.interview_id}`}>View result</Link>
                        : <button className="btn-primary" onClick={() => navigate(`/interview/${a.id}`)}>
                            {a.interview_id ? "Continue interview" : "Start AI interview"}
                          </button>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div>
      <div className="text-slate-500">{label}</div>
      <div className="font-medium text-slate-800">{value || "—"}</div>
    </div>
  );
}
