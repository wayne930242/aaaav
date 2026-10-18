#!/usr/bin/env python3
"""Append to and read an aaaav-do decision trail (TSV, one row per decision).

Usage:
  decision_log.py append <log> <decision> <why> <evidence> <result>
  decision_log.py start <log> <run-id>
  decision_log.py tail <log> [count]

Adapted from pstack's show-me-your-work log.sh (MIT, (c) 2026 Lauren Tan).
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HEADER = ("ts", "decision", "why", "evidence", "result")
FORMULA_LEADS = ("=", "+", "-", "@", '"')


def clean(cell: str) -> str:
    """Keep a cell on one line and stop spreadsheets from reading it as a formula."""
    flat = cell.replace("\t", " ").replace("\r", " ").replace("\n", " ")
    return f"'{flat}" if flat.startswith(FORMULA_LEADS) else flat


def append_row(log: Path, cells: list[str]) -> str:
    if len(cells) != len(HEADER) - 1:
        raise ValueError(f"expected {len(HEADER) - 1} cells, got {len(cells)}")
    log.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = "\t".join([ts, *(clean(cell) for cell in cells)]) + "\n"
    data = row if log.exists() and log.stat().st_size > 0 else "\t".join(HEADER) + "\n" + row
    # One O_APPEND write per row, so parallel writers never interleave inside a row.
    fd = os.open(log, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        encoded = data.encode()
        written = os.write(fd, encoded)
        if written != len(encoded):
            raise OSError(f"short write: {written} of {len(encoded)} bytes")
    finally:
        os.close(fd)
    return row


def start_row(log: Path, run_id: str) -> str:
    rows = read_rows(log)
    span = f"{rows[0][0]}..{rows[-1][0]}" if rows else "empty trail"
    return append_row(log, ["start", f"picked up after {len(rows)} earlier rows ({span})", run_id, "open"])


def read_rows(log: Path) -> list[list[str]]:
    if not log.exists():
        return []
    lines = log.read_text().splitlines()
    return [line.split("\t") for line in lines[1:] if line]


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in ("append", "start", "tail"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    command, log, rest = argv[0], Path(argv[1]), argv[2:]
    try:
        if command == "append":
            append_row(log, rest)
        elif command == "start":
            if len(rest) != 1:
                raise ValueError("start takes exactly one run id")
            start_row(log, rest[0])
        else:
            count = int(rest[0]) if rest else 10
            for row in read_rows(log)[-count:]:
                print("\t".join(row))
    except ValueError as error:
        print(f"decision_log: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
