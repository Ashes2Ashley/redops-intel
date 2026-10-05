#!/usr/bin/env python3
"""Certificate transparency poller - compares crt.sh now vs a baseline file. Tags: recon.
Usage: python3 certspotter_poll.py <domain> [baseline.txt]"""
import json, sys, urllib.request, urllib.parse
def get(d):
    url = "https://crt.sh/?q=%25." + urllib.parse.quote(d) + "&output=json"
    rows = json.load(urllib.request.urlopen(url, timeout=30))
    seen = set()
    for r in rows:
        for n in str(r.get("name_value", "")).split("\n"):
            n = n.strip().lower()
            if n and "*" not in n:
                seen.add(n)
    return seen
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: certspotter_poll.py <domain> [baseline.txt]")
    now = get(sys.argv[1])
    base = set()
    if len(sys.argv) > 2:
        try:
            base = set(l.strip() for l in open(sys.argv[2]) if l.strip())
        except OSError:
            pass
    new = sorted(now - base)
    print("known: %d  new: %d" % (len(base), len(new)))
    for s in new:
        print("NEW:", s)
    with open(sys.argv[1] + ".baseline.txt", "w") as f:
        f.write("\n".join(sorted(now)))
if __name__ == "__main__":
    main()
