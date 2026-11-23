import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../utils/api";
import ReportResults from "../components/ReportResults";
import { ArrowLeft, RefreshCw, Trash2, AlertCircle } from "lucide-react";

export default function ReportView() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchReport();
        // eslint-disable-next-line
    }, [id]);

    const fetchReport = async () => {
        try {
            const res = await api.get(`/reports/${id}`);
            setReport(res.data);
        } catch (err) {
            setError("Report not found");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!confirm("Delete this report?")) return;
        try {
            await api.delete(`/reports/${id}`);
            navigate("/history");
        } catch (err) {
            alert("Failed to delete");
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    if (error || !report) {
        return (
            <div className="text-center py-12 animate-fade-in">
                <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-3" />
                <p className="text-sm text-red-300">{error}</p>
                <button
                    onClick={() => navigate("/history")}
                    className="mt-4 text-sm text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
                >
                    ← Back to History
                </button>
            </div>
        );
    }

    const r = report.results || {};

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <button
                        onClick={() => navigate("/history")}
                        className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors mb-1.5 cursor-pointer"
                    >
                        <ArrowLeft className="w-3.5 h-3.5" />
                        Back to History
                    </button>
                    <h2
                        className="text-xl font-bold text-white capitalize"
                        style={{ fontFamily: "Poppins, sans-serif" }}
                    >
                        {report.keyword}
                    </h2>
                    <p className="text-xs text-slate-400">
                        {new Date(report.createdAt).toLocaleString("en-IN")}
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() =>
                            navigate(
                                `/keyword-research?q=${encodeURIComponent(
                                    report.keyword
                                )}`
                            )
                        }
                        className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs border border-white/[0.1] text-white hover:bg-white/[0.05] rounded-xl transition-all cursor-pointer font-medium"
                    >
                        <RefreshCw className="w-3.5 h-3.5" />
                        Re-run
                    </button>
                    <button
                        onClick={handleDelete}
                        className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs text-red-300 border border-red-500/20 hover:bg-red-500/10 rounded-xl transition-all cursor-pointer font-medium"
                    >
                        <Trash2 className="w-3.5 h-3.5" />
                        Delete
                    </button>
                </div>
            </div>

            <ReportResults results={r} />
        </div>
    );
}
