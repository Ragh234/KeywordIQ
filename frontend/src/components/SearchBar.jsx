import { Search } from "lucide-react";

export default function SearchBar({
    value,
    onChange,
    onSubmit,
    placeholder,
    loading,
}) {
    return (
        <form onSubmit={onSubmit} className="flex gap-2">
            <div className="relative flex-1">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                    type="text"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={placeholder || "Enter a keyword..."}
                    className="w-full pl-10 pr-4 py-3 bg-white/[0.04] border border-white/[0.08] rounded-xl text-white text-sm placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                />
            </div>
            <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-all hover:shadow-lg hover:shadow-indigo-500/25 cursor-pointer disabled:cursor-not-allowed"
            >
                {loading ? "Analyzing..." : "Analyze"}
            </button>
        </form>
    );
}
