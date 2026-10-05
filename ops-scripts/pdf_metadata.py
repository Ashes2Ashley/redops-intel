#!/usr/bin/env python3
"""PDF metadata extractor - plain-text metadata fields. Tags: forensics.
Usage: python3 pdf_metadata.py <file.pdf>"""
import re, sys
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: pdf_metadata.py <file.pdf>")
    raw = open(sys.argv[1], "rb").read().decode("latin1", "replace")
    for key in ["Title", "Author", "Subject", "Creator", "Producer",
                "CreationDate", "ModDate"]:
        m = re.search(r"/" + key + r"\s*\(([^)]{0,200})\)", raw)
        print("%-12s %s" % (key + ":", m.group(1) if m else "-"))
if __name__ == "__main__":
    main()
