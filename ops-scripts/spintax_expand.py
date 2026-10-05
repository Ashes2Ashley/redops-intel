#!/usr/bin/env python3
"""Spintax expander - {a|b|c} to N variants. Tags: util.
Usage: python3 spintax_expand.py '{Hello|Hi} {there|friend}' [count]"""
import itertools, re, sys
def expand(s, n=5):
    parts = re.split(r"(\{[^{}]*\})", s)
    opts = [p[1:-1].split("|") if p.startswith("{") else [p] for p in parts]
    out = []
    for combo in itertools.islice(itertools.product(*opts), n):
        out.append("".join(combo))
    return out
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: spintax_expand.py '{a|b}' [count]")
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    for v in expand(sys.argv[1], n):
        print(v)
if __name__ == "__main__":
    main()
