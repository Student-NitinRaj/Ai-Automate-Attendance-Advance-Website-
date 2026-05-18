"""
view_attendance.py  —  CLI Attendance Viewer
=============================================
Quick terminal view of attendance records.

Usage:
    python view_attendance.py              # show today's records
    python view_attendance.py --all        # show all records
    python view_attendance.py --date 2026-05-15
    python view_attendance.py --name Nitin
"""

import argparse
import os
from datetime import datetime
from attendance_logger import AttendanceLogger


def fmt_table(records):
    if not records:
        return "  (no records)"
    col_w = {
        "Name":   max(len("Name"),   max(len(r["Name"])   for r in records)) + 2,
        "Date":   max(len("Date"),   max(len(r["Date"])   for r in records)) + 2,
        "Time":   max(len("Time"),   max(len(r["Time"])   for r in records)) + 2,
        "Status": max(len("Status"), max(len(r["Status"]) for r in records)) + 2,
    }
    sep  = "+" + "+".join("-" * col_w[c] for c in col_w) + "+"
    head = "|" + "|".join(f" {c:{col_w[c]-2}} " for c in col_w) + "|"
    rows = [sep, head, sep]
    for r in records:
        row = "|" + "|".join(f" {r[c]:{col_w[c]-2}} " for c in col_w) + "|"
        rows.append(row)
    rows.append(sep)
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(
        description="View attendance records",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--all",  action="store_true", help="Show all records")
    parser.add_argument("--date", default=None,        help="Filter by date (YYYY-MM-DD)")
    parser.add_argument("--name", default=None,        help="Filter by name (partial match)")
    args = parser.parse_args()

    logger  = AttendanceLogger()
    today   = datetime.now().strftime("%Y-%m-%d")
    records = logger.get_all_records()

    # Apply filters
    if not args.all and not args.date and not args.name:
        records = [r for r in records if r["Date"] == today]
        title   = f"Today's Attendance ({today})"
    else:
        if args.date:
            records = [r for r in records if r["Date"] == args.date]
            title   = f"Attendance for {args.date}"
        else:
            title = "All Attendance Records"
        if args.name:
            records = [r for r in records if args.name.lower() in r["Name"].lower()]
            title  += f"  (name filter: '{args.name}')"

    print("=" * 55)
    print(f"  {title}")
    print(f"  Total: {len(records)} record(s)")
    print("=" * 55)
    print(fmt_table(records))
    print()


if __name__ == "__main__":
    main()
