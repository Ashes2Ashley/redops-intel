#!/usr/bin/env python3
"""File/string hasher - sha256 and md5. Tags: util.
Usage: python3 hash_file.py <file>   or   python3 hash_file.py -s <string>"""
import hashlib, sys
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: hash_file.py <file> | -s <string>")
    data = sys.argv[2].encode() if sys.argv[1] == "-s" else open(sys.argv[1], "rb").read()
    print("sha256:", hashlib.sha256(data).hexdigest())
    print("md5:   ", hashlib.md5(data).hexdigest())
if __name__ == "__main__":
    main()
