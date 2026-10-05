#!/usr/bin/env python3
"""Page text extractor - strips tags/scripts, prints clean text. Tags: utilities.
Usage: python3 page_text_extract.py <url>"""
import re, sys, urllib.request
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: page_text_extract.py <url>")
    try:
        html = urllib.request.urlopen(sys.argv[1], timeout=20).read().decode("utf8", "replace")
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    html = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", html)
    html = re.sub(r"<!--.*?-->", " ", html)
    txt = re.sub(r"<[^>]+>", " ", html)
    txt = re.sub(r"[ \t]+", " ", txt)
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    print("\n".join(lines))
if __name__ == "__main__":
    main()
