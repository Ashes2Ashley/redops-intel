#!/usr/bin/env python3
"""PII redactor - masks emails, phones, long tokens in text. Tags: util.
Usage: python3 redact_pii.py [file]   (stdin if no file)"""
import re, sys
def main():
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    src = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[EMAIL]", src)
    src = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[PHONE]", src)
    src = re.sub(r"\b[A-Za-z0-9_-]{32,}\b", "[TOKEN]", src)
    sys.stdout.write(src)
if __name__ == "__main__":
    main()
