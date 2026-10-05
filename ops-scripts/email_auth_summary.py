#!/usr/bin/env python3
"""Email auth summary - MX/SPF/DKIM/DMARC for a domain via DoH. Tags: recon.
Usage: python3 email_auth_summary.py [domain] [dkim-selector]   (default: {{DOMAIN}})"""
import json, sys, urllib.request, urllib.parse
DOMAIN = "{{DOMAIN}}"
def q(name, rtype):
    url = ("https://cloudflare-dns.com/dns-query?name=" + urllib.parse.quote(name) +
           "&type=" + rtype)
    req = urllib.request.Request(url, headers={"accept": "application/dns-json",
                                               "User-Agent": "redops-ops/1.0"})
    j = json.load(urllib.request.urlopen(req, timeout=15))
    return [a["data"] for a in j.get("Answer", [])]
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    sel = sys.argv[2] if len(sys.argv) > 2 else "default"
    mx, a = q(d, "MX"), q(d, "A")
    spf = [t for t in q(d, "TXT") if "v=spf1" in t]
    dmarc = q("_dmarc." + d, "TXT")
    dkim = q(sel + "._domainkey." + d, "TXT")
    print("domain:", d)
    print("MX:    ", "; ".join(mx) or "none")
    print("A:     ", "; ".join(a) or "none")
    print("SPF:   ", spf[0][:120] if spf else "MISSING")
    print("DKIM(%s): %s" % (sel, "PRESENT" if dkim else "MISSING"))
    print("DMARC: ", dmarc[0][:120] if dmarc else "MISSING")
if __name__ == "__main__":
    main()
