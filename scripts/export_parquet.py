"""Export every registered dataset (forex_centuries.DATASETS) to Parquet.

Usage: python scripts/export_parquet.py OUT_DIR

Run after build.py; the weekly workflow attaches the files to each release
so `forex_centuries.load(name)` can fetch them.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from forex_centuries.datasets import DATASETS  # noqa: E402

DERIVED = ROOT / "data" / "derived"


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, (rel, _) in DATASETS.items():
        # Text columns where empty means "none", not missing.
        df = pd.read_csv(DERIVED / rel)
        for col in ("flags", "unit"):
            if col in df.columns:
                df[col] = df[col].fillna("")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        if df.columns[0].startswith("Unnamed"):  # correlation matrices
            df = df.rename(columns={df.columns[0]: "country"})
        df.to_parquet(out / f"{name}.parquet", index=False)
        print(f"  {name}.parquet: {len(df):,} rows")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
