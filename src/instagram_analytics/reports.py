from __future__ import annotations


def markdown_report(summary: dict) -> str:
    date_range = summary.get("date_range") or {}
    top_account = summary.get("top_account") or {}
    lines = [
        "# Instagram Analytics Report",
        "",
        f"- Files analyzed: {summary.get('source_count', 0)}",
        f"- Total interactions: {summary.get('total_interactions', 0)}",
        f"- Unique accounts: {summary.get('unique_accounts', 0)}",
        f"- Date range: {date_range.get('start', '') or 'unknown'} to {date_range.get('end', '') or 'unknown'}",
        f"- Top account: {top_account.get('account', 'none')} ({top_account.get('count', 0)})",
        "",
        "## Interaction Types",
        "",
    ]

    for row in summary.get("interaction_types", []):
        lines.append(f"- {row['kind']}: {row['count']}")

    lines.extend(["", "## Top Accounts", ""])
    for row in summary.get("top_accounts", [])[:20]:
        lines.append(f"- {row['account']}: {row['count']}")

    post_summary = summary.get("post_summary", {})
    if post_summary.get("count"):
        lines.extend(
            [
                "",
                "## Post Metrics",
                "",
                f"- Posts found: {post_summary['count']}",
                f"- Average likes: {post_summary['average_likes']}",
                f"- Average comments: {post_summary['average_comments']}",
                f"- Average engagement: {post_summary['average_engagement']}",
            ]
        )

    return "\n".join(lines) + "\n"
