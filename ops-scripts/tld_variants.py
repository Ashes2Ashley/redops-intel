#!/usr/bin/env python3
"""Typosquat watchlist generator - omission, doubling, swaps, ascii lookalikes, TLD swaps. Tags: recon.
Usage: python3 tld_variants.py [domain]   (default: {{DOMAIN}})"""
import sys
DOMAIN = "{{DOMAIN}}"
TLDS = ["com", "net", "org", "io", "co", "info", "biz", "online", "site", "app"]
SWAPS = {"a": ["4", "@"], "e": ["3"], "i": ["1", "l"], "l": ["1", "i"],
         "o": ["0"], "s": ["5", "$"], "t": ["7"], "g": ["9"], "b": ["8"]}
def name_variants(name):
    out = []
    for i in range(len(name)):
        out.append(name[:i] + name[i+1:])
    for i in range(len(name)):
        out.append(name[:i] + name[i] + name[i:])
    for i in range(len(name) - 1):
        out.append(name[:i] + name[i+1] + name[i] + name[i+2:])
    for i, ch in enumerate(name):
        for rep in SWAPS.get(ch.lower(), []):
            out.append(name[:i] + rep + name[i+1:])
    seen, uniq = set(), []
    for v in out:
        if v and v != name and v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq
def main():
    d = (sys.argv[1] if len(sys.argv) > 1 else DOMAIN).lower().strip()
    name, tld = d.rsplit(".", 1) if "." in d else (d, "com")
    n = 0
    for v in name_variants(name):
        n += 1
        print("%3d. %s.%s" % (n, v, tld))
    for t in TLDS:
        if t != tld:
            n += 1
            print("%3d. %s.%s" % (n, name, t))
    print("total: %d candidates" % n)
if __name__ == "__main__":
    main()
