from __future__ import annotations

import hashlib
import json
from pathlib import Path


def main() -> None:
    artifacts = {}
    for path in sorted(Path("results").rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            artifacts[str(path)] = {"sha256": digest, "bytes": path.stat().st_size}
    target = Path("results/run_metadata/final_artifact_manifest.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"artifacts": artifacts}, indent=2), encoding="utf-8")
    md = Path("paper/tables/artifact_manifest.md")
    md.parent.mkdir(parents=True, exist_ok=True)
    lines = ["| Artifact | SHA-256 | Bytes |", "|---|---|---|"]
    for path, meta in artifacts.items():
        lines.append(f"| `{path}` | `{meta['sha256']}` | {meta['bytes']} |")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()

