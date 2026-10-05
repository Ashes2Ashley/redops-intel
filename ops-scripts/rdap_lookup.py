#!/usr/bin/env python3
"""RDAP domain lookup - registrar, creation date, status. Tags: recon.
Usage: python3 rdap_lookup.py [domain]   (default: {{DOMAIN}})"""
import json, sys, urllib.request, urllib.parse
DOMAIN = "{{DOMAIN}}"
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    url = "https://rdap.org/domain/" + urllib.parse.quote(d)
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    j = json.load(urllib.request.urlopen(req, timeout=30))
    print("domain:  ", j.get("ldhName"))
    print("registrar:", ", ".join(e.get("handle", "") for e in j.get("entities", [])))
    for ev in j.get("events", []):
        if ev.get("eventAction") in ("registration", "last changed"):
            print("%-10s %s" % (ev["eventAction"], ev.get("eventDate")))
    print("status:  ", ", ".join(j.get("status", [])))
if __name__ == "__main__":
    main()
