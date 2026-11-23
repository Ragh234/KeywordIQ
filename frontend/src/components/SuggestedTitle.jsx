import { useRef, useState } from "react";
import { Check, Copy } from "lucide-react";

// Editable, rule-based listing title built from the report's keywords.
export default function SuggestedTitle({ suggestion }) {
    const [title, setTitle] = useState(suggestion.title);
    const [copied, setCopied] = useState(false);
    const inputRef = useRef(null);

    const max = suggestion.max_length;
    const tooLong = title.length > max;

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(title);
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
        } catch {
            // Clipboard blocked: select the text so Ctrl+C works.
            inputRef.current?.select();
        }
    };

    return (
        <div className="glass-card p-5">
            <div className="flex items-start justify-between gap-4 mb-3">
                <div>
                    <h3 className="text-sm font-semibold text-white">
                        Suggested Listing Title
                    </h3>
                    <p className="text-xs text-slate-400 mt-1">
                        Built from the top and competitor-gap keywords. Edit it:
                        add your own brand and remove any competitor brand names
                        that slipped in.
                    </p>
                </div>
                <button
                    onClick={handleCopy}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs border border-white/[0.1] text-white hover:bg-white/[0.05] rounded-xl transition-all cursor-pointer font-medium shrink-0"
                >
                    {copied ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                        <Copy className="w-3.5 h-3.5" />
                    )}
                    {copied ? "Copied" : "Copy"}
                </button>
            </div>

            <textarea
                ref={inputRef}
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                rows={5}
                aria-label="Suggested listing title"
                className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white resize-none focus:outline-none focus:border-indigo-500/50"
            />

            <p
                className={`text-xs mt-2 text-right ${
                    tooLong ? "text-red-400" : "text-slate-400"
                }`}
            >
                {title.length} / {max} characters
                {tooLong && " — over Amazon's limit"}
            </p>
        </div>
    );
}
