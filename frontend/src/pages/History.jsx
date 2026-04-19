import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ReportCard from "../components/ReportCard";
import api from "../utils/api";
import { Search } from "lucide-react";

export default function History() {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

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

    const handleDelete = async (id) => {
        if (!confirm("Delete this report?")) return;
        try {
            await api.delete(`/reports/${id}`);
            setReports((prev) => prev.filter((r) => r._id !== id));
        } catch (err) {
            alert("Failed to delete report");
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto animate-fade-in">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2
                        className="text-lg font-bold text-white"
                        style={{ fontFamily: "Poppins, sans-serif" }}
                    >
                        Report History
                    </h2>
                    <p className="text-sm text-slate-400">
                        {reports.length} saved report
                        {reports.length !== 1 ? "s" : ""}
                    </p>
                </div>
            </div>

            {reports.length === 0 ? (
                <div className="glass-card p-12 text-center">
                    <Search className="w-10 h-10 text-slate-500 mx-auto mb-3" />
                    <p className="text-sm text-slate-400 mb-4">
                        No reports saved yet.
                    </p>
                    <button
                        onClick={() => navigate("/keyword-research")}
                        className="px-5 py-2.5 text-sm bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-medium rounded-xl transition-all hover:shadow-lg hover:shadow-indigo-500/25 cursor-pointer"
                    >
                        Run First Analysis
                    </button>
                </div>
            ) : (
                <div className="space-y-2">
                    {reports.map((r) => (
                        <ReportCard
                            key={r._id}
                            report={r}
                            onClick={() => navigate(`/history/${r._id}`)}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
