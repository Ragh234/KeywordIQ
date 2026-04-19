import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import { KeyRound } from "lucide-react";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validate(fields, mode) {
    const errors = {};
    if (mode === "signup" && (!fields.name || fields.name.trim().length < 2)) {
        errors.name = "Name must be at least 2 characters";
    }
    if (!fields.email) {
        errors.email = "Email is required";
    } else if (!EMAIL_REGEX.test(fields.email)) {
        errors.email = "Please enter a valid email";
    }
    if (!fields.password) {
        errors.password = "Password is required";
    } else if (fields.password.length < 6) {
        errors.password = "Password must be at least 6 characters";
    }
    return errors;
}

export default function AuthPage() {
    const [mode, setMode] = useState("signin"); // "signin" | "signup"
    const [fields, setFields] = useState({ name: "", email: "", password: "" });
    const [errors, setErrors] = useState({});
    const [touched, setTouched] = useState({});
    const [apiError, setApiError] = useState("");
    const [loading, setLoading] = useState(false);
    const { login, signup } = useAuth();
    const navigate = useNavigate();

    const isSignup = mode === "signup";

    const handleChange = useCallback((field, value) => {
        setFields((prev) => ({ ...prev, [field]: value }));
        setApiError("");
        // Clear error on change
        setErrors((prev) => ({ ...prev, [field]: "" }));
    }, []);

    const handleBlur = useCallback(
        (field) => {
            setTouched((prev) => ({ ...prev, [field]: true }));
            const fieldErrors = validate(fields, mode);
            setErrors((prev) => ({ ...prev, [field]: fieldErrors[field] || "" }));
        },
        [fields, mode]
    );

    const toggleMode = () => {
        setMode((m) => (m === "signin" ? "signup" : "signin"));
        setErrors({});
        setTouched({});
        setApiError("");
    };

    const allErrors = validate(fields, mode);
    const isFormValid = Object.keys(allErrors).length === 0;

    const handleSubmit = async (e) => {
        e.preventDefault();
        // Mark all fields touched
        const allTouched = { email: true, password: true };
        if (isSignup) allTouched.name = true;
        setTouched(allTouched);

        const errs = validate(fields, mode);
        setErrors(errs);
        if (Object.keys(errs).length > 0) return;

        setLoading(true);
        setApiError("");
        try {
            if (isSignup) {
                await signup(fields.name.trim(), fields.email, fields.password);
            } else {
                await login(fields.email, fields.password);
            }
            navigate("/dashboard");
        } catch (err) {
            setApiError(
                err.response?.data?.message ||
                    (isSignup ? "Signup failed" : "Login failed")
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-8 bg-[var(--color-bg)] relative overflow-hidden">
            {/* Background gradient orbs */}
            <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-600/15 blur-[120px] animate-float pointer-events-none" />
            <div className="absolute bottom-[-15%] right-[-10%] w-[400px] h-[400px] rounded-full bg-violet-600/10 blur-[100px] animate-float-delayed pointer-events-none" />

            <div className="w-full max-w-md animate-slide-up">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/25">
                        <KeyRound className="w-6 h-6 text-white" />
                    </div>
                    <h1 className="text-2xl font-bold text-white">
                        {isSignup ? "Create your account" : "Welcome back"}
                    </h1>
                    <p className="text-sm text-slate-400 mt-1">
                        {isSignup
                            ? "Start researching keywords for free"
                            : "Sign in to continue to KeywordIQ"}
                    </p>
                </div>

                {/* Card */}
                <div className="glass-card p-6 sm:p-8">
                    {/* Tab Toggle */}
                    <div className="flex bg-white/[0.04] rounded-xl p-1 mb-6">
                        <button
                            type="button"
                            onClick={() => mode !== "signin" && toggleMode()}
                            className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer ${
                                !isSignup
                                    ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md"
                                    : "text-slate-400 hover:text-slate-200"
                            }`}
                        >
                            Sign In
                        </button>
                        <button
                            type="button"
                            onClick={() => mode !== "signup" && toggleMode()}
                            className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer ${
                                isSignup
                                    ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md"
                                    : "text-slate-400 hover:text-slate-200"
                            }`}
                        >
                            Sign Up
                        </button>
                    </div>

                    {/* API Error */}
                    {apiError && (
                        <div className="mb-4 p-3 text-sm text-red-300 bg-red-500/10 border border-red-500/20 rounded-xl animate-fade-in">
                            {apiError}
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* Name — signup only */}
                        <div
                            className={`transition-all duration-300 overflow-hidden ${
                                isSignup
                                    ? "max-h-24 opacity-100"
                                    : "max-h-0 opacity-0"
                            }`}
                        >
                            <Input
                                id="auth-name"
                                label="Name"
                                placeholder="Your name"
                                value={fields.name}
                                onChange={(e) =>
                                    handleChange("name", e.target.value)
                                }
                                onBlur={() => handleBlur("name")}
                                error={touched.name ? errors.name : ""}
                                autoComplete="name"
                            />
                        </div>

                        <Input
                            id="auth-email"
                            label="Email"
                            type="email"
                            placeholder="you@example.com"
                            value={fields.email}
                            onChange={(e) =>
                                handleChange("email", e.target.value)
                            }
                            onBlur={() => handleBlur("email")}
                            error={touched.email ? errors.email : ""}
                            autoComplete="email"
                        />

                        <Input
                            id="auth-password"
                            label="Password"
                            type="password"
                            placeholder={isSignup ? "Min 6 characters" : "••••••••"}
                            value={fields.password}
                            onChange={(e) =>
                                handleChange("password", e.target.value)
                            }
                            onBlur={() => handleBlur("password")}
                            error={touched.password ? errors.password : ""}
                            autoComplete={
                                isSignup ? "new-password" : "current-password"
                            }
                        />

                        <div className="pt-1">
                            <Button
                                type="submit"
                                loading={loading}
                                disabled={!isFormValid}
                            >
                                {isSignup ? "Create Account" : "Sign In"}
                            </Button>
                        </div>
                    </form>

                    {/* Toggle hint */}
                    <p className="text-center text-sm text-slate-400 mt-5">
                        {isSignup
                            ? "Already have an account? "
                            : "Don't have an account? "}
                        <button
                            type="button"
                            onClick={toggleMode}
                            className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors cursor-pointer"
                        >
                            {isSignup ? "Sign In" : "Sign Up"}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
}
