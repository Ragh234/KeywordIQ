import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";

export default function Navbar({ title }) {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/auth");
    };

    // Get initials for avatar
    const initials = user?.name
        ? user.name
              .split(" ")
              .map((w) => w[0])
              .join("")
              .toUpperCase()
              .slice(0, 2)
        : "?";

    return (
        <header className="h-14 flex items-center justify-between px-6 bg-[var(--color-surface)] border-b border-white/[0.06]">
            <h1 className="text-base font-semibold text-white">{title}</h1>

            <div className="flex items-center gap-3">
                {/* Avatar */}
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                    <span className="text-xs font-semibold text-white">
                        {initials}
                    </span>
                </div>
                <span className="text-sm text-slate-300 hidden sm:inline">
                    {user?.name}
                </span>
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-red-400 transition-colors cursor-pointer ml-1"
                    title="Logout"
                >
                    <LogOut className="w-4 h-4" />
                    <span className="hidden sm:inline">Logout</span>
                </button>
            </div>
        </header>
    );
}
