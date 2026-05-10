"""Command line interface."""

from __future__ import annotations

import argparse

from .config import load_config
from .pipeline import run_benchmark


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="rag-pareto")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="run the benchmark")
    run_parser.add_argument("--config", default="configs/default.yaml")
    run_parser.add_argument("--output-dir", default=None)
    args = parser.parse_args(argv)

    if args.command == "run":
        config = load_config(args.config)
        artifacts = run_benchmark(config, output_dir_override=args.output_dir)
        print(f"wrote benchmark artifacts to {artifacts['output_dir']}")


if __name__ == "__main__":
    main()

