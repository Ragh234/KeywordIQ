import SuggestedTitle from "./SuggestedTitle";
import TopProductsTable from "./TopProductsTable";

// Shared by the live Keyword Research page and the saved ReportView page, so
// every section is defined once. Sections hide themselves when their data is
// missing, which keeps reports saved before a section existed working.

function Section({ title, children }) {
    return (
        <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-white mb-3">{title}</h3>
            {children}
        </div>
    );
}

function Table({ headers, children }) {
    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
                <thead>
                    <tr className="text-xs text-slate-400 border-b border-white/[0.06]">
                        {headers.map((h, i) => (
                            <th
                                key={h}
                                className={`pb-2 font-medium ${
                                    i === 0 || h === "Keyword" ? "" : "text-right"
                                }`}
                            >
                                {h}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>{children}</tbody>
            </table>
        </div>
    );
}

const difficultyColor = (d) =>
    d > 75 ? "bg-red-500" : d > 50 ? "bg-amber-500" : "bg-emerald-500";

export default function ReportResults({ results }) {
    const r = results || {};

    return (
        <div className="space-y-6">
            {/* Stats row */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="glass-card p-4">
                    <p className="text-xs text-slate-400">Products Analyzed</p>
                    <p className="text-lg font-bold text-white mt-1">
                        {r.total_products}
                    </p>
                </div>
                <div className="glass-card p-4">
                    <p className="text-xs text-slate-400">Price Sweet Spot</p>
                    <p className="text-lg font-bold text-white mt-1">
                        ₹{r.price_sweet_spot?.low?.toLocaleString()} - ₹
                        {r.price_sweet_spot?.high?.toLocaleString()}
                    </p>
                </div>
                <div className="glass-card p-4">
                    <p className="text-xs text-slate-400">Competitor Gaps</p>
                    <p className="text-lg font-bold text-white mt-1">
                        {r.competitor_gaps?.length || 0}
                    </p>
                </div>
            </div>

            {r.suggested_title?.title && (
                <SuggestedTitle suggestion={r.suggested_title} />
            )}

            {r.top_keywords?.length > 0 && (
                <Section title="Top Keywords">
                    <Table headers={["#", "Keyword", "Score", "Frequency", "Avg Rank"]}>
                        {r.top_keywords.map((kw, i) => (
                            <tr
                                key={i}
                                className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors"
                            >
                                <td className="py-2.5 text-slate-500">{i + 1}</td>
                                <td className="py-2.5 text-white">{kw.keyword}</td>
                                <td className="py-2.5 text-right">
                                    <span className="px-2.5 py-0.5 bg-indigo-500/15 text-indigo-300 rounded-md text-xs font-mono">
                                        {kw.importance?.toFixed(3)}
                                    </span>
                                </td>
                                <td className="py-2.5 text-right text-slate-400">
                                    {kw.frequency}
                                </td>
                                <td className="py-2.5 text-right text-slate-400">
                                    {kw.avg_rank?.toFixed(1)}
                                </td>
                            </tr>
                        ))}
                    </Table>
                </Section>
            )}

            {r.difficulty_table?.length > 0 && (
                <Section title="Difficulty & Density">
                    <Table headers={["Keyword", "Difficulty", "Products"]}>
                        {r.difficulty_table.map((row, i) => (
                            <tr key={i} className="border-b border-white/[0.04]">
                                <td className="py-2.5 text-white">{row.keyword}</td>
                                <td className="py-2.5 text-right">
                                    <div className="flex items-center justify-end gap-2">
                                        <span className="text-slate-400">
                                            {row.difficulty?.toFixed(0)}
                                        </span>
                                        <div className="w-12 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full ${difficultyColor(
                                                    row.difficulty
                                                )}`}
                                                style={{ width: `${row.difficulty}%` }}
                                            />
                                        </div>
                                    </div>
                                </td>
                                <td className="py-2.5 text-right text-slate-400">
                                    {row.product_count}
                                </td>
                            </tr>
                        ))}
                    </Table>
                </Section>
            )}

            {r.top_products?.length > 0 && r.score_weights && (
                <TopProductsTable
                    products={r.top_products}
                    weights={r.score_weights}
                />
            )}

            {r.competitor_gaps?.length > 0 && (
                <Section title="Competitor Gaps">
                    <div className="flex flex-wrap gap-2">
                        {r.competitor_gaps.map((gap, i) => (
                            <span
                                key={i}
                                className="px-3 py-1.5 text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 rounded-lg font-medium"
                            >
                                {gap}
                            </span>
                        ))}
                    </div>
                </Section>
            )}

            {r.title_patterns?.length > 0 && (
                <Section title="Title Patterns: Top 10 vs Rest">
                    <p className="text-xs text-slate-400 -mt-1 mb-3">
                        Share of listings containing each keyword. A large gap
                        means top-ranked listings use it far more often.
                    </p>
                    <Table headers={["Keyword", "In Top 10", "In Rest", "Gap"]}>
                        {r.title_patterns.map((row, i) => (
                            <tr key={i} className="border-b border-white/[0.04]">
                                <td className="py-2.5 text-white">{row.keyword}</td>
                                <td className="py-2.5 text-right text-slate-400">
                                    {row.top_pct?.toFixed(0)}%
                                </td>
                                <td className="py-2.5 text-right text-slate-400">
                                    {row.bottom_pct?.toFixed(0)}%
                                </td>
                                <td
                                    className={`py-2.5 text-right font-mono text-xs ${
                                        row.gap > 0 ? "text-emerald-300" : "text-slate-500"
                                    }`}
                                >
                                    {row.gap > 0 ? "+" : ""}
                                    {row.gap?.toFixed(0)}
                                </td>
                            </tr>
                        ))}
                    </Table>
                </Section>
            )}
        </div>
    );
}
