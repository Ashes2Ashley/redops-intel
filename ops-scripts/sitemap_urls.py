#!/usr/bin/env python3
"""Sitemap harvester - fetches /sitemap.xml, follows sitemapindex one level. Tags: recon.
Usage: python3 sitemap_urls.py [domain]   (default: {{DOMAIN}})"""
import re, sys, urllib.request, urllib.error
DOMAIN = "{{DOMAIN}}"
LOC = re.compile(r"<loc>\s*([^<]+?)\s*</loc>", re.I)
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    return urllib.request.urlopen(req, timeout=25).read(4 * 1024 * 1024).decode("utf-8", "replace")
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    try:
        xml = get("https://" + d + "/sitemap.xml")
    except urllib.error.HTTPError as e:
        print("sitemap.xml: HTTP %d" % e.code)
        return
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    locs = LOC.findall(xml)
    urls = []
    if "<sitemapindex" in xml.lower():
        print("sitemapindex with %d child sitemaps" % len(locs))
        for sm in locs[:20]:
            try:
                urls.extend(LOC.findall(get(sm)))
            except Exception as e:
                print("  skip %s (%s)" % (sm[:60], e))
    else:
        urls = locs
    print("total urls: %d" % len(urls))
    for u in urls[:50]:
        print(u)
    if len(urls) > 50:
        print("... and %d more" % (len(urls) - 50))
if __name__ == "__main__":
    main()
