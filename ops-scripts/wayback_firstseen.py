#!/usr/bin/env python3
"""Wayback first-seen - earliest archived snapshot of a URL. Tags: recon.
Usage: python3 wayback_firstseen.py [url]   (default: https://{{DOMAIN}})"""
import json, sys, urllib.request, urllib.parse
DOMAIN = "{{DOMAIN}}"
def main():
    u = sys.argv[1] if len(sys.argv) > 1 else "https://" + DOMAIN
    url = ("https://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(u) +
           "&output=json&filter=statuscode:200&limit=5")
    rows = json.load(urllib.request.urlopen(url, timeout=30))
    if len(rows) < 2:
        sys.exit("no snapshots found for " + u)
    ts = rows[1][1]
    print("url:       ", u)
    print("first seen: %s-%s-%s %s:%s:%s UTC" % (ts[0:4], ts[4:6], ts[6:8], ts[8:10], ts[10:12], ts[12:14]))
    print("snapshot:   https://web.archive.org/web/%s/%s" % (ts, u))
    print("total 200s: %d (capped at 5 shown)" % (len(rows) - 1))
if __name__ == "__main__":
    main()
