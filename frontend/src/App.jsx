import { createContext, useContext, useEffect, useState } from "react";
import { Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import { api, getToken, setToken } from "./api";
import Login from "./pages/Login.jsx";
import CandidateHome from "./pages/CandidateHome.jsx";
import Interview from "./pages/Interview.jsx";
import Result from "./pages/Result.jsx";
import HrDashboard from "./pages/HrDashboard.jsx";
import JobDetail from "./pages/JobDetail.jsx";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

function Navbar() {
  const { user, logout } = useAuth();
  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-slate-800">
          <span className="grid place-items-center w-8 h-8 rounded-lg bg-indigo-600 text-white text-sm">AI</span>
          HR Recruitment Simulator
        </Link>
        {user && (
          <div className="flex items-center gap-3 text-sm">
            <span className="hidden sm:inline text-slate-600">
              {user.name} <span className="chip bg-indigo-50 text-indigo-700 ml-1">{user.role}</span>
            </span>
            <button onClick={logout} className="btn-outline">Logout</button>
          </div>
        )}
      </div>
    </header>
  );
}

function Protected({ role, children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!getToken());
  const navigate = useNavigate();

  useEffect(() => {
    if (!getToken()) return;
    api.me().then(setUser).catch(() => setToken(null)).finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const { access_token } = await api.login(email, password);
    setToken(access_token);
    const me = await api.me();
    setUser(me);
    navigate("/");
  };
  const logout = () => {
    setToken(null);
    setUser(null);
    navigate("/login");
  };

  if (loading) return <div className="p-10 text-center text-slate-500">Loading…</div>;

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
          <Route path="/" element={
            <Protected>{user?.role === "hr" ? <HrDashboard /> : <CandidateHome />}</Protected>
          } />
          <Route path="/interview/:applicationId" element={<Protected role="candidate"><Interview /></Protected>} />
          <Route path="/result/:interviewId" element={<Protected><Result /></Protected>} />
          <Route path="/jobs/:jobId" element={<Protected role="hr"><JobDetail /></Protected>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </AuthContext.Provider>
  );
}
