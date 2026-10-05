#!/usr/bin/env python3
"""CSP parser - fetches Content-Security-Policy, flags weak directives. Tags: recon.
Usage: python3 csp_parse.py <url>"""
import sys, urllib.request
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: csp_parse.py <url>")
    try:
        r = urllib.request.urlopen(sys.argv[1], timeout=20)
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    csp = r.headers.get("Content-Security-Policy")
    if not csp:
        print("CSP: MISSING")
        return
    print("raw:", csp[:400])
    low = csp.lower()
    flags = []
    if "'unsafe-inline'" in low:
        flags.append("unsafe-inline present")
    if "'unsafe-eval'" in low:
        flags.append("unsafe-eval present")
    if " *" in low or low.startswith("*"):
        flags.append("wildcard source")
    if " http:" in low:
        flags.append("plain-http source")
    if "default-src" not in low:
        flags.append("no default-src fallback")
    print("verdict:", "WEAK - " + "; ".join(flags) if flags else "no obvious weaknesses")
if __name__ == "__main__":
    main()
