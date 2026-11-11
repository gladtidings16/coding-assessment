import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { AppLayout } from "./layouts/AppLayout";
import { LoginPage } from "./features/auth/LoginPage";
import { HomePage } from "./features/home/HomePage";
import { LivePage } from "./features/live/LivePage";

function Protected({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="muted" style={{ padding: 24 }}>Restoring session…</p>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <Protected>
            <AppLayout />
          </Protected>
        }
      >
        <Route index element={<HomePage />} />
        <Route path="live" element={<LivePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
