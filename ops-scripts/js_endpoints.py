#!/usr/bin/env python3
"""JS endpoint extractor - absolute URLs and /api/* paths from a JS file. Tags: recon.
Usage: python3 js_endpoints.py <js-url>"""
import re, sys, urllib.request
ABS = re.compile(r"[\x22'](https?://[A-Za-z0-9._~:/?#@!$&()*+,;=%-]{4,200})[\x22']")
API = re.compile(r"[\x22'](/(?:api|v[0-9]|graphql)[A-Za-z0-9._~:/?#@!$&()*+,;=%-]{1,160})[\x22']")
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: js_endpoints.py <js-url>")
    req = urllib.request.Request(sys.argv[1], headers={"User-Agent": "redops-ops/1.0"})
    try:
        body = urllib.request.urlopen(req, timeout=25).read(2 * 1024 * 1024).decode("utf-8", "replace")
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    absu = sorted(set(ABS.findall(body)))
    apis = sorted(set(API.findall(body)))
    print("absolute urls (%d):" % len(absu))
    for u in absu[:80]:
        print("  " + u)
    print("api-ish paths (%d):" % len(apis))
    for p in apis[:80]:
        print("  " + p)
if __name__ == "__main__":
    main()
