// The five A9-style factors. `weight` is the key in results.score_weights.
const PARTS = [
    { key: "score_relevance", weight: "relevance", label: "Relevance", color: "bg-indigo-500" },
    { key: "score_velocity", weight: "sales_velocity", label: "Sales", color: "bg-violet-500" },
    { key: "score_satisfaction", weight: "satisfaction", label: "Rating", color: "bg-amber-500" },
    { key: "score_price", weight: "price_comp", label: "Price", color: "bg-emerald-500" },
    { key: "score_rank", weight: "rank_position", label: "Rank", color: "bg-sky-500" },
];

// Scraped URLs are untrusted: only link to http(s).
const isHttpUrl = (url) => /^https?:\/\//i.test(url || "");

function ScoreBar({ product, weights }) {
    return (
        <div className="flex w-28 h-2 bg-white/[0.06] rounded-full overflow-hidden">
            {PARTS.map((part) => {
                const score = product[part.key] ?? 0;
                const share = score * (weights[part.weight] ?? 0);
                return (
                    <div
                        key={part.key}
                        className={part.color}
                        style={{ width: `${share * 100}%` }}
                        title={`${part.label}: ${score.toFixed(2)} × ${Math.round(
                            (weights[part.weight] ?? 0) * 100
                        )}% weight`}
                    />
                );
            })}
        </div>
    );
}

export default function TopProductsTable({ products, weights }) {
    return (
        <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-white">
                Top Products by A9 Score
            </h3>
            <p className="text-xs text-slate-400 mt-1 mb-3">
                An estimated 0–1 score from five weighted factors. It
                approximates how Amazon ranks listings; it is not Amazon's
                actual algorithm.
            </p>

            <div className="flex flex-wrap gap-x-4 gap-y-1 mb-4">
                {PARTS.map((part) => (
                    <span
                        key={part.key}
                        className="inline-flex items-center gap-1.5 text-xs text-slate-400"
                    >
                        <span className={`w-2.5 h-2.5 rounded-sm ${part.color}`} />
                        {part.label} {Math.round((weights[part.weight] ?? 0) * 100)}%
                    </span>
                ))}
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="text-xs text-slate-400 border-b border-white/[0.06]">
                            <th className="pb-2 font-medium">#</th>
                            <th className="pb-2 pl-3 font-medium min-w-[14rem]">Product</th>
                            <th className="pb-2 pl-4 font-medium text-right whitespace-nowrap">Price</th>
                            <th className="pb-2 pl-4 font-medium text-right whitespace-nowrap">Rating</th>
                            <th className="pb-2 pl-4 font-medium text-right whitespace-nowrap">Reviews</th>
                            <th className="pb-2 pl-4 font-medium text-right whitespace-nowrap">Amazon Rank</th>
                            <th className="pb-2 pl-4 font-medium text-right whitespace-nowrap">A9 Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map((p, i) => (
                            <tr
                                key={i}
                                className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors"
                            >
                                <td className="py-2.5 text-slate-500">{i + 1}</td>
                                <td className="py-2.5 pl-3 min-w-[14rem] max-w-xs">
                                    {isHttpUrl(p.product_url) ? (
                                        <a
                                            href={p.product_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-white hover:text-indigo-300 transition-colors line-clamp-2"
                                        >
                                            {p.title}
                                        </a>
                                    ) : (
                                        <span className="text-white line-clamp-2">
                                            {p.title}
                                        </span>
                                    )}
                                </td>
                                <td className="py-2.5 pl-4 text-right text-slate-400 whitespace-nowrap">
                                    {p.price != null
                                        ? `₹${p.price.toLocaleString("en-IN")}`
                                        : "—"}
                                </td>
                                <td className="py-2.5 pl-4 text-right text-slate-400">
                                    {p.rating != null ? p.rating.toFixed(1) : "—"}
                                </td>
                                <td className="py-2.5 pl-4 text-right text-slate-400">
                                    {p.review_count != null
                                        ? p.review_count.toLocaleString("en-IN")
                                        : "—"}
                                </td>
                                <td className="py-2.5 pl-4 text-right text-slate-400">
                                    {p.rank_position}
                                </td>
                                <td className="py-2.5 pl-4">
                                    <div className="flex flex-col items-end gap-1.5">
                                        <span className="px-2.5 py-0.5 bg-indigo-500/15 text-indigo-300 rounded-md text-xs font-mono">
                                            {p.a9_score?.toFixed(3)}
                                        </span>
                                        <ScoreBar product={p} weights={weights} />
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
