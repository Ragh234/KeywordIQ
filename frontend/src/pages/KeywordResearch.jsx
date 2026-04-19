import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import SearchBar from "../components/SearchBar";
import api from "../utils/api";
import { AlertCircle } from "lucide-react";

export default function KeywordResearch() {
    const [searchParams] = useSearchParams();
    const [keyword, setKeyword] = useState("");
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState("");
    const [saved, setSaved] = useState(false);

    // Auto-trigger from ?q= param
    useEffect(() => {
        const q = searchParams.get("q");
        if (q && q.trim()) {
            setKeyword(q.trim());
            runAnalysis(q.trim());
        }
        // eslint-disable-next-line
    }, []);

    const runAnalysis = async (kw) => {
        if (!kw.trim()) return;
        setLoading(true);
        setError("");
        setResults(null);
        setSaved(false);

        try {
            const res = await api.post("/keyword/analyze", {
                keyword: kw.trim(),
                max_pages: 1,
                top_n: 20,
            });
            setResults(res.data);
        } catch (err) {
            setError(
                err.response?.data?.message ||
                    "Analysis failed. Make sure the Python analysis service is running."
            );
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        runAnalysis(keyword);
    };

    const handleSave = async () => {
        if (!results) return;
        try {
            await api.post("/reports", { keyword, results });
            setSaved(true);
        } catch (err) {
            alert("Failed to save report");
        }
    };

    const handleRerun = () => {
        runAnalysis(keyword);
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
            {/* Search */}
            <div>
                <h2
                    className="text-lg font-bold text-white mb-3"
                    style={{ fontFamily: "Poppins, sans-serif" }}
                >
                    Keyword Research
                </h2>
                <SearchBar
                    value={keyword}
                    onChange={setKeyword}
                    onSubmit={handleSubmit}
                    loading={loading}
                    placeholder="Enter a product keyword — e.g. gaming mouse"
                />
            </div>

            {/* Loading */}
            {loading && (
                <div className="glass-card p-12 text-center">
                    <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                    <p className="text-sm text-slate-400">
                        Analyzing "{keyword}" — scraping Amazon data...
                    </p>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-sm text-red-300 animate-fade-in">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    {error}
                </div>
            )}

            {/* Results */}
            {results && !loading && (
                <div className="space-y-6">
                    {/* Actions */}
                    <div className="flex gap-3">
                        <button
                            onClick={handleSave}
                            disabled={saved}
                            className="px-5 py-2.5 text-sm bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white font-medium rounded-xl transition-all hover:shadow-lg hover:shadow-indigo-500/25 cursor-pointer disabled:cursor-not-allowed"
                        >
                            {saved ? "✓ Saved" : "Save Report"}
                        </button>
                        <button
                            onClick={handleRerun}
                            className="px-5 py-2.5 text-sm border border-white/[0.1] text-white hover:bg-white/[0.05] rounded-xl transition-all cursor-pointer font-medium"
                        >
                            Re-run Search
                        </button>
                    </div>

                    {/* Stats row */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div className="glass-card p-4">
                            <p className="text-xs text-slate-400">Keyword</p>
                            <p className="text-lg font-bold text-white capitalize mt-1">
                                {results.search_keyword}
                            </p>
                        </div>
                        <div className="glass-card p-4">
                            <p className="text-xs text-slate-400">
                                Products Analyzed
                            </p>
                            <p className="text-lg font-bold text-white mt-1">
                                {results.total_products}
                            </p>
                        </div>
                        <div className="glass-card p-4">
                            <p className="text-xs text-slate-400">
                                Price Sweet Spot
                            </p>
                            <p className="text-lg font-bold text-white mt-1">
                                ₹
                                {results.price_sweet_spot?.low?.toLocaleString()}{" "}
                                - ₹
                                {results.price_sweet_spot?.high?.toLocaleString()}
                            </p>
                        </div>
                    </div>

                    {/* Top Keywords */}
                    <div className="glass-card p-5">
                        <h3 className="text-sm font-semibold text-white mb-3">
                            Top Keywords by Relevance
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
                                    {results.top_keywords
                                        ?.slice(0, 15)
                                        .map((kw, i) => (
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
                                                        {kw.importance?.toFixed(
                                                            3
                                                        )}
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

                    {/* Difficulty Table */}
                    {results.difficulty_table?.length > 0 && (
                        <div className="glass-card p-5">
                            <h3 className="text-sm font-semibold text-white mb-3">
                                Difficulty & Density
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
                                        {results.difficulty_table
                                            .slice(0, 10)
                                            .map((row, i) => (
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
                                                                {row.difficulty?.toFixed(
                                                                    0
                                                                )}
                                                            </span>
                                                            <div className="w-12 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                                                                <div
                                                                    className={`h-full rounded-full ${
                                                                        row.difficulty >
                                                                        75
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
                    {results.competitor_gaps?.length > 0 && (
                        <div className="glass-card p-5">
                            <h3 className="text-sm font-semibold text-white mb-3">
                                Competitor Gaps
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {results.competitor_gaps.map((gap, i) => (
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
            )}
        </div>
    );
}
