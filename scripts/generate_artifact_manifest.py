from __future__ import annotations

import hashlib
import json
from pathlib import Path


def main() -> None:
    artifacts = {}
    for path in sorted(Path("results").rglob("*")):
        if path.is_file() and path.name != ".DS_Store":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            artifacts[str(path)] = {"sha256": digest, "bytes": path.stat().st_size}
    target = Path("results/run_metadata/final_artifact_manifest.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"artifacts": artifacts}, indent=2), encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
