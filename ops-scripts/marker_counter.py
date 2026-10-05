#!/usr/bin/env python3
"""Keyword marker counter - fear/greed/despair signals in chat text. Tags: forensics.
Usage: python3 marker_counter.py chat.txt"""
import re, sys
MARKERS = {"fear": ["afraid", "scared", "worried", "anxious", "panic", "dread"],
           "anger": ["angry", "furious", "rage", "hate"],
           "greed": ["profit", "lambo", "moon", "pump"],
           "despair": ["lost everything", "broke", "ruined", "scam", "rigged", "stolen"],
           "sunk_cost": ["already put in", "too deep", "all in", "no choice"]}
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: marker_counter.py chat.txt")
    t = open(sys.argv[1]).read().lower()
    tot = 0
    for k, words in MARKERS.items():
        n = sum(len(re.findall(re.escape(w), t)) for w in words)
        tot += n
        print("%-10s %d" % (k + ":", n))
    print("index: %.1f hits/1k chars" % (1000 * tot / max(1, len(t))))
    print("# temperature read only - not a verdict", file=sys.stderr)
if __name__ == "__main__":
    main()
