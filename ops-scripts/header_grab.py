#!/usr/bin/env python3
"""HTTP security header checker. Tags: recon.
Usage: python3 header_grab.py <url>"""
import sys, urllib.request
CHECKS = ["content-security-policy", "strict-transport-security",
          "x-content-type-options", "x-frame-options",
          "referrer-policy", "permissions-policy"]
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: header_grab.py <url>")
    try:
        r = urllib.request.urlopen(sys.argv[1], timeout=20)
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    print("status:", r.status)
    hdrs = {k.lower(): v for k, v in r.headers.items()}
    for c in CHECKS:
        print("%-28s %s" % (c, "PRESENT" if c in hdrs else "MISSING"))
if __name__ == "__main__":
    main()
