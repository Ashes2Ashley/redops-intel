#!/usr/bin/env python3
"""Redirect chain tracer - manual hop-by-hop, no auto-follow. Tags: recon.
Usage: python3 redirect_chain.py <url>"""
import sys, urllib.request, urllib.parse, urllib.error
class NoFollow(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: redirect_chain.py <url>")
    url = sys.argv[1]
    opener = urllib.request.build_opener(NoFollow)
    for hop in range(10):
        req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
        try:
            r = opener.open(req, timeout=15)
            print("%d. %s -> HTTP %d (final)" % (hop + 1, url, r.status))
            break
        except urllib.error.HTTPError as e:
            loc = e.headers.get("Location")
            print("%d. %s -> HTTP %d -> %s" % (hop + 1, url, e.code, loc))
            if not loc or hop == 9:
                break
            url = urllib.parse.urljoin(url, loc)
if __name__ == "__main__":
    main()
