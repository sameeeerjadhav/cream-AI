"""Command-line interface for exploring UdyamSathi MSME records."""

import argparse
import json
from pathlib import Path
from pprint import pprint

from app.records import count_by, get_by_id, load_records, search


def _render_ascii_table(records: list[dict]) -> None:
    """Render a clean tabular view of scheme records."""
    headers = ("ID", "Scheme Name", "Max Cost", "General Subsidy")
    col_widths = (25, 45, 30, 25)

    def row_str(cells: tuple) -> str:
        return " | ".join(
            str(c)[:w].ljust(w) for c, w in zip(cells, col_widths, strict=False)
        )

    separator = "-+-".join("-" * w for w in col_widths)

    print("=" * len(separator))
    print(row_str(headers))
    print(separator)
    for r in records:
        cells = (
            r.get("id", "N/A"),
            r.get("scheme_name", "N/A"),
            r.get("max_project_cost", "N/A"),
            r.get("subsidy_general", "N/A"),
        )
        print(row_str(cells))
    print("=" * len(separator))
    print(f"Total: {len(records)} records listed.\n")


def _render_summary(records: list[dict]) -> None:
    """Print comprehensive statistical summary of the UdyamSathi dataset."""
    categories = count_by(records, "category")
    avg_eligibility_len = sum(len(r.get("eligibility", "")) for r in records) / max(
        1, len(records)
    )

    print("\n=== UdyamSathi Records Dataset Summary ===")
    print(f"Total Records Count: {len(records)}")
    print("Breakdown by Category:")
    for cat, count in sorted(categories.items()):
        print(f"  • {cat.ljust(20)}: {count} records")
    print(f"Average Eligibility Text Length: {avg_eligibility_len:.1f} characters")
    print("Verified Sources: Bank of Maharashtra (PMEGP, CMEGP, MUDRA, Stand-Up India)")
    print("==========================================\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Explore UdyamSathi MSME records")
    parser.add_argument("--search", metavar="KEYWORD", help="search all record fields")
    parser.add_argument(
        "--count", action="store_true", help="count records by category"
    )
    parser.add_argument("--get", metavar="ID", help="get a record by ID")
    parser.add_argument(
        "--table", action="store_true", help="render records in formatted ASCII table"
    )
    parser.add_argument(
        "--summary", action="store_true", help="display statistical dataset summary"
    )
    parser.add_argument(
        "--category",
        metavar="CAT",
        help="filter records by category (scheme, msme-limit-2025, pmegp-sub-rule)",
    )
    parser.add_argument(
        "--export", metavar="FILE", help="export records to a formatted JSON file"
    )
    args = parser.parse_args()

    records = load_records()

    if args.summary:
        _render_summary(records)
    elif args.table:
        _render_ascii_table(records)
    elif args.category:
        filtered = [
            r
            for r in records
            if r.get("category", "").casefold() == args.category.casefold()
        ]
        pprint(filtered)
    elif args.export:
        out_path = Path(args.export)
        out_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        print(f"Successfully exported {len(records)} records to {out_path}")
    elif args.search:
        pprint(search(records, args.search))
    elif args.count:
        pprint(count_by(records))
    elif args.get:
        result = get_by_id(records, args.get)
        if result is None:
            parser.error(f"record not found: {args.get}")
        pprint(result)
    else:
        pprint(records)


if __name__ == "__main__":
    main()
