#!/usr/bin/env python3
"""Security.txt checker - fetches /.well-known/security.txt, prints contacts/policy. Tags: recon.
Usage: python3 security_txt.py [domain]   (default: {{DOMAIN}})"""
import sys, urllib.request, urllib.error
DOMAIN = "{{DOMAIN}}"
FIELDS = ("contact", "policy", "expires", "encryption", "acknowledgments", "hiring", "preferred-languages")
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    req = urllib.request.Request("https://" + d + "/.well-known/security.txt",
                                 headers={"User-Agent": "redops-ops/1.0"})
    try:
        body = urllib.request.urlopen(req, timeout=20).read(65536).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        print("security.txt: ABSENT (HTTP %d)" % e.code)
        return
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    print("security.txt: PRESENT")
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        if k.strip().lower() in FIELDS:
            print("%-18s %s" % (k.strip().lower(), v.strip()))
if __name__ == "__main__":
    main()
