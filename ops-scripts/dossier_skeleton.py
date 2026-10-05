#!/usr/bin/env python3
"""Dossier skeleton assembler - markdown case file from CLI fields. Tags: reporting.
Usage: python3 dossier_skeleton.py <subject> <confidence>"""
import sys
from datetime import date
def main():
    if len(sys.argv) < 3:
        sys.exit("usage: dossier_skeleton.py <subject> <confidence>")
    subj, conf = sys.argv[1], sys.argv[2].upper()
    print("# Dossier: %s" % subj)
    print("\n- Filed: %s | Callsign: %s | Confidence: %s"
          % (date.today().isoformat(), "{{CALLSIGN}}", conf))
    print("\n## Summary\n")
    print("\n## Evidence\n")
    print("\n## Links\n")
    print("\n## Assessment\n")
if __name__ == "__main__":
    main()
