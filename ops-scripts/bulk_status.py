#!/usr/bin/env python3
"""Bulk URL status - code, final URL, ms for each URL. Tags: utilities.
Usage: python3 bulk_status.py [file] [url ...]   (stdin if nothing given)"""
import sys, time, urllib.request, urllib.error
def check(url):
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    try:
        r = urllib.request.urlopen(req, timeout=15)
        ms = int((time.time() - t0) * 1000)
        return r.status, r.url, ms
    except urllib.error.HTTPError as e:
        return e.code, url, int((time.time() - t0) * 1000)
    except Exception:
        return "ERR", url, int((time.time() - t0) * 1000)
def main():
    urls, args = [], sys.argv[1:]
    if args:
        try:
            urls += [l.strip() for l in open(args[0]) if l.strip()]
            args = args[1:]
        except OSError:
            pass
        urls += args
    if not urls:
        urls = [l.strip() for l in sys.stdin if l.strip()]
    if not urls:
        sys.exit("usage: bulk_status.py [file] [url ...]")
    for u in urls:
        code, final, ms = check(u)
        extra = "" if final == u else "  -> " + final
        print("%-6s %5dms  %s%s" % (code, ms, u, extra))
if __name__ == "__main__":
    main()
