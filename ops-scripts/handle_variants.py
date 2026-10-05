#!/usr/bin/env python3
"""Handle variant generator - 15 alias spellings for a handle. Tags: handles.
Usage: python3 handle_variants.py <handle>"""
import sys
def variants(h):
    h = h.strip()
    v = [h, h.lower(), h.upper(), h.replace("_", ""), h.replace("_", "-"),
         h.replace("0", "o"), h.replace("1", "l"), h + "_", "_" + h,
         h + "1", h + "123", "the" + h, "real" + h, h + "tv", h + "gg"]
    out = []
    for x in v:
        if x not in out:
            out.append(x)
    return out
def main():
    if len(sys.argv) < 2:
        print("usage: handle_variants.py <handle>"); sys.exit(2)
    for x in variants(sys.argv[1]):
        print(x)
if __name__ == "__main__":
    main()
