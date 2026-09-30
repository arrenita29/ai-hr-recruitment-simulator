import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { ErrorBox, ScoreBadge, Skills, StatusBadge } from "../components/ui.jsx";

export default function JobDetail() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [ranking, setRanking] = useState([]);
  const [details, setDetails] = useState({});
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const [jobs, rank, apps] = await Promise.all([api.jobs(), api.ranking(jobId), api.jobApplications(jobId)]);
      setJob(jobs.find((j) => j.id === Number(jobId)));
      setRanking(rank);
      setDetails(Object.fromEntries(apps.map((a) => [a.id, a])));
    } catch (e) {
      setError(e.message);
    }
  };
  useEffect(() => { load(); }, [jobId]);

  const changeStatus = async (id, status) => {
    try {
      await api.setStatus(id, status);
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="space-y-5">
      <Link to="/" className="text-sm text-indigo-600">← Back to dashboard</Link>
      <ErrorBox message={error} />
      {job && (
        <div className="card">
          <h1 className="text-2xl font-bold">{job.title}</h1>
          <p className="text-slate-600 mt-2 whitespace-pre-wrap">{job.description}</p>
          <div className="mt-3"><Skills items={(job.skills_required || "").split(",").map((s) => s.trim()).filter(Boolean)} /></div>
        </div>
      )}

      <div className="card">
        <h2 className="font-semibold text-lg mb-1">AI candidate ranking</h2>
        <p className="text-xs text-slate-500 mb-4">Final score = 60% resume match + 40% interview (match only if not interviewed yet)</p>
        {ranking.length === 0 && <p className="text-sm text-slate-500">No applicants yet.</p>}
        <div className="space-y-3">
          {ranking.map((r) => {
            const d = details[r.application_id];
            return (
              <div key={r.application_id} className="rounded-xl border border-slate-200 p-4">
                <div className="flex items-center justify-between gap-3 flex-wrap">
                  <div className="flex items-center gap-3">
                    <span className="grid place-items-center w-9 h-9 rounded-full bg-indigo-600 text-white font-bold">#{r.rank}</span>
                    <div>
                      <div className="font-semibold">{r.candidate_name}</div>
                      <div className="text-sm text-slate-500">{r.candidate_email}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="text-center"><div className="text-slate-500 text-xs">Match</div><ScoreBadge score={r.match_score} /></div>
                    <div className="text-center"><div className="text-slate-500 text-xs">Interview</div><ScoreBadge score={r.interview_score} /></div>
                    <div className="text-center"><div className="text-slate-500 text-xs">Final</div><span className="font-bold text-lg">{r.final_score}</span></div>
                    <StatusBadge status={r.status} />
                  </div>
                </div>
                {d && (
                  <div className="mt-3 grid sm:grid-cols-2 gap-3 text-sm">
                    <div><div className="text-slate-500 mb-1">Matched skills</div><Skills items={d.matched_skills} tone="green" /></div>
                    <div><div className="text-slate-500 mb-1">Missing skills</div><Skills items={d.missing_skills} tone="red" /></div>
                  </div>
                )}
                <div className="mt-3 flex flex-wrap gap-2">
                  {d?.interview_score != null && <Link className="btn-outline" to={`/result/${d.interview_id}`}>Interview answers</Link>}
                  <button className="btn-outline" onClick={() => changeStatus(r.application_id, "shortlisted")}>Shortlist</button>
                  <button className="btn-outline" onClick={() => changeStatus(r.application_id, "hired")}>Hire</button>
                  <button className="btn-outline text-rose-600" onClick={() => changeStatus(r.application_id, "rejected")}>Reject</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
