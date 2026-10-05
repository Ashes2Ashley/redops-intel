#!/usr/bin/env python3
"""robots.txt and sitemap parser. Tags: recon.
Usage: python3 robots_sitemap.py [domain]   (default: {{DOMAIN}})"""
import re, sys, urllib.request
DOMAIN = "{{DOMAIN}}"
def get(url):
    try:
        return urllib.request.urlopen(url, timeout=20).read().decode("utf8", "replace")
    except Exception as e:
        return "# fetch failed: %s" % e
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    base = "https://" + d
    robots = get(base + "/robots.txt")
    print("## robots.txt"); print(robots[:2000])
    for sm in re.findall(r"Sitemap:\s*(\S+)", robots, re.I):
        print("## sitemap:", sm); print(get(sm)[:2000])
if __name__ == "__main__":
    main()
