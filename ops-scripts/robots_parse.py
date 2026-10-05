#!/usr/bin/env python3
"""Robots.txt parser - lists Disallow paths, Sitemaps, rule counts per agent. Tags: recon.
Usage: python3 robots_parse.py [domain]   (default: {{DOMAIN}})"""
import sys, urllib.request, urllib.error
from collections import Counter
DOMAIN = "{{DOMAIN}}"
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    req = urllib.request.Request("https://" + d + "/robots.txt",
                                 headers={"User-Agent": "redops-ops/1.0"})
    try:
        body = urllib.request.urlopen(req, timeout=20).read(262144).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        print("robots.txt: HTTP %d" % e.code)
        return
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    agent, counts, disallows, sitemaps = "*", Counter(), [], []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            agent = v
        elif k == "disallow":
            counts[agent] += 1
            if v:
                disallows.append((agent, v))
        elif k == "sitemap":
            sitemaps.append(v)
    print("robots.txt: %d lines" % len(body.splitlines()))
    print("rules per agent:")
    for a, c in counts.most_common():
        print("  %-22s %d disallows" % (a, c))
    print("disallow paths (%d):" % len(disallows))
    for a, p in disallows[:60]:
        print("  [%s] %s" % (a, p))
    if len(disallows) > 60:
        print("  ... and %d more" % (len(disallows) - 60))
    print("sitemaps (%d):" % len(sitemaps))
    for s in sitemaps:
        print("  " + s)
if __name__ == "__main__":
    main()
