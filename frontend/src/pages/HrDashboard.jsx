import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { ErrorBox } from "../components/ui.jsx";

export default function HrDashboard() {
  const [stats, setStats] = useState(null);
  const [form, setForm] = useState({ title: "", description: "", skills_required: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () => api.stats().then(setStats).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const createJob = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.createJob(form);
      setForm({ title: "", description: "", skills_required: "" });
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">HR Dashboard</h1>
        <p className="text-slate-500">Post jobs and review AI-ranked candidates.</p>
      </div>
      <ErrorBox message={error} />

      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Stat label="Open jobs" value={stats.total_jobs} />
          <Stat label="Candidates" value={stats.total_candidates} />
          <Stat label="Applications" value={stats.total_applications} />
          <Stat label="Interviews done" value={stats.total_interviews} />
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        <form onSubmit={createJob} className="card space-y-3 lg:col-span-1">
          <h2 className="font-semibold text-lg">Post a new job</h2>
          <div><label className="label">Job title</label><input className="input" value={form.title} onChange={set("title")} required /></div>
          <div><label className="label">Description</label><textarea className="input min-h-28" value={form.description} onChange={set("description")} required /></div>
          <div>
            <label className="label">Required skills</label>
            <input className="input" placeholder="Python, SQL, Power BI" value={form.skills_required} onChange={set("skills_required")} />
            <p className="text-xs text-slate-500 mt-1">Comma separated</p>
          </div>
          <button className="btn-primary w-full" disabled={busy}>{busy ? "Posting…" : "Post job"}</button>
        </form>

        <div className="card lg:col-span-2">
          <h2 className="font-semibold text-lg mb-4">Jobs</h2>
          {stats?.jobs.length === 0 && <p className="text-sm text-slate-500">No jobs yet. Post your first job.</p>}
          <div className="space-y-3">
            {stats?.jobs.map((j) => (
              <Link key={j.job_id} to={`/jobs/${j.job_id}`}
                className="flex items-center justify-between rounded-xl border border-slate-200 p-4 hover:border-indigo-300 hover:bg-indigo-50/40 transition">
                <div>
                  <div className="font-semibold">{j.title}</div>
                  <div className="text-sm text-slate-500">
                    {j.applications} applicants · {j.interviewed} interviewed
                    {j.avg_match_score != null && ` · avg match ${j.avg_match_score}%`}
                  </div>
                </div>
                <span className="text-indigo-600 text-sm font-semibold">View ranking →</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="card">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="text-3xl font-bold text-slate-900 mt-1">{value}</div>
    </div>
  );
}
