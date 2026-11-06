# Command-line interface for exploring sample MSME records.

import argparse
from pprint import pprint

from app.records import count_by, get_by_id, load_records, search


def main() -> None:
    parser = argparse.ArgumentParser(description="Explore UdyamSathi MSME records")
    parser.add_argument("--search", metavar="KEYWORD", help="search all record fields")
    parser.add_argument("--count", action="store_true", help="count records by category")
    parser.add_argument("--get", metavar="ID", help="get a record by ID")
    args = parser.parse_args()

    records = load_records()
    if args.search:
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
