from pathlib import Path
import shutil


def main() -> None:
    source = Path("results/default/tables/query_type_summary.csv")
    target = Path("results/query_type_analysis.csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"wrote {target}")


if __name__ == "__main__":
    main()

