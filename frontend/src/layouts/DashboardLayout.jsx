import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

const pageTitles = {
    "/dashboard": "Dashboard",
    "/keyword-research": "Keyword Research",
    "/history": "History",
    "/settings": "Settings",
};

export default function DashboardLayout() {
    const [collapsed, setCollapsed] = useState(false);
    const location = useLocation();

    // Get title — handle nested routes like /history/:id
    let title = pageTitles[location.pathname] || "Report";
    if (location.pathname.startsWith("/history/") && location.pathname !== "/history") {
        title = "Report View";
    }

    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
            <div className="flex-1 flex flex-col overflow-hidden">
                <Navbar title={title} />
                <main className="flex-1 overflow-y-auto p-6">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
