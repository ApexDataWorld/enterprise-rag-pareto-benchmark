"""Small YAML reader for the repository's deterministic benchmark configs."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "None"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [_parse_scalar(part.strip()) for part in inner.split(",")]
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value.strip("\"'")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load the simple YAML subset used by configs/default.yaml.

    PyYAML is intentionally not required so CI and the paper artifact can run
    in a clean Python environment.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    root: dict[str, Any] = {}
    current_key: str | None = None
    current_item: dict[str, Any] | None = None

    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()

        if indent == 0:
            key, _, value = line.partition(":")
            if value.strip():
                root[key] = _parse_scalar(value)
                current_key = None
            else:
                current_key = key
                root[current_key] = []
                current_item = None
        elif indent == 2 and line.startswith("- "):
            if current_key is None:
                raise ValueError(f"List item without parent key near: {raw}")
            key, _, value = line[2:].partition(":")
            current_item = {key: _parse_scalar(value)}
            root[current_key].append(current_item)
        elif indent == 2 and current_key:
            key, _, value = line.partition(":")
            if root[current_key] == []:
                root[current_key] = {}
            if isinstance(root[current_key], list):
                raise ValueError(f"Mapping entry under list key near: {raw}")
            root[current_key][key] = _parse_scalar(value)
        elif indent == 4 and current_item is not None:
            key, _, value = line.partition(":")
            current_item[key] = _parse_scalar(value)
        elif indent == 4 and current_key and isinstance(root[current_key], dict):
            key, _, value = line.partition(":")
            root[current_key][key] = _parse_scalar(value)
        else:
            raise ValueError(f"Unsupported config syntax near: {raw}")

    return root
