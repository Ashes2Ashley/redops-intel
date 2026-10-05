#!/usr/bin/env python3
"""Page metadata extractor - title, description, og: tags, generator. Tags: recon.
Usage: python3 meta_extract.py <url>"""
import html, re, sys, urllib.request
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
META = re.compile(r"<meta\s+[^>]*>", re.I)
ATTR = re.compile(r"(\w[\w:-]*)\s*=\s*(?:\x22([^\x22]*)\x22|'([^']*)'|([^\s>]+))")
WANTED = ("description", "og:description", "og:title", "og:site_name",
          "generator", "author", "keywords", "twitter:description")
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: meta_extract.py <url>")
    req = urllib.request.Request(sys.argv[1], headers={"User-Agent": "redops-ops/1.0"})
    try:
        body = urllib.request.urlopen(req, timeout=25).read(1024 * 1024).decode("utf-8", "replace")
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    m = re.search(r"</head\s*>", body, re.I)
    head = body[:m.start()] if m else body[:200000]
    t = TITLE.search(head)
    print("title: %s" % (html.unescape(t.group(1).strip()) if t else "(none)"))
    seen = set()
    for tag in META.findall(head):
        attrs = {}
        for k, v1, v2, v3 in ATTR.findall(tag):
            attrs[k.lower()] = v1 or v2 or v3
        name = attrs.get("name", "").lower() or attrs.get("property", "").lower()
        if name in WANTED and name not in seen and "content" in attrs:
            seen.add(name)
            print("%s: %s" % (name, html.unescape(attrs["content"])[:200]))
    if not seen:
        print("(no description/og:/generator meta found)")
if __name__ == "__main__":
    main()
