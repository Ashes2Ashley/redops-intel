#!/usr/bin/env python3
"""Subdomain enumerator - certificate transparency logs (crt.sh). Tags: recon.
Usage: python3 subdomains_crt.py [domain]   (default: {{DOMAIN}})"""
import json, sys, urllib.request, urllib.parse
DOMAIN = "{{DOMAIN}}"
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    url = "https://crt.sh/?q=%25." + urllib.parse.quote(d) + "&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    rows = json.load(urllib.request.urlopen(req, timeout=30))
    seen = set()
    for r in rows:
        for n in str(r.get("name_value", "")).split("\n"):
            n = n.strip().lower()
            if n and "*" not in n and n not in seen:
                seen.add(n)
    for s in sorted(seen):
        print(s)
    print("total: %d" % len(seen), file=sys.stderr)
if __name__ == "__main__":
    main()
