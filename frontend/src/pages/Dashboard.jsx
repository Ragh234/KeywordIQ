import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import DashboardCards from "../components/DashboardCards";
import SearchBar from "../components/SearchBar";
import ReportCard from "../components/ReportCard";
import api from "../utils/api";
import { Search, ArrowRight } from "lucide-react";

export default function Dashboard() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [keyword, setKeyword] = useState("");
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = async () => {
        try {
            const res = await api.get("/reports");
            setReports(res.data);
        } catch (err) {
            console.error("Failed to fetch reports:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        if (keyword.trim()) {
            navigate(`/keyword-research?q=${encodeURIComponent(keyword.trim())}`);
        }
    };

    const recentReports = reports.slice(0, 5);

    const stats = {
        totalReports: reports.length,
        totalKeywords: new Set(reports.map((r) => r.keyword)).size,
        lastAnalysis: reports[0]
            ? new Date(reports[0].createdAt).toLocaleDateString("en-IN", {
                  day: "numeric",
                  month: "short",
              })
            : "Never",
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
            {/* Welcome */}
            <div>
                <h2
                    className="text-xl font-bold text-white"
                    style={{ fontFamily: "Poppins, sans-serif" }}
                >
                    Welcome back, {user?.name} 👋
                </h2>
                <p className="text-sm text-slate-400 mt-1">
                    Here's an overview of your keyword research activity.
                </p>
            </div>

            {/* Stats */}
            <DashboardCards stats={stats} />

            {/* Quick Search */}
            <div className="glass-card p-5">
                <h3 className="text-sm font-semibold text-white mb-3">
                    Quick Search
                </h3>
                <SearchBar
                    value={keyword}
                    onChange={setKeyword}
                    onSubmit={handleSearch}
                    placeholder="Search a keyword — e.g. gaming mouse"
                />
            </div>

            {/* Tool Card */}
            <div
                onClick={() => navigate("/keyword-research")}
                className="glass-card glass-card-hover p-5 cursor-pointer group"
            >
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                        <Search className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-sm font-semibold text-white">
                            Keyword Research Tool
                        </h3>
                        <p className="text-xs text-slate-400">
                            Analyze Amazon keywords, competitor gaps, and
                            pricing insights
                        </p>
                    </div>
                    <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all" />
                </div>
            </div>

            {/* Recent Searches */}
            <div>
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-white">
                        Recent Searches
                    </h3>
                    {reports.length > 0 && (
                        <button
                            onClick={() => navigate("/history")}
                            className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
                        >
                            View all →
                        </button>
                    )}
                </div>

                {loading ? (
                    <div className="flex items-center justify-center py-8">
                        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                ) : recentReports.length > 0 ? (
                    <div className="space-y-2">
                        {recentReports.map((r) => (
                            <ReportCard
                                key={r._id}
                                report={r}
                                onClick={() => navigate(`/history/${r._id}`)}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="glass-card p-8 text-center">
                        <Search className="w-8 h-8 text-slate-500 mx-auto mb-3" />
                        <p className="text-sm text-slate-400">
                            No searches yet. Run your first keyword analysis!
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
