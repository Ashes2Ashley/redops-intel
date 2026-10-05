#!/usr/bin/env python3
"""Fee outlier finder - amount,fee per line. Tags: forensics.
Usage: python3 fee_outliers.py fees.csv"""
import csv, sys
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: fee_outliers.py fees.csv")
    rows = []
    for row in csv.reader(open(sys.argv[1])):
        try:
            a, f = float(row[0]), float(row[1])
            if a > 0:
                rows.append((a, f, f / a * 100))
        except (ValueError, IndexError):
            pass
    avg = sum(r[2] for r in rows) / len(rows)
    print("avg fee: %.3f%% over %d rows" % (avg, len(rows)))
    for a, f, p in rows:
        if p > avg * 2:
            print("FLAG %.0f,%.0f -> %.3f%%" % (a, f, p))
if __name__ == "__main__":
    main()
