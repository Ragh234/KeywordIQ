import { Link } from "react-router-dom";
import { Search, BarChart3, DollarSign, ArrowRight, Sparkles } from "lucide-react";

const features = [
    {
        icon: Search,
        title: "Keyword Research",
        desc: "TF-IDF powered analysis with Amazon A9 data",
        gradient: "from-blue-500 to-cyan-400",
    },
    {
        icon: BarChart3,
        title: "Competitor Gaps",
        desc: "Discover untargeted high-value search terms",
        gradient: "from-violet-500 to-purple-400",
    },
    {
        icon: DollarSign,
        title: "Price Insights",
        desc: "Find sweet-spot pricing for maximum conversions",
        gradient: "from-emerald-500 to-teal-400",
    },
];

export default function Landing() {
    return (
        <div className="min-h-screen bg-[var(--color-bg)] flex flex-col relative overflow-hidden">
            {/* Background orbs */}
            <div className="absolute top-[-20%] left-[20%] w-[600px] h-[600px] rounded-full bg-indigo-600/10 blur-[140px] animate-float pointer-events-none" />
            <div className="absolute bottom-[-10%] right-[10%] w-[500px] h-[500px] rounded-full bg-violet-600/8 blur-[120px] animate-float-delayed pointer-events-none" />

            {/* Navbar */}
            <nav className="relative z-10 flex items-center justify-between px-6 md:px-10 py-4">
                <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                        <Sparkles className="w-4.5 h-4.5 text-white" />
                    </div>
                    <span className="text-lg font-bold text-white" style={{ fontFamily: "Poppins, sans-serif" }}>
                        KeywordIQ
                    </span>
                </div>
                <div className="flex items-center gap-3">
                    <Link
                        to="/auth"
                        className="px-4 py-2 text-sm text-slate-300 hover:text-white transition-colors"
                    >
                        Sign In
                    </Link>
                    <Link
                        to="/auth"
                        className="px-5 py-2.5 text-sm bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-medium rounded-xl transition-all hover:shadow-lg hover:shadow-indigo-500/25"
                    >
                        Get Started
                    </Link>
                </div>
            </nav>

            {/* Hero */}
            <div className="relative z-10 flex-1 flex items-center justify-center px-6">
                <div className="max-w-2xl text-center animate-slide-up">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium mb-6">
                        <Sparkles className="w-3.5 h-3.5" />
                        Powered by TF-IDF & Amazon A9
                    </div>

                    <h1
                        className="text-4xl md:text-6xl font-bold text-white mb-5 leading-tight tracking-tight"
                        style={{ fontFamily: "Poppins, sans-serif" }}
                    >
                        Amazon Keyword Research
                        <br />
                        <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                            Made Simple
                        </span>
                    </h1>

                    <p className="text-lg text-slate-400 mb-10 max-w-xl mx-auto leading-relaxed">
                        Discover high-value keywords, analyze competitor gaps,
                        find pricing sweet spots, and optimize your Amazon
                        listings with real A9 data.
                    </p>

                    <div className="flex items-center justify-center gap-4">
                        <Link
                            to="/auth"
                            className="group inline-flex items-center gap-2 px-7 py-3.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold rounded-xl transition-all hover:shadow-xl hover:shadow-indigo-500/25"
                        >
                            Get Started Free
                            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                        </Link>
                        <Link
                            to="/auth"
                            className="px-7 py-3.5 border border-white/[0.1] text-white hover:bg-white/[0.05] rounded-xl transition-all font-medium"
                        >
                            Sign In
                        </Link>
                    </div>

                    {/* Features */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-20">
                        {features.map((f, i) => (
                            <div
                                key={i}
                                className="glass-card glass-card-hover p-5 text-left group cursor-default"
                            >
                                <div
                                    className={`w-10 h-10 rounded-xl bg-gradient-to-br ${f.gradient} flex items-center justify-center mb-3 shadow-lg group-hover:scale-110 transition-transform`}
                                >
                                    <f.icon className="w-5 h-5 text-white" />
                                </div>
                                <h3 className="text-sm font-semibold text-white mb-1">
                                    {f.title}
                                </h3>
                                <p className="text-xs text-slate-400 leading-relaxed">
                                    {f.desc}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Footer spacer */}
            <div className="h-12" />
        </div>
    );
}
