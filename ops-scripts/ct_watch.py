#!/usr/bin/env python3
"""Certificate-transparency watch - certs issued for a domain in the last 30 days. Tags: hardening.
Usage: python3 ct_watch.py [domain]   (default: {{DOMAIN}})
Newest first; the operator spots issuers/SANs they don't recognize."""
import json, sys, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone

DOMAIN = "{{DOMAIN}}"

def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    url = "https://crt.sh/?q=%25." + urllib.parse.quote(d) + "&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    try:
        rows = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        sys.exit("crt.sh query failed: %s" % e)
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    certs = []
    for r in rows:
        try:
            nb = datetime.fromisoformat(
                str(r.get("not_before", "")).replace("Z", "+00:00"))
        except ValueError:
            continue
        if nb.tzinfo is None:
            nb = nb.replace(tzinfo=timezone.utc)
        if nb >= cutoff:
            certs.append((nb, r))
    certs.sort(key=lambda x: x[0], reverse=True)
    print("certs for %s issued in last 30 days: %d" % (d, len(certs)))
    for nb, r in certs[:50]:
        issuer = (r.get("issuer_name") or "").replace("\n", " ")
        sans = str(r.get("name_value", "")).replace("\n", ", ")
        print("%s  id=%s" % (nb.strftime("%Y-%m-%d"), r.get("id")))
        print("   issuer: %s" % issuer[:120])
        print("   SANs: %s" % sans[:200])
    if len(certs) > 50:
        print("... and %d more" % (len(certs) - 50))
    print("")
    print("verify every issuer/SAN above - anything unrecognized may be rogue.")

if __name__ == "__main__":
    main()
