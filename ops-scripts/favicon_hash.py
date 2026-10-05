#!/usr/bin/env python3
"""Favicon hasher - SHA-256 and murmur3-32 of a site's favicon. Tags: recon.
Usage: python3 favicon_hash.py [url]   (default: https://{{DOMAIN}})"""
import hashlib, sys, urllib.request
DOMAIN = "{{DOMAIN}}"
def murmur3_32(data, seed=0):
    c1, c2 = 0xcc9e2d51, 0x1b873593
    h = seed
    n = len(data) - len(data) % 4
    for i in range(0, n, 4):
        k = int.from_bytes(data[i:i + 4], "little")
        k = (k * c1) & 0xffffffff
        k = ((k << 15) | (k >> 17)) & 0xffffffff
        k = (k * c2) & 0xffffffff
        h ^= k
        h = ((h << 13) | (h >> 19)) & 0xffffffff
        h = (h * 5 + 0xe6546b64) & 0xffffffff
    tail, k = data[n:], 0
    for i, b in enumerate(tail):
        k |= b << (8 * i)
    if tail:
        k = (k * c1) & 0xffffffff
        k = ((k << 15) | (k >> 17)) & 0xffffffff
        k = (k * c2) & 0xffffffff
        h ^= k
    h ^= len(data)
    h ^= h >> 16
    h = (h * 0x85ebca6b) & 0xffffffff
    h ^= h >> 13
    h = (h * 0xc2b2ae35) & 0xffffffff
    h ^= h >> 16
    return h
def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "https://" + DOMAIN
    url = base.rstrip("/") + "/favicon.ico"
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    try:
        data = urllib.request.urlopen(req, timeout=20).read()
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    print("url:    ", url)
    print("bytes:  ", len(data))
    print("sha256: ", hashlib.sha256(data).hexdigest())
    print("murmur3:", murmur3_32(data))
if __name__ == "__main__":
    main()
