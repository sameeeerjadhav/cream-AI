"""Print three pandas facts about the UdyamSathi records."""

import json
from pathlib import Path

import pandas as pd


def main() -> None:
    records = json.loads(Path("data/records.json").read_text(encoding="utf-8"))
    frame = pd.DataFrame(records)
    print(f"Records: {len(frame)}")
    print(f"Columns: {', '.join(frame.columns)}")
    print(f"Average eligibility length: {frame['eligibility'].str.len().mean():.1f}")


if __name__ == "__main__":
    main()
