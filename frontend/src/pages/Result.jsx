import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { ErrorBox, ProgressBar, ScoreBadge } from "../components/ui.jsx";

export default function Result() {
  const { interviewId } = useParams();
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.interviewResult(interviewId).then(setResult).catch((e) => setError(e.message));
  }, [interviewId]);

  if (error) return <div className="card"><ErrorBox message={error} /></div>;
  if (!result) return <div className="card text-slate-500">Loading result…</div>;

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <Link to="/" className="text-sm text-indigo-600">← Back</Link>
      <div className="card text-center">
        <div className="text-sm text-slate-500">Interview score</div>
        <div className="text-5xl font-bold text-slate-900 my-2">{result.score.toFixed(1)}%</div>
        <div className="max-w-sm mx-auto"><ProgressBar value={result.score} /></div>
        <p className="mt-4 text-slate-700">{result.overall_feedback}</p>
        <p className="mt-1 text-xs text-slate-400">Evaluated by: {result.evaluated_by}</p>
      </div>

      {(result.strengths.length > 0 || result.improvements.length > 0) && (
        <div className="grid sm:grid-cols-2 gap-4">
          <List title="Strengths" items={result.strengths} tone="text-emerald-700" />
          <List title="To improve" items={result.improvements} tone="text-rose-700" />
        </div>
      )}

      <div className="card space-y-4">
        <h2 className="font-semibold text-lg">Question-by-question feedback</h2>
        {result.per_question.map((q, i) => (
          <div key={i} className="border-t border-slate-100 pt-4 first:border-0 first:pt-0">
            <div className="flex justify-between gap-3">
              <p className="font-medium">{i + 1}. {q.question}</p>
              <ScoreBadge score={q.score} />
            </div>
            <p className="mt-2 text-sm text-slate-600 whitespace-pre-wrap">{q.answer}</p>
            <p className="mt-2 text-sm text-indigo-700">💡 {q.feedback}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function List({ title, items, tone }) {
  return (
    <div className="card">
      <h3 className={`font-semibold mb-2 ${tone}`}>{title}</h3>
      {items.length === 0 ? <p className="text-sm text-slate-400">—</p> : (
        <ul className="list-disc pl-5 space-y-1 text-sm text-slate-700">{items.map((s, i) => <li key={i}>{s}</li>)}</ul>
      )}
    </div>
  );
}
