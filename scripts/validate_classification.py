"""
Checks the classification tables before the tracker runs. Exits with an error when a table is
malformed, so a bad edit stops the daily job instead of silently changing the index.

Usage (from the repo root):
  python scripts/validate_classification.py
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.classification import load_tables, validate_tables


def main():
    tables = load_tables()
    errors = validate_tables(*tables)
    subcats, rules, overrides, queue = tables
    print(f"subcategory_ccif: {len(subcats)} rows | mixed rules: {len(rules)} | "
          f"overrides: {len(overrides)} | review queue: {(queue.status == 'provisional').sum()} pending")
    if errors:
        print(f"\n{len(errors)} classification table error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("Classification tables OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
