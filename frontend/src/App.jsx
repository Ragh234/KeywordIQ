import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";

import AuthPage from "./pages/AuthPage";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import KeywordResearch from "./pages/KeywordResearch";
import History from "./pages/History";
import ReportView from "./pages/ReportView";
import Settings from "./pages/Settings";

function App() {
    const { token } = useAuth();

    return (
        <Routes>
            {/* Public routes */}
            <Route
                path="/"
                element={token ? <Navigate to="/dashboard" /> : <Landing />}
            />
            <Route
                path="/auth"
                element={token ? <Navigate to="/dashboard" /> : <AuthPage />}
            />
            {/* Backwards compat redirects */}
            <Route path="/login" element={<Navigate to="/auth" replace />} />
            <Route path="/signup" element={<Navigate to="/auth" replace />} />

            {/* Protected routes — wrapped in DashboardLayout */}
            <Route
                element={
                    <ProtectedRoute>
                        <DashboardLayout />
                    </ProtectedRoute>
                }
            >
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/keyword-research" element={<KeywordResearch />} />
                <Route path="/history" element={<History />} />
                <Route path="/history/:id" element={<ReportView />} />
                <Route path="/settings" element={<Settings />} />
            </Route>

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" />} />
        </Routes>
    );
}

export default App;
