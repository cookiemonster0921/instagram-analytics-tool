from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from statistics import mean

from .extractors import extract_interactions, extract_post_metrics
from .models import Interaction, PostMetric


def analyze_documents(documents: list[tuple[str, object]]) -> dict:
    interactions = extract_interactions(documents)
    post_metrics = extract_post_metrics(documents)
    return build_summary(interactions, post_metrics, [source for source, _ in documents])


def build_summary(
    interactions: list[Interaction],
    post_metrics: list[PostMetric],
    sources: list[str],
) -> dict:
    account_counts = Counter(interaction.account for interaction in interactions)
    kind_counts = Counter(interaction.kind for interaction in interactions)
    dated = [interaction.timestamp for interaction in interactions if interaction.timestamp]
    monthly_counts: dict[str, int] = defaultdict(int)
    for timestamp in dated:
        monthly_counts[timestamp.strftime("%Y-%m")] += 1

    post_points = [
        {
            "index": metric.index,
            "likes": metric.likes,
            "comments": metric.comments,
            "engagement": metric.likes + metric.comments,
            "owner": metric.owner,
            "date": metric.timestamp.date().isoformat() if metric.timestamp else "",
            "source": metric.source,
        }
        for metric in post_metrics
    ]

    top_accounts = [
        {"account": account, "count": count}
        for account, count in account_counts.most_common(20)
    ]

    return {
        "source_count": len(sources),
        "sources": sources,
        "total_interactions": len(interactions),
        "unique_accounts": len(account_counts),
        "top_account": top_accounts[0] if top_accounts else None,
        "date_range": _date_range(dated),
        "interaction_types": [
            {"kind": kind, "count": count}
            for kind, count in kind_counts.most_common()
        ],
        "top_accounts": top_accounts,
        "monthly_counts": [
            {"month": month, "count": monthly_counts[month]}
            for month in sorted(monthly_counts)
        ],
        "post_metrics": post_points,
        "post_summary": _post_summary(post_metrics),
        "records": [asdict(interaction) for interaction in interactions[:1000]],
    }


def _date_range(dates) -> dict:
    if not dates:
        return {"start": "", "end": ""}
    return {
        "start": min(dates).date().isoformat(),
        "end": max(dates).date().isoformat(),
    }


def _post_summary(metrics: list[PostMetric]) -> dict:
    if not metrics:
        return {
            "count": 0,
            "average_likes": 0,
            "average_comments": 0,
            "average_engagement": 0,
        }

    return {
        "count": len(metrics),
        "average_likes": round(mean(metric.likes for metric in metrics), 2),
        "average_comments": round(mean(metric.comments for metric in metrics), 2),
        "average_engagement": round(
            mean(metric.likes + metric.comments for metric in metrics),
            2,
        ),
    }
