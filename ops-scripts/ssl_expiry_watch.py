#!/usr/bin/env python3
"""SSL expiry watch - days-to-expiry for hosts, flags <30d. Tags: recon.
Usage: python3 ssl_expiry_watch.py [host ...]   (stdin, one per line, if none)"""
import socket, ssl, sys
from datetime import datetime, timezone
def days_left(host):
    ctx = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=12) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ss:
            cert = ss.getpeercert()
    na = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    return (na - datetime.now(timezone.utc)).days
def main():
    hosts = sys.argv[1:] or [l.strip() for l in sys.stdin if l.strip()]
    if not hosts:
        sys.exit("usage: ssl_expiry_watch.py [host ...]")
    for h in hosts:
        try:
            d = days_left(h)
            flag = "  <-- EXPIRING SOON" if d < 30 else ""
            print("%-30s %4d days%s" % (h, d, flag))
        except Exception as e:
            print("%-30s ERROR %s" % (h, type(e).__name__))
if __name__ == "__main__":
    main()
