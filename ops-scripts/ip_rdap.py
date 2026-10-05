#!/usr/bin/env python3
"""IP RDAP lookup - network name, country, entities for an IP. Tags: recon.
Usage: python3 ip_rdap.py [ip]   (default: 1.1.1.1)"""
import ipaddress, json, sys, urllib.request
UA = {"User-Agent": "redops-ops/1.0"}
def find_rdap(ip):
    boot = ("https://data.iana.org/rdap/ipv6.json" if ":" in ip
            else "https://data.iana.org/rdap/ipv4.json")
    req = urllib.request.Request(boot, headers=UA)
    data = json.load(urllib.request.urlopen(req, timeout=20))
    addr = ipaddress.ip_address(ip)
    for svc in data.get("services", []):
        for cidr in svc[0]:
            try:
                if addr in ipaddress.ip_network(cidr):
                    return svc[1][0]
            except ValueError:
                pass
    return None
def main():
    ip = sys.argv[1] if len(sys.argv) > 1 else "1.1.1.1"
    base = find_rdap(ip)
    if not base:
        sys.exit("no RDAP server found for " + ip)
    req = urllib.request.Request(base.rstrip("/") + "/ip/" + ip, headers=UA)
    j = json.load(urllib.request.urlopen(req, timeout=20))
    print("network: ", j.get("name"))
    print("handle:  ", j.get("handle"))
    print("country: ", j.get("country"))
    nets = []
    for r in j.get("cidr0_cidrs", []):
        pfx = r.get("v4prefix") or r.get("v6prefix") or "?"
        nets.append("%s/%s" % (pfx, r.get("length", "?")))
    print("cidr:    ", ", ".join(nets) or "-")
    ents = ["%s (%s)" % (e.get("handle", "?"), ",".join(e.get("roles", [])))
            for e in j.get("entities", [])]
    print("entities:", "; ".join(ents) or "-")
    print("status:  ", ", ".join(j.get("status", [])))
if __name__ == "__main__":
    main()
