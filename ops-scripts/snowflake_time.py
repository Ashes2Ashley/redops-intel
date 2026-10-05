#!/usr/bin/env python3
"""Discord snowflake to UTC timestamp converter. Tags: util.
Usage: python3 snowflake_time.py <snowflake_id> [...]"""
import datetime, sys
EPOCH = 1420070400000
def main():
    for arg in sys.argv[1:]:
        try:
            ts = (int(arg) >> 22) + EPOCH
            dt = datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc)
            print(arg, "->", dt.strftime("%Y-%m-%d %H:%M:%S UTC"))
        except ValueError:
            print(arg, "-> not a snowflake", file=sys.stderr)
if __name__ == "__main__":
    main()
