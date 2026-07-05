from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzers import analyze_documents
from .charts import bar_chart, line_chart
from .loaders import load_documents
from .reports import markdown_report
from .web import run_server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="instagram-analytics",
        description="Analyze Instagram export JSON files offline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Print JSON summary.")
    analyze_parser.add_argument("paths", nargs="+", help="JSON files or export folders.")

    report_parser = subparsers.add_parser("report", help="Write a Markdown report.")
    report_parser.add_argument("paths", nargs="+", help="JSON files or export folders.")
    report_parser.add_argument(
        "-o",
        "--output",
        default="output/report.md",
        help="Markdown output path.",
    )

    charts_parser = subparsers.add_parser("charts", help="Write SVG charts.")
    charts_parser.add_argument("paths", nargs="+", help="JSON files or export folders.")
    charts_parser.add_argument(
        "-o",
        "--output-dir",
        default="output",
        help="Directory for SVG chart files.",
    )

    web_parser = subparsers.add_parser("web", help="Start the local upload UI.")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=8088)

    args = parser.parse_args(argv)

    if args.command == "web":
        run_server(args.host, args.port)
        return 0

    documents = load_documents(args.paths)
    summary = analyze_documents(documents)

    if args.command == "analyze":
        print(json.dumps(summary, indent=2, default=str))
        return 0

    if args.command == "report":
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown_report(summary), encoding="utf-8")
        print(f"Wrote {output}")
        return 0

    if args.command == "charts":
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "top_accounts.svg").write_text(
            bar_chart(summary["top_accounts"], "account", "count", title="Top accounts"),
            encoding="utf-8",
        )
        (output_dir / "monthly_interactions.svg").write_text(
            line_chart(
                summary["monthly_counts"],
                "month",
                "count",
                title="Interactions over time",
            ),
            encoding="utf-8",
        )
        print(f"Wrote charts to {output_dir}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
