import { useState } from "react";
import { api } from "../api";
import { useAuth } from "../App.jsx";
import { ErrorBox } from "../components/ui.jsx";

export default function Login() {
  const { login } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "candidate" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "register") await api.register(form);
      await login(form.email, form.password);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid md:grid-cols-2 gap-10 items-center mt-6">
      <div>
        <h1 className="text-4xl font-bold text-slate-900 leading-tight">
          Smarter hiring with <span className="text-indigo-600">AI</span>
        </h1>
        <p className="mt-4 text-slate-600">
          Upload a resume, get matched to the right jobs, take an AI interview and get instant feedback.
          HR teams see ranked candidates in one dashboard.
        </p>
        <ol className="mt-6 space-y-2 text-sm text-slate-700">
          {["Register & upload resume", "AI parses skills", "Match with jobs", "AI interview", "Score & ranking", "HR dashboard"].map((s, i) => (
            <li key={s} className="flex items-center gap-3">
              <span className="grid place-items-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold">{i + 1}</span>
              {s}
            </li>
          ))}
        </ol>
      </div>

      <form onSubmit={submit} className="card space-y-4">
        <div className="flex rounded-lg bg-slate-100 p-1">
          {["login", "register"].map((m) => (
            <button type="button" key={m} onClick={() => setMode(m)}
              className={`flex-1 rounded-md py-2 text-sm font-semibold capitalize ${mode === m ? "bg-white shadow text-slate-900" : "text-slate-500"}`}>
              {m}
            </button>
          ))}
        </div>

        {mode === "register" && (
          <>
            <div>
              <label className="label">Full name</label>
              <input className="input" value={form.name} onChange={set("name")} required />
            </div>
            <div>
              <label className="label">I am a</label>
              <select className="input" value={form.role} onChange={set("role")}>
                <option value="candidate">Candidate (looking for a job)</option>
                <option value="hr">HR / Recruiter</option>
              </select>
            </div>
          </>
        )}
        <div>
          <label className="label">Email</label>
          <input className="input" type="email" value={form.email} onChange={set("email")} required />
        </div>
        <div>
          <label className="label">Password</label>
          <input className="input" type="password" value={form.password} onChange={set("password")} required />
        </div>
        <ErrorBox message={error} />
        <button className="btn-primary w-full" disabled={busy}>
          {busy ? "Please wait…" : mode === "login" ? "Login" : "Create account"}
        </button>
      </form>
    </div>
  );
}
