#!/usr/bin/env python3
"""DNS-over-HTTPS resolver - A/AAAA/MX/TXT via Google DoH. Tags: recon.
Usage: python3 doh_resolve.py <domain> [type]"""
import json, sys, urllib.request, urllib.parse
def main():
    if len(sys.argv) < 2:
        print("usage: doh_resolve.py <domain> [type]"); sys.exit(2)
    d, t = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "A"
    url = "https://dns.google/resolve?name=" + urllib.parse.quote(d) + "&type=" + t
    j = json.load(urllib.request.urlopen(url, timeout=20))
    for a in j.get("Answer", []):
        print("%-6s %s" % (a.get("type"), a.get("data")))
    if not j.get("Answer"):
        print("no answers (status %s)" % j.get("Status"))
if __name__ == "__main__":
    main()
