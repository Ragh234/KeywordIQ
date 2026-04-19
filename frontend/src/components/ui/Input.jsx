import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

export default function Input({
    label,
    type = "text",
    error,
    id,
    className = "",
    ...props
}) {
    const [showPassword, setShowPassword] = useState(false);
    const isPassword = type === "password";
    const inputType = isPassword && showPassword ? "text" : type;

    return (
        <div className={className}>
            {label && (
                <label
                    htmlFor={id}
                    className="block text-sm font-medium text-slate-300 mb-1.5"
                >
                    {label}
                </label>
            )}
            <div className="relative">
                <input
                    id={id}
                    type={inputType}
                    className={`w-full px-4 py-3 bg-white/[0.06] border rounded-xl text-white text-sm placeholder:text-slate-500 outline-none transition-all duration-200 ${
                        error
                            ? "border-red-500/60 focus:border-red-400 focus:ring-2 focus:ring-red-500/20"
                            : "border-white/[0.08] focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20"
                    } ${isPassword ? "pr-11" : ""}`}
                    {...props}
                />
                {isPassword && (
                    <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 transition-colors"
                        tabIndex={-1}
                        aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                        {showPassword ? (
                            <EyeOff className="w-4.5 h-4.5" />
                        ) : (
                            <Eye className="w-4.5 h-4.5" />
                        )}
                    </button>
                )}
            </div>
            {error && (
                <p className="mt-1.5 text-xs text-red-400 animate-fade-in">
                    {error}
                </p>
            )}
        </div>
    );
}
