#!/usr/bin/env python3
"""URL extractor - dedupes links from text. Tags: handles.
Usage: python3 url_extract.py [file]   (stdin if no file)"""
import re, sys
def main():
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    urls = sorted(set(re.findall(r"https?://[^\s\"')\]]+", src)))
    for u in urls:
        print(u)
    print("total: %d" % len(urls), file=sys.stderr)
if __name__ == "__main__":
    main()
