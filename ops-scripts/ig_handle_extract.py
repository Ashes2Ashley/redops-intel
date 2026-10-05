#!/usr/bin/env python3
"""Instagram handle extractor - pulls @handles from pasted HTML/text. Tags: handles.
Usage: python3 ig_handle_extract.py [file]   (stdin if no file)"""
import re, sys
def main():
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    found = sorted(set(re.findall(r"@([A-Za-z0-9_.]{2,30})", src)))
    for h in found:
        print("@" + h)
    print("total: %d" % len(found), file=sys.stderr)
if __name__ == "__main__":
    main()
