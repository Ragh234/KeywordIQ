import { NavLink } from "react-router-dom";
import {
    LayoutDashboard,
    Search,
    ClipboardList,
    Settings,
    PanelLeftClose,
    PanelLeft,
    Sparkles,
} from "lucide-react";

const navItems = [
    { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { path: "/keyword-research", label: "Keyword Research", icon: Search },
    { path: "/history", label: "History", icon: ClipboardList },
    { path: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar({ collapsed, setCollapsed }) {
    return (
        <aside
            className={`h-full flex flex-col bg-[var(--color-surface)] border-r border-white/[0.06] transition-all duration-300 ${
                collapsed ? "w-[68px]" : "w-60"
            }`}
        >
            {/* Logo */}
            <div className="flex items-center gap-3 px-4 h-16 border-b border-white/[0.06]">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shrink-0 shadow-md shadow-indigo-500/20">
                    <Sparkles className="w-4 h-4 text-white" />
                </div>
                {!collapsed && (
                    <span
                        className="text-base font-bold text-white whitespace-nowrap"
                        style={{ fontFamily: "Poppins, sans-serif" }}
                    >
                        KeywordIQ
                    </span>
                )}
            </div>

            {/* Nav */}
            <nav className="flex-1 py-3 px-2 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                                isActive
                                    ? "bg-gradient-to-r from-indigo-600/20 to-violet-600/10 text-white"
                                    : "text-slate-400 hover:bg-white/[0.04] hover:text-slate-200"
                            } ${collapsed ? "justify-center" : ""}`
                        }
                    >
                        {({ isActive }) => (
                            <>
                                {/* Active indicator */}
                                {isActive && (
                                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-gradient-to-b from-indigo-400 to-violet-500 rounded-r-full" />
                                )}
                                <item.icon
                                    className={`w-[18px] h-[18px] shrink-0 ${
                                        isActive
                                            ? "text-indigo-400"
                                            : "text-slate-400 group-hover:text-slate-200"
                                    } transition-colors`}
                                />
                                {!collapsed && <span>{item.label}</span>}
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>

            {/* Collapse toggle */}
            <div className="px-2 py-3 border-t border-white/[0.06]">
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-sm text-slate-400 hover:bg-white/[0.04] hover:text-slate-200 transition-all cursor-pointer"
                >
                    {collapsed ? (
                        <PanelLeft className="w-[18px] h-[18px]" />
                    ) : (
                        <>
                            <PanelLeftClose className="w-[18px] h-[18px]" />
                            <span>Collapse</span>
                        </>
                    )}
                </button>
            </div>
        </aside>
    );
}
