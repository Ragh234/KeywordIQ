import { Trash2 } from "lucide-react";

export default function ReportCard({ report, onClick, onDelete }) {
    const date = new Date(report.createdAt).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
    });

    return (
        <div className="glass-card glass-card-hover group overflow-hidden">
            <div className="flex">
                {/* Accent bar */}
                <div className="w-1 bg-gradient-to-b from-indigo-500 to-violet-600 shrink-0 rounded-l-2xl" />

                <div className="flex-1 flex items-start justify-between p-4">
                    <button
                        onClick={onClick}
                        className="text-left flex-1 cursor-pointer"
                    >
                        <h3 className="text-sm font-semibold text-white capitalize group-hover:text-indigo-300 transition-colors">
                            {report.keyword}
                        </h3>
                        <div className="flex gap-3 mt-1 text-xs text-slate-400">
                            <span>{date}</span>
                            <span>
                                {report.totalProducts || 0} products
                            </span>
                        </div>
                    </button>
                    {onDelete && (
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onDelete(report._id);
                            }}
                            className="text-slate-500 hover:text-red-400 transition-colors ml-2 p-1 rounded-lg hover:bg-red-500/10 cursor-pointer"
                            title="Delete report"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
