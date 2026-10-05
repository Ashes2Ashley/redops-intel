#!/usr/bin/env python3
"""HTTP security header audit - PASS/MISSING score for security headers. Tags: recon.
Usage: python3 http_headers_audit.py <url>"""
import sys, urllib.request
CHECKS = [
    ("Content-Security-Policy", "blocks XSS / injection"),
    ("Strict-Transport-Security", "forces HTTPS"),
    ("X-Frame-Options", "blocks clickjacking"),
    ("X-Content-Type-Options", "stops MIME sniffing"),
    ("Referrer-Policy", "limits referrer leakage"),
    ("Permissions-Policy", "restricts browser features"),
]
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: http_headers_audit.py <url>")
    req = urllib.request.Request(sys.argv[1], headers={"User-Agent": "redops-ops/1.0"})
    try:
        r = urllib.request.urlopen(req, timeout=20)
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    h, score = r.headers, 0
    for name, why in CHECKS:
        v = h.get(name)
        if v:
            score += 1
            print("PASS    %-28s %s" % (name, v[:80]))
        else:
            print("MISSING %-28s (%s)" % (name, why))
    srv = h.get("Server")
    print("note: Server header discloses '%s'" % srv[:60] if srv else "note: Server header absent (good)")
    print("score: %d/%d" % (score, len(CHECKS)))
if __name__ == "__main__":
    main()
