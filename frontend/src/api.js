const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const getToken = () => localStorage.getItem("token");
export const setToken = (t) => (t ? localStorage.setItem("token", t) : localStorage.removeItem("token"));

async function request(path, { method = "GET", body, form, file } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let payload;
  if (file) {
    payload = new FormData();
    payload.append("file", file);
  } else if (form) {
    payload = new URLSearchParams(form);
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  const res = await fetch(`${API}${path}`, { method, headers, body: payload });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.map((d) => d.msg).join(", ") : data.detail;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return data;
}

export const api = {
  register: (data) => request("/auth/register", { method: "POST", body: data }),
  login: (email, password) => request("/auth/login", { method: "POST", form: { username: email, password } }),
  me: () => request("/auth/me"),

  jobs: () => request("/jobs"),
  createJob: (data) => request("/jobs", { method: "POST", body: data }),
  ranking: (jobId) => request(`/jobs/${jobId}/ranking`),

  uploadResume: (file) => request("/resumes/upload", { method: "POST", file }),
  myResumes: () => request("/resumes/me"),
  matches: (resumeId) => request(`/resumes/${resumeId}/matches`),

  apply: (jobId, resumeId) => request("/applications", { method: "POST", body: { job_id: jobId, resume_id: resumeId } }),
  myApplications: () => request("/applications/me"),
  application: (id) => request(`/applications/${id}`),
  jobApplications: (jobId) => request(`/applications/job/${jobId}`),
  setStatus: (id, status) => request(`/applications/${id}/status`, { method: "PATCH", body: { status } }),

  startInterview: (applicationId) => request("/interviews/start", { method: "POST", body: { application_id: applicationId, num_questions: 5 } }),
  submitInterview: (id, answers) => request(`/interviews/${id}/submit`, { method: "POST", body: { answers } }),
  interviewResult: (id) => request(`/interviews/${id}/result`),

  stats: () => request("/dashboard/stats"),
};
