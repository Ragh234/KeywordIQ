import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../utils/api";
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

            {/* Stats row */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="glass-card p-4">
                    <p className="text-xs text-slate-400">Products</p>
                    <p className="text-lg font-bold text-white mt-1">
                        {r.total_products}
                    </p>
                </div>
                <div className="glass-card p-4">
                    <p className="text-xs text-slate-400">Price Range</p>
                    <p className="text-lg font-bold text-white mt-1">
                        ₹{r.price_sweet_spot?.low?.toLocaleString()} - ₹
                        {r.price_sweet_spot?.high?.toLocaleString()}
                    </p>
                </div>
                <div className="glass-card p-4">
                    <p className="text-xs text-slate-400">Competitor Gaps</p>
                    <p className="text-lg font-bold text-white mt-1">
                        {r.competitor_gaps?.length || 0}
                    </p>
                </div>
            </div>

            {/* Top Keywords */}
            {r.top_keywords?.length > 0 && (
                <div className="glass-card p-5">
                    <h3 className="text-sm font-semibold text-white mb-3">
                        Top Keywords
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead>
                                <tr className="text-xs text-slate-400 border-b border-white/[0.06]">
                                    <th className="pb-2 font-medium">#</th>
                                    <th className="pb-2 font-medium">
                                        Keyword
                                    </th>
                                    <th className="pb-2 font-medium text-right">
                                        Score
                                    </th>
                                    <th className="pb-2 font-medium text-right">
                                        Frequency
                                    </th>
                                    <th className="pb-2 font-medium text-right">
                                        Avg Rank
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {r.top_keywords.map((kw, i) => (
                                    <tr
                                        key={i}
                                        className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors"
                                    >
                                        <td className="py-2.5 text-slate-500">
                                            {i + 1}
                                        </td>
                                        <td className="py-2.5 text-white">
                                            {kw.keyword}
                                        </td>
                                        <td className="py-2.5 text-right">
                                            <span className="px-2.5 py-0.5 bg-indigo-500/15 text-indigo-300 rounded-md text-xs font-mono">
                                                {kw.importance?.toFixed(3)}
                                            </span>
                                        </td>
                                        <td className="py-2.5 text-right text-slate-400">
                                            {kw.frequency}
                                        </td>
                                        <td className="py-2.5 text-right text-slate-400">
                                            {kw.avg_rank?.toFixed(1)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Difficulty */}
            {r.difficulty_table?.length > 0 && (
                <div className="glass-card p-5">
                    <h3 className="text-sm font-semibold text-white mb-3">
                        Difficulty
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead>
                                <tr className="text-xs text-slate-400 border-b border-white/[0.06]">
                                    <th className="pb-2 font-medium">
                                        Keyword
                                    </th>
                                    <th className="pb-2 font-medium text-right">
                                        Difficulty
                                    </th>
                                    <th className="pb-2 font-medium text-right">
                                        Products
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {r.difficulty_table.map((row, i) => (
                                    <tr
                                        key={i}
                                        className="border-b border-white/[0.04]"
                                    >
                                        <td className="py-2.5 text-white">
                                            {row.keyword}
                                        </td>
                                        <td className="py-2.5 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                <span className="text-slate-400">
                                                    {row.difficulty?.toFixed(0)}
                                                </span>
                                                <div className="w-12 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${
                                                            row.difficulty > 75
                                                                ? "bg-red-500"
                                                                : row.difficulty >
                                                                    50
                                                                  ? "bg-amber-500"
                                                                  : "bg-emerald-500"
                                                        }`}
                                                        style={{
                                                            width: `${row.difficulty}%`,
                                                        }}
                                                    />
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-2.5 text-right text-slate-400">
                                            {row.product_count}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Competitor Gaps */}
            {r.competitor_gaps?.length > 0 && (
                <div className="glass-card p-5">
                    <h3 className="text-sm font-semibold text-white mb-3">
                        Competitor Gaps
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {r.competitor_gaps.map((gap, i) => (
                            <span
                                key={i}
                                className="px-3 py-1.5 text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 rounded-lg font-medium"
                            >
                                {gap}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
