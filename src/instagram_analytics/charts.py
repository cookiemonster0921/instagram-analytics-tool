from __future__ import annotations

import html


def bar_chart(items: list[dict], label_key: str, value_key: str, *, title: str) -> str:
    width = 760
    row_height = 34
    top = 54
    height = max(180, top + row_height * max(1, len(items)) + 24)
    max_value = max([item.get(value_key, 0) for item in items] or [1])
    rows = []

    for index, item in enumerate(items[:12]):
        label = html.escape(str(item.get(label_key, "")))
        value = int(item.get(value_key, 0))
        bar_width = int((width - 230) * value / max_value) if max_value else 0
        y = top + index * row_height
        rows.append(
            f'<text x="18" y="{y + 20}" class="label">{label}</text>'
            f'<rect x="190" y="{y + 5}" width="{bar_width}" height="18" rx="5" />'
            f'<text x="{200 + bar_width}" y="{y + 20}" class="value">{value}</text>'
        )

    return f"""<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">
<style>
svg {{ font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
.title {{ font-size: 18px; font-weight: 700; fill: #222; }}
.label {{ font-size: 13px; fill: #343434; }}
.value {{ font-size: 12px; fill: #6b6b6b; }}
rect {{ fill: #f06449; }}
</style>
<text x="18" y="30" class="title">{html.escape(title)}</text>
{''.join(rows)}
</svg>"""


def line_chart(items: list[dict], label_key: str, value_key: str, *, title: str) -> str:
    width = 760
    height = 260
    pad_left = 48
    pad_top = 50
    chart_width = width - 84
    chart_height = height - 92
    values = [int(item.get(value_key, 0)) for item in items]
    labels = [str(item.get(label_key, "")) for item in items]
    max_value = max(values or [1])

    if not values:
        values = [0]
        labels = [""]

    points = []
    for index, value in enumerate(values):
        x = pad_left + (chart_width * index / max(1, len(values) - 1))
        y = pad_top + chart_height - (chart_height * value / max_value if max_value else 0)
        points.append((x, y))

    point_string = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" />' for x, y in points)
    last_label = html.escape(labels[-1] if labels else "")

    return f"""<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">
<style>
svg {{ font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
.title {{ font-size: 18px; font-weight: 700; fill: #222; }}
.axis {{ stroke: #d8d8d8; stroke-width: 1; }}
.line {{ fill: none; stroke: #1f9d8a; stroke-width: 3; }}
circle {{ fill: #1f9d8a; }}
.caption {{ font-size: 12px; fill: #6b6b6b; }}
</style>
<text x="18" y="30" class="title">{html.escape(title)}</text>
<line x1="{pad_left}" y1="{pad_top + chart_height}" x2="{pad_left + chart_width}" y2="{pad_top + chart_height}" class="axis" />
<line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{pad_top + chart_height}" class="axis" />
<polyline points="{point_string}" class="line" />
{dots}
<text x="{pad_left}" y="{height - 20}" class="caption">First period</text>
<text x="{width - 150}" y="{height - 20}" class="caption">Last: {last_label}</text>
</svg>"""
