import { Loader2 } from "lucide-react";

export default function Button({
    children,
    variant = "primary",
    loading = false,
    disabled = false,
    className = "",
    ...props
}) {
    const base =
        "w-full py-3 px-4 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed";

    const variants = {
        primary:
            "bg-gradient-to-r from-indigo-600 to-violet-600 text-white hover:from-indigo-500 hover:to-violet-500 hover:shadow-lg hover:shadow-indigo-500/25 active:scale-[0.98] disabled:opacity-50 disabled:hover:shadow-none disabled:active:scale-100",
        secondary:
            "bg-white/[0.06] border border-white/[0.1] text-slate-200 hover:bg-white/[0.1] hover:border-white/[0.15] active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100",
    };

    return (
        <button
            className={`${base} ${variants[variant]} ${className}`}
            disabled={disabled || loading}
            {...props}
        >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {children}
        </button>
    );
}
