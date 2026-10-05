#!/usr/bin/env python3
"""Email header analyzer - Received chain, From, auth results from a .eml. Tags: forensics.
Usage: python3 email_header_analyze.py [file.eml]   (stdin if no file)"""
import email, sys
from email import policy
def main():
    raw = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else sys.stdin.buffer.read()
    msg = email.message_from_bytes(raw, policy=policy.default)
    print("From:       ", msg.get("From", "-"))
    print("Return-Path:", msg.get("Return-Path", "-"))
    print("Date:       ", msg.get("Date", "-"))
    print("## Received chain (oldest first)")
    hops = msg.get_all("Received", [])
    for r in reversed(hops):
        print("  " + " ".join(str(r).split()))
    if not hops:
        print("  none")
    print("## Authentication-Results")
    auth = msg.get_all("Authentication-Results", [])
    for a in auth:
        print("  " + " ".join(str(a).split()))
    if not auth:
        print("  none present")
if __name__ == "__main__":
    main()
