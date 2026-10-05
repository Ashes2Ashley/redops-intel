#!/usr/bin/env python3
"""Wayback snapshot lister - CDX API for a domain. Tags: recon.
Usage: python3 wayback_list.py [domain]   (default: {{DOMAIN}})"""
import json, sys, urllib.request, urllib.parse
DOMAIN = "{{DOMAIN}}"
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    url = ("https://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(d) +
           "&output=json&filter=statuscode:200&collapse=digest&limit=50")
    rows = json.load(urllib.request.urlopen(url, timeout=30))
    for r in rows[1:]:
        print(r[1], r[2])
    print("snapshots: %d" % (len(rows) - 1), file=sys.stderr)
if __name__ == "__main__":
    main()
