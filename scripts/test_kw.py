"""Manual probe: print the top keywords from the most recently saved report.

Run from anywhere:
    python scripts/test_kw.py
"""
import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)


def main():
    output_dir = os.path.join(PROJECT_ROOT, "output")
    if not os.path.isdir(output_dir):
        print(f"No output directory at {output_dir}. Run the CLI or API first to generate a report.")
        return

    files = [f for f in os.listdir(output_dir) if f.startswith("report_") and f.endswith(".json")]
    files.sort(reverse=True)
    if not files:
        print("No reports found.")
        return

    latest_report = os.path.join(output_dir, files[0])
    print(f"Loading {latest_report}...")

    with open(latest_report, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Metadata: {data.get('metadata')}")
    print("Top keywords in file:")
    for kw in data.get("top_keywords", [])[:10]:
        print(f"  - {kw['keyword']}: freq={kw['frequency']}, imp={kw['importance']}")


if __name__ == "__main__":
    main()
