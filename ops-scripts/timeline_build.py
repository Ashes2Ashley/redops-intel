#!/usr/bin/env python3
"""Timeline builder - date,event CSV lines to markdown timeline. Tags: reporting.
Usage: python3 timeline_build.py events.csv"""
import csv, sys
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: timeline_build.py events.csv")
    rows = sorted(csv.reader(open(sys.argv[1])))
    print("# Timeline - %s" % "{{CALLSIGN}}")
    for r in rows:
        if len(r) >= 2:
            print("- **%s** - %s" % (r[0].strip(), r[1].strip()))
if __name__ == "__main__":
    main()
