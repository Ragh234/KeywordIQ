import { BarChart3, Search, Clock } from "lucide-react";

const iconMap = [BarChart3, Search, Clock];
const gradients = [
    "from-blue-500 to-cyan-400",
    "from-violet-500 to-purple-400",
    "from-amber-500 to-orange-400",
];

export default function DashboardCards({ stats }) {
    const cards = [
        { label: "Total Reports", value: stats.totalReports },
        { label: "Keywords Analyzed", value: stats.totalKeywords },
        { label: "Last Analysis", value: stats.lastAnalysis || "Never" },
    ];

    return (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {cards.map((card, i) => {
                const Icon = iconMap[i];
                return (
                    <div
                        key={i}
                        className="glass-card glass-card-hover p-4 group"
                    >
                        <div className="flex items-center gap-3">
                            <div
                                className={`w-10 h-10 rounded-xl bg-gradient-to-br ${gradients[i]} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}
                            >
                                <Icon className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <p className="text-xs text-slate-400">
                                    {card.label}
                                </p>
                                <p className="text-lg font-bold text-white">
                                    {card.value}
                                </p>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
