#!/usr/bin/env python3
"""Wayback diff - unified diff of a URL between two snapshots. Tags: reporting.
Usage: python3 wayback_diff.py <url> <ts1> <ts2>   (timestamps like 20200101)"""
import difflib, re, sys, urllib.request
def text_of(url):
    html = urllib.request.urlopen(url, timeout=30).read().decode("utf8", "replace")
    html = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", html)
    txt = re.sub(r"<[^>]+>", " ", html)
    txt = re.sub(r"\s+", " ", txt)
    return [s.strip() for s in txt.split(". ") if s.strip()]
def main():
    if len(sys.argv) < 4:
        sys.exit("usage: wayback_diff.py <url> <ts1> <ts2>")
    u, t1, t2 = sys.argv[1], sys.argv[2], sys.argv[3]
    a = text_of("https://web.archive.org/web/%s/%s" % (t1, u))
    b = text_of("https://web.archive.org/web/%s/%s" % (t2, u))
    diff = list(difflib.unified_diff(a, b, fromfile=t1, tofile=t2, lineterm=""))
    if diff:
        print("\n".join(diff))
    else:
        print("no text differences")
if __name__ == "__main__":
    main()
