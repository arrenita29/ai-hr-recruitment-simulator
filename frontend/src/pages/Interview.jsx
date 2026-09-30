import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { ErrorBox } from "../components/ui.jsx";

export default function Interview() {
  const { applicationId } = useParams();
  const navigate = useNavigate();
  const [interview, setInterview] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.startInterview(Number(applicationId))
      .then((iv) => {
        setInterview(iv);
        setAnswers(iv.questions.map(() => ""));
      })
      .catch((e) => setError(e.message));
  }, [applicationId]);

  const submit = async () => {
    setBusy(true);
    setError("");
    try {
      await api.submitInterview(interview.id, answers);
      navigate(`/result/${interview.id}`);
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  };

  if (error && !interview) return <div className="card"><ErrorBox message={error} /></div>;
  if (!interview) return <div className="card text-slate-500">Preparing your interview questions…</div>;

  const total = interview.questions.length;
  const words = answers[step].trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">AI Interview</h1>
        <span className="text-sm text-slate-500">Question {step + 1} of {total}</span>
      </div>
      <div className="flex gap-1">
        {interview.questions.map((_, i) => (
          <div key={i} className={`h-1.5 flex-1 rounded-full ${i <= step ? "bg-indigo-600" : "bg-slate-200"}`} />
        ))}
      </div>

      <div className="card space-y-4">
        <p className="text-lg font-medium text-slate-800">{interview.questions[step]}</p>
        <textarea
          className="input min-h-48"
          placeholder="Type your answer… Tip: explain what you did, how you did it, and the result."
          value={answers[step]}
          onChange={(e) => setAnswers(answers.map((a, i) => (i === step ? e.target.value : a)))}
        />
        <div className="text-xs text-slate-500">{words} words {words < 40 && "· aim for 60+ words for a strong answer"}</div>
        <ErrorBox message={error} />
        <div className="flex justify-between">
          <button className="btn-outline" disabled={step === 0} onClick={() => setStep(step - 1)}>Previous</button>
          {step < total - 1 ? (
            <button className="btn-primary" onClick={() => setStep(step + 1)}>Next question</button>
          ) : (
            <button className="btn-primary" disabled={busy || answers.some((a) => !a.trim())} onClick={submit}>
              {busy ? "AI is evaluating…" : "Submit interview"}
            </button>
          )}
        </div>
        {step === total - 1 && answers.some((a) => !a.trim()) && (
          <p className="text-xs text-amber-600">Answer all questions to submit.</p>
        )}
      </div>
    </div>
  );
}
