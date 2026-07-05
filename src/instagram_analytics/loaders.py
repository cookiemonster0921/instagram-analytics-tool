from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def iter_json_files(paths: Iterable[str | Path]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser()
        if path.is_file() and path.suffix.lower() == ".json":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(p for p in path.rglob("*.json") if p.is_file()))
    return sorted(dict.fromkeys(files))


def load_json_file(path: str | Path) -> object:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_json_text(content: str, source: str = "uploaded.json") -> tuple[str, object]:
    try:
        return source, json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{source}: invalid JSON at line {exc.lineno}") from exc


def load_documents(paths: Iterable[str | Path]) -> list[tuple[str, object]]:
    documents: list[tuple[str, object]] = []
    for path in iter_json_files(paths):
        try:
            documents.append((str(path), load_json_file(path)))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not read {path}: {exc}") from exc
    return documents
