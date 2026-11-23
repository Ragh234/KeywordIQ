import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import SearchBar from "../components/SearchBar";
import ReportResults from "../components/ReportResults";
import api from "../utils/api";
import { AlertCircle } from "lucide-react";

export default function KeywordResearch() {
    const [searchParams] = useSearchParams();
    const [keyword, setKeyword] = useState("");
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState("");
    const [saved, setSaved] = useState(false);
    // StrictMode runs effects twice in development, which would scrape Amazon twice.
    const autoRan = useRef(false);

    // Auto-trigger from ?q= param
    useEffect(() => {
        if (autoRan.current) return;
        autoRan.current = true;
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
            await api.post("/reports", {
                keyword: results.search_keyword,
                results,
            });
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

                    <ReportResults results={results} />
                </div>
            )}
        </div>
    );
}
