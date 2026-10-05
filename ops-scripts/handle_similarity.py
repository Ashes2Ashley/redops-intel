#!/usr/bin/env python3
"""Handle similarity - difflib pairs >= 0.8 across two lists. Tags: handles.
Usage: python3 handle_similarity.py <list1> <list2>   (files, or comma-separated)"""
import difflib, sys
def load(arg):
    try:
        return [l.strip() for l in open(arg) if l.strip()]
    except OSError:
        return [h.strip() for h in arg.split(",") if h.strip()]
def main():
    if len(sys.argv) < 3:
        sys.exit("usage: handle_similarity.py <list1> <list2>")
    a, b = load(sys.argv[1]), load(sys.argv[2])
    hits = 0
    for x in a:
        for y in b:
            if x.lower() == y.lower():
                continue
            r = difflib.SequenceMatcher(None, x.lower(), y.lower()).ratio()
            if r >= 0.8:
                print("%.2f  %s  <->  %s" % (r, x, y))
                hits += 1
    print("pairs >= 0.80: %d" % hits, file=sys.stderr)
if __name__ == "__main__":
    main()
