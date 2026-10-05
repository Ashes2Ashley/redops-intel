#!/usr/bin/env python3
"""Dangling-DNS candidate finder - CNAMEs from crt.sh subdomains via DoH. Tags: hardening.
Usage: python3 dangling_dns.py [domain]   (default: {{DOMAIN}})
Prints CNAME targets; the operator must verify whether each is claimed."""
import json, sys, urllib.request, urllib.parse

DOMAIN = "{{DOMAIN}}"
PAAS = ("herokuapp.com", "azurewebsites.net", "amazonaws.com", "cloudfront.net",
        "github.io", "netlify.app", "vercel.app", "s3.amazonaws.com",
        "trafficmanager.net", "cloudapp.net", "elasticbeanstalk.com")

def get_json(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0",
                                               "Accept": accept})
    return json.load(urllib.request.urlopen(req, timeout=25))

def subdomains(d):
    url = "https://crt.sh/?q=%25." + urllib.parse.quote(d) + "&output=json"
    rows = get_json(url)
    seen = set()
    for r in rows:
        for n in str(r.get("name_value", "")).split("\n"):
            n = n.strip().lower().rstrip(".")
            if n and "*" not in n and (n == d or n.endswith("." + d)):
                seen.add(n)
    return sorted(seen)

def cname(name):
    url = ("https://cloudflare-dns.com/dns-query?name=" + urllib.parse.quote(name)
           + "&type=CNAME")
    try:
        j = get_json(url, "application/dns-json")
    except Exception:
        return None
    for a in j.get("Answer", []):
        if a.get("type") == 5:
            return a.get("data", "").rstrip(".").lower()
    return None

def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    try:
        subs = subdomains(d)
    except Exception as e:
        sys.exit("crt.sh query failed: %s" % e)
    print("subdomains from crt.sh: %d" % len(subs))
    flagged = 0
    for s in subs:
        t = cname(s)
        if not t:
            continue
        mark = ""
        if any(t == p or t.endswith("." + p) for p in PAAS):
            mark = "  <-- VERIFY: points at third-party host"
            flagged += 1
        print("%-45s CNAME -> %s%s" % (s, t, mark))
    print("")
    print("%d CNAME(s) merit verification for dangling records." % flagged)
    print("note: only the operator can confirm a target is unclaimed - check the provider.")

if __name__ == "__main__":
    main()
