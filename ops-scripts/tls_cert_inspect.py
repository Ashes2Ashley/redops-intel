#!/usr/bin/env python3
"""TLS certificate inspector - subject, issuer, SANs, expiry for a host. Tags: recon.
Usage: python3 tls_cert_inspect.py [host] [port]   (default: {{DOMAIN}} 443)"""
import socket, ssl, sys
from datetime import datetime, timezone
DOMAIN = "{{DOMAIN}}"
def dn(x):
    return ", ".join("=".join(p) for rdn in x for p in rdn)
def main():
    host = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=15) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ss:
            cert = ss.getpeercert()
    print("subject:", dn(cert.get("subject", [])))
    print("issuer: ", dn(cert.get("issuer", [])))
    sans = [v for t, v in cert.get("subjectAltName", []) if t == "DNS"]
    extra = " (+%d more)" % (len(sans) - 10) if len(sans) > 10 else ""
    print("SANs:   ", ", ".join(sans[:10]) + extra)
    nb = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    na = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    days = (na - datetime.now(timezone.utc)).days
    print("valid:  ", nb.date(), "->", na.date())
    flag = "  EXPIRED" if days < 0 else "  EXPIRING SOON" if days < 30 else ""
    print("expires in %d days%s" % (days, flag))
if __name__ == "__main__":
    main()
