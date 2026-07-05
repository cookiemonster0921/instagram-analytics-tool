from __future__ import annotations

from collections.abc import Iterator

from .models import Interaction, PostMetric, timestamp_to_datetime

INTERACTION_KEYS = {
    "likes_media_likes": "post_like",
    "story_activities_story_likes": "story_like",
    "story_activities_emoji_sliders": "story_emoji_slider",
    "story_activities_polls": "story_poll",
    "story_activities_questions": "story_question",
    "comments_media_comments": "comment",
    "connections_followers_and_following": "connection",
}


def extract_interactions(documents: list[tuple[str, object]]) -> list[Interaction]:
    interactions: list[Interaction] = []
    for source, document in documents:
        interactions.extend(_walk_interactions(document, source, None))
    return interactions


def extract_post_metrics(documents: list[tuple[str, object]]) -> list[PostMetric]:
    metrics: list[PostMetric] = []
    for source, document in documents:
        metrics.extend(_walk_post_metrics(document, source))
    return [
        PostMetric(
            index=index + 1,
            likes=metric.likes,
            comments=metric.comments,
            timestamp=metric.timestamp,
            owner=metric.owner,
            source=metric.source,
        )
        for index, metric in enumerate(metrics)
    ]


def _walk_interactions(
    value: object,
    source: str,
    current_kind: str | None,
) -> Iterator[Interaction]:
    if isinstance(value, dict):
        for key, child in value.items():
            kind = INTERACTION_KEYS.get(key, current_kind)
            if isinstance(child, list) and kind:
                for item in child:
                    interaction = _interaction_from_item(item, kind, source)
                    if interaction:
                        yield interaction
            yield from _walk_interactions(child, source, kind)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_interactions(item, source, current_kind)


def _interaction_from_item(item: object, kind: str, source: str) -> Interaction | None:
    if not isinstance(item, dict):
        return None

    account = _clean_account(item.get("title") or item.get("name") or item.get("username"))
    timestamp = timestamp_to_datetime(item.get("timestamp"))

    string_data = item.get("string_list_data")
    if isinstance(string_data, list) and string_data:
        first = string_data[0]
        if isinstance(first, dict):
            account = account or _clean_account(first.get("value"))
            timestamp = timestamp or timestamp_to_datetime(first.get("timestamp"))

    if not account:
        return None

    return Interaction(kind=kind, account=account, timestamp=timestamp, source=source)


def _walk_post_metrics(value: object, source: str) -> Iterator[PostMetric]:
    if isinstance(value, dict):
        likes = value.get("like_count")
        comments = value.get("comment_count")
        if isinstance(likes, int) and isinstance(comments, int):
            owner = ""
            owner_data = value.get("owner")
            if isinstance(owner_data, dict):
                owner = str(owner_data.get("username") or owner_data.get("full_name") or "")
            yield PostMetric(
                index=0,
                likes=likes,
                comments=comments,
                timestamp=timestamp_to_datetime(
                    value.get("taken_at_timestamp") or value.get("timestamp")
                ),
                owner=owner,
                source=source,
            )

        for child in value.values():
            yield from _walk_post_metrics(child, source)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_post_metrics(item, source)


def _clean_account(value: object) -> str:
    if not isinstance(value, str):
        return ""
    stripped = value.strip()
    if not stripped:
        return ""
    return stripped.removeprefix("@")
