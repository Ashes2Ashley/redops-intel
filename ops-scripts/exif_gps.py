#!/usr/bin/env python3
"""JPEG EXIF GPS extractor - prints coordinates if present. Tags: forensics.
Usage: python3 exif_gps.py <photo.jpg>"""
import struct, sys
def main():
    data = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else sys.exit("usage: exif_gps.py <photo.jpg>")
    i = data.find(b"Exif\x00\x00")
    if i < 0:
        sys.exit("no EXIF block")
    t = i + 6
    le = data[t:t+2] == b"II"
    e = "<" if le else ">"
    if struct.unpack(e + "H", data[t:t+2])[0] not in (0x4949, 0x4D4D):
        sys.exit("bad TIFF header")
    def u16(o): return struct.unpack(e + "H", data[t+o:t+o+2])[0]
    def u32(o): return struct.unpack(e + "I", data[t+o:t+o+4])[0]
    def rat(o):
        n = struct.unpack(e + "I", data[t+o:t+o+4])[0]
        d = struct.unpack(e + "I", data[t+o+4:t+o+8])[0] or 1
        return n / d
    off0 = u32(4)
    n = u16(off0); gps = None
    for k in range(n):
        en = off0 + 2 + k * 12
        if u16(en) == 0x8825:
            gps = u32(en + 8)
    if gps is None:
        sys.exit("EXIF present, no GPS tags")
    tags = {}
    for k in range(u16(gps)):
        en = gps + 2 + k * 12
        tags[u16(en)] = u32(en + 8)
    def coord(rt, vt):
        ref = chr(data[t + tags[rt]])
        o = tags[vt]
        v = rat(o) + rat(o + 8) / 60 + rat(o + 16) / 3600
        return -v if ref in "SW" else v
    lat, lon = coord(1, 2), coord(3, 4)
    print("%.6f, %.6f" % (lat, lon))
    print("https://www.google.com/maps?q=%.6f,%.6f" % (lat, lon))
if __name__ == "__main__":
    main()
