export function ScoreBadge({ score }) {
  if (score === null || score === undefined) return <span className="text-slate-400 text-sm">—</span>;
  const color = score >= 70 ? "bg-emerald-100 text-emerald-700" : score >= 45 ? "bg-amber-100 text-amber-700" : "bg-rose-100 text-rose-700";
  return <span className={`chip ${color}`}>{Number(score).toFixed(1)}%</span>;
}

const STATUS_COLORS = {
  applied: "bg-slate-100 text-slate-700",
  interviewed: "bg-blue-100 text-blue-700",
  shortlisted: "bg-emerald-100 text-emerald-700",
  rejected: "bg-rose-100 text-rose-700",
  hired: "bg-indigo-100 text-indigo-700",
};
export function StatusBadge({ status }) {
  return <span className={`chip ${STATUS_COLORS[status] || STATUS_COLORS.applied}`}>{status}</span>;
}

export function Skills({ items, tone = "indigo" }) {
  if (!items?.length) return <span className="text-slate-400 text-sm">None</span>;
  const cls = tone === "red" ? "bg-rose-50 text-rose-700" : tone === "green" ? "bg-emerald-50 text-emerald-700" : "bg-indigo-50 text-indigo-700";
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((s) => <span key={s} className={`chip ${cls}`}>{s}</span>)}
    </div>
  );
}

export function ErrorBox({ message }) {
  if (!message) return null;
  return <div className="rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-sm px-3 py-2">{message}</div>;
}

export function ProgressBar({ value }) {
  const v = Math.max(0, Math.min(100, value || 0));
  const color = v >= 70 ? "bg-emerald-500" : v >= 45 ? "bg-amber-500" : "bg-rose-500";
  return (
    <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
      <div className={`h-full ${color}`} style={{ width: `${v}%` }} />
    </div>
  );
}
