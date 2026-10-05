#!/usr/bin/env python3
"""Withdrawal delay analyzer - request_date,paid_date,amount per line. Tags: forensics.
Usage: python3 withdrawal_delays.py delays.csv"""
import csv, statistics, sys
from datetime import date
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: withdrawal_delays.py delays.csv")
    delays = []
    for row in csv.reader(open(sys.argv[1])):
        if len(row) < 2:
            continue
        try:
            d = (date.fromisoformat(row[1].strip()) - date.fromisoformat(row[0].strip())).days
            delays.append((d, ",".join(row)))
        except ValueError:
            pass
    ds = [d for d, _ in delays]
    print("count: %d  avg: %.1fd  median: %.1fd  max: %dd"
          % (len(ds), sum(ds) / len(ds), statistics.median(ds), max(ds)))
    slow = [(d, r) for d, r in delays if d > 7]
    print("over 7 days: %d" % len(slow))
    for d, r in slow:
        print("  %dd  %s" % (d, r))
if __name__ == "__main__":
    main()
