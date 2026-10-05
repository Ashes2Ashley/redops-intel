#!/usr/bin/env python3
"""Write the 25 ops scripts to ops-scripts/ and compile-check each one."""
import os, py_compile

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ops-scripts")
os.makedirs(BASE, exist_ok=True)

SCRIPTS = {}

SCRIPTS["subdomains_crt"] = '''#!/usr/bin/env python3
"""Subdomain enumerator - certificate transparency logs (crt.sh). Tags: recon.
Usage: python3 subdomains_crt.py [domain]   (default: {{DOMAIN}})"""
import json, sys, urllib.request, urllib.parse
DOMAIN = "{{DOMAIN}}"
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    url = "https://crt.sh/?q=%25." + urllib.parse.quote(d) + "&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    rows = json.load(urllib.request.urlopen(req, timeout=30))
    seen = set()
    for r in rows:
        for n in str(r.get("name_value", "")).split("\\n"):
            n = n.strip().lower()
            if n and "*" not in n and n not in seen:
                seen.add(n)
    for s in sorted(seen):
        print(s)
    print("total: %d" % len(seen), file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["rdap_lookup"] = '''#!/usr/bin/env python3
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
'''

SCRIPTS["doh_resolve"] = '''#!/usr/bin/env python3
"""DNS-over-HTTPS resolver - A/AAAA/MX/TXT via Google DoH. Tags: recon.
Usage: python3 doh_resolve.py <domain> [type]"""
import json, sys, urllib.request, urllib.parse
def main():
    if len(sys.argv) < 2:
        print("usage: doh_resolve.py <domain> [type]"); sys.exit(2)
    d, t = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "A"
    url = "https://dns.google/resolve?name=" + urllib.parse.quote(d) + "&type=" + t
    j = json.load(urllib.request.urlopen(url, timeout=20))
    for a in j.get("Answer", []):
        print("%-6s %s" % (a.get("type"), a.get("data")))
    if not j.get("Answer"):
        print("no answers (status %s)" % j.get("Status"))
if __name__ == "__main__":
    main()
'''

SCRIPTS["handle_variants"] = '''#!/usr/bin/env python3
"""Handle variant generator - 15 alias spellings for a handle. Tags: handles.
Usage: python3 handle_variants.py <handle>"""
import sys
def variants(h):
    h = h.strip()
    v = [h, h.lower(), h.upper(), h.replace("_", ""), h.replace("_", "-"),
         h.replace("0", "o"), h.replace("1", "l"), h + "_", "_" + h,
         h + "1", h + "123", "the" + h, "real" + h, h + "tv", h + "gg"]
    out = []
    for x in v:
        if x not in out:
            out.append(x)
    return out
def main():
    if len(sys.argv) < 2:
        print("usage: handle_variants.py <handle>"); sys.exit(2)
    for x in variants(sys.argv[1]):
        print(x)
if __name__ == "__main__":
    main()
'''

SCRIPTS["email_permutations"] = '''#!/usr/bin/env python3
"""Email permutation generator - likely addresses for a name. Tags: handles.
Usage: python3 email_permutations.py <first> <last> [domain]"""
import sys
def perms(first, last):
    f, l = first.lower(), last.lower()
    pats = [f + "." + l, f + l, f[0] + l, f + l[0], f + "_" + l, f + "-" + l,
            l + "." + f, l + f, f[0] + "." + l, f + "." + l[0], f + l + "1",
            f + "." + l + "1", f[0] + l[0], f + l + "123"]
    return sorted(set(pats))
def main():
    if len(sys.argv) < 3:
        print("usage: email_permutations.py <first> <last> [domain]"); sys.exit(2)
    dom = sys.argv[3] if len(sys.argv) > 3 else "gmail.com  # guess - verify"
    for p in perms(sys.argv[1], sys.argv[2]):
        print(p + "@" + dom.split()[0])
if __name__ == "__main__":
    main()
'''

SCRIPTS["dork_pack"] = '''#!/usr/bin/env python3
"""Dork pack generator - 12 search queries for a handle. Tags: handles.
Usage: python3 dork_pack.py <handle>"""
import sys
DORKS = ['"{h}"', 'site:runehall.com "{h}"', 'site:sythe.org "{h}"',
         '"{h}" discord', '"{h}" telegram', '"{h}" github',
         '"{h}" site:pastebin.com OR site:psbdmp.ws', 'site:reddit.com "{h}"',
         'site:x.com "{h}"', 'site:youtube.com "{h}"',
         'site:twitch.tv "{h}"', '"{h}" runehall']
def main():
    if len(sys.argv) < 2:
        print("usage: dork_pack.py <handle>"); sys.exit(2)
    for d in DORKS:
        print(d.format(h=sys.argv[1]))
if __name__ == "__main__":
    main()
'''

SCRIPTS["ig_handle_extract"] = '''#!/usr/bin/env python3
"""Instagram handle extractor - pulls @handles from pasted HTML/text. Tags: handles.
Usage: python3 ig_handle_extract.py [file]   (stdin if no file)"""
import re, sys
def main():
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    found = sorted(set(re.findall(r"@([A-Za-z0-9_.]{2,30})", src)))
    for h in found:
        print("@" + h)
    print("total: %d" % len(found), file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["snowflake_time"] = '''#!/usr/bin/env python3
"""Discord snowflake to UTC timestamp converter. Tags: util.
Usage: python3 snowflake_time.py <snowflake_id> [...]"""
import datetime, sys
EPOCH = 1420070400000
def main():
    for arg in sys.argv[1:]:
        try:
            ts = (int(arg) >> 22) + EPOCH
            dt = datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc)
            print(arg, "->", dt.strftime("%Y-%m-%d %H:%M:%S UTC"))
        except ValueError:
            print(arg, "-> not a snowflake", file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["exif_gps"] = '''#!/usr/bin/env python3
"""JPEG EXIF GPS extractor - prints coordinates if present. Tags: forensics.
Usage: python3 exif_gps.py <photo.jpg>"""
import struct, sys
def main():
    data = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else sys.exit("usage: exif_gps.py <photo.jpg>")
    i = data.find(b"Exif\\x00\\x00")
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
'''

SCRIPTS["pdf_metadata"] = '''#!/usr/bin/env python3
"""PDF metadata extractor - plain-text metadata fields. Tags: forensics.
Usage: python3 pdf_metadata.py <file.pdf>"""
import re, sys
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: pdf_metadata.py <file.pdf>")
    raw = open(sys.argv[1], "rb").read().decode("latin1", "replace")
    for key in ["Title", "Author", "Subject", "Creator", "Producer",
                "CreationDate", "ModDate"]:
        m = re.search(r"/" + key + r"\\s*\\(([^)]{0,200})\\)", raw)
        print("%-12s %s" % (key + ":", m.group(1) if m else "-"))
if __name__ == "__main__":
    main()
'''

SCRIPTS["chisq_uniform"] = '''#!/usr/bin/env python3
"""Chi-square uniformity test - one value per line on stdin. Tags: forensics.
Usage: cat winners.txt | python3 chisq_uniform.py"""
import math, sys
def main():
    vals = [l.strip() for l in sys.stdin if l.strip()]
    if len(vals) < 5:
        sys.exit("need at least 5 values")
    counts = {}
    for v in vals:
        counts[v] = counts.get(v, 0) + 1
    n, k = len(vals), len(counts)
    exp = n / k
    chi = sum((c - exp) ** 2 / exp for c in counts.values())
    print("draws: %d  unique: %d  chi-square: %.2f  (df %d)" % (n, k, chi, k - 1))
    print("verdict:", "SKEWED - worth a deeper look" if chi > (k - 1) * 2
          else "consistent with a fair draw")
if __name__ == "__main__":
    main()
'''

SCRIPTS["withdrawal_delays"] = '''#!/usr/bin/env python3
"""Withdrawal delay analyzer - request_date,paid_date,amount per line. Tags: forensics.
Usage: python3 withdrawal_delays.py delays.csv"""
import csv, statistics, sys
from datetime import date
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: withdrawal_delays.py delays.csv")
    delays = []
    for row in csv.reader(open(sys.argv[1])):
        if len(row) < 2:
            continue
        try:
            d = (date.fromisoformat(row[1].strip()) - date.fromisoformat(row[0].strip())).days
            delays.append((d, ",".join(row)))
        except ValueError:
            pass
    ds = [d for d, _ in delays]
    print("count: %d  avg: %.1fd  median: %.1fd  max: %dd"
          % (len(ds), sum(ds) / len(ds), statistics.median(ds), max(ds)))
    slow = [(d, r) for d, r in delays if d > 7]
    print("over 7 days: %d" % len(slow))
    for d, r in slow:
        print("  %dd  %s" % (d, r))
if __name__ == "__main__":
    main()
'''

SCRIPTS["fee_outliers"] = '''#!/usr/bin/env python3
"""Fee outlier finder - amount,fee per line. Tags: forensics.
Usage: python3 fee_outliers.py fees.csv"""
import csv, sys
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: fee_outliers.py fees.csv")
    rows = []
    for row in csv.reader(open(sys.argv[1])):
        try:
            a, f = float(row[0]), float(row[1])
            if a > 0:
                rows.append((a, f, f / a * 100))
        except (ValueError, IndexError):
            pass
    avg = sum(r[2] for r in rows) / len(rows)
    print("avg fee: %.3f%% over %d rows" % (avg, len(rows)))
    for a, f, p in rows:
        if p > avg * 2:
            print("FLAG %.0f,%.0f -> %.3f%%" % (a, f, p))
if __name__ == "__main__":
    main()
'''

SCRIPTS["timeline_build"] = '''#!/usr/bin/env python3
"""Timeline builder - date,event CSV lines to markdown timeline. Tags: reporting.
Usage: python3 timeline_build.py events.csv"""
import csv, sys
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: timeline_build.py events.csv")
    rows = sorted(csv.reader(open(sys.argv[1])))
    print("# Timeline - %s" % "{{CALLSIGN}}")
    for r in rows:
        if len(r) >= 2:
            print("- **%s** - %s" % (r[0].strip(), r[1].strip()))
if __name__ == "__main__":
    main()
'''

SCRIPTS["url_extract"] = '''#!/usr/bin/env python3
"""URL extractor - dedupes links from text. Tags: handles.
Usage: python3 url_extract.py [file]   (stdin if no file)"""
import re, sys
def main():
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    urls = sorted(set(re.findall(r"https?://[^\\s\\"')\\]]+", src)))
    for u in urls:
        print(u)
    print("total: %d" % len(urls), file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["platform_urls"] = '''#!/usr/bin/env python3
"""Platform URL builder - profile links for a username. Tags: handles.
Usage: python3 platform_urls.py <username>"""
import sys, urllib.parse
PLATFORMS = [("Steam", "https://steamcommunity.com/id/{}"),
             ("Xbox", "https://xboxgamertag.com/search/{}"),
             ("PSN", "https://psnprofiles.com/{}"),
             ("Twitch", "https://www.twitch.tv/{}"),
             ("Reddit", "https://www.reddit.com/user/{}"),
             ("GitHub", "https://github.com/{}"),
             ("X", "https://x.com/{}"),
             ("YouTube", "https://www.youtube.com/@{}")]
def main():
    if len(sys.argv) < 2:
        print("usage: platform_urls.py <username>"); sys.exit(2)
    u = urllib.parse.quote(sys.argv[1])
    for name, tpl in PLATFORMS:
        print("%-8s %s" % (name + ":", tpl.format(u)))
    print("# links only - not identity verification", file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["wayback_list"] = '''#!/usr/bin/env python3
"""Wayback snapshot lister - CDX API for a domain. Tags: recon.
Usage: python3 wayback_list.py [domain]   (default: {{DOMAIN}})"""
import json, sys, urllib.request, urllib.parse
DOMAIN = "{{DOMAIN}}"
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    url = ("https://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(d) +
           "&output=json&filter=statuscode:200&collapse=digest&limit=50")
    rows = json.load(urllib.request.urlopen(url, timeout=30))
    for r in rows[1:]:
        print(r[1], r[2])
    print("snapshots: %d" % (len(rows) - 1), file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["certspotter_poll"] = '''#!/usr/bin/env python3
"""Certificate transparency poller - compares crt.sh now vs a baseline file. Tags: recon.
Usage: python3 certspotter_poll.py <domain> [baseline.txt]"""
import json, sys, urllib.request, urllib.parse
def get(d):
    url = "https://crt.sh/?q=%25." + urllib.parse.quote(d) + "&output=json"
    rows = json.load(urllib.request.urlopen(url, timeout=30))
    seen = set()
    for r in rows:
        for n in str(r.get("name_value", "")).split("\\n"):
            n = n.strip().lower()
            if n and "*" not in n:
                seen.add(n)
    return seen
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: certspotter_poll.py <domain> [baseline.txt]")
    now = get(sys.argv[1])
    base = set()
    if len(sys.argv) > 2:
        try:
            base = set(l.strip() for l in open(sys.argv[2]) if l.strip())
        except OSError:
            pass
    new = sorted(now - base)
    print("known: %d  new: %d" % (len(base), len(new)))
    for s in new:
        print("NEW:", s)
    with open(sys.argv[1] + ".baseline.txt", "w") as f:
        f.write("\\n".join(sorted(now)))
if __name__ == "__main__":
    main()
'''

SCRIPTS["marker_counter"] = '''#!/usr/bin/env python3
"""Keyword marker counter - fear/greed/despair signals in chat text. Tags: forensics.
Usage: python3 marker_counter.py chat.txt"""
import re, sys
MARKERS = {"fear": ["afraid", "scared", "worried", "anxious", "panic", "dread"],
           "anger": ["angry", "furious", "rage", "hate"],
           "greed": ["profit", "lambo", "moon", "pump"],
           "despair": ["lost everything", "broke", "ruined", "scam", "rigged", "stolen"],
           "sunk_cost": ["already put in", "too deep", "all in", "no choice"]}
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: marker_counter.py chat.txt")
    t = open(sys.argv[1]).read().lower()
    tot = 0
    for k, words in MARKERS.items():
        n = sum(len(re.findall(re.escape(w), t)) for w in words)
        tot += n
        print("%-10s %d" % (k + ":", n))
    print("index: %.1f hits/1k chars" % (1000 * tot / max(1, len(t))))
    print("# temperature read only - not a verdict", file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["dossier_skeleton"] = '''#!/usr/bin/env python3
"""Dossier skeleton assembler - markdown case file from CLI fields. Tags: reporting.
Usage: python3 dossier_skeleton.py <subject> <confidence>"""
import sys
from datetime import date
def main():
    if len(sys.argv) < 3:
        sys.exit("usage: dossier_skeleton.py <subject> <confidence>")
    subj, conf = sys.argv[1], sys.argv[2].upper()
    print("# Dossier: %s" % subj)
    print("\\n- Filed: %s | Callsign: %s | Confidence: %s"
          % (date.today().isoformat(), "{{CALLSIGN}}", conf))
    print("\\n## Summary\\n")
    print("\\n## Evidence\\n")
    print("\\n## Links\\n")
    print("\\n## Assessment\\n")
if __name__ == "__main__":
    main()
'''

SCRIPTS["hash_file"] = '''#!/usr/bin/env python3
"""File/string hasher - sha256 and md5. Tags: util.
Usage: python3 hash_file.py <file>   or   python3 hash_file.py -s <string>"""
import hashlib, sys
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: hash_file.py <file> | -s <string>")
    data = sys.argv[2].encode() if sys.argv[1] == "-s" else open(sys.argv[1], "rb").read()
    print("sha256:", hashlib.sha256(data).hexdigest())
    print("md5:   ", hashlib.md5(data).hexdigest())
if __name__ == "__main__":
    main()
'''

SCRIPTS["redact_pii"] = '''#!/usr/bin/env python3
"""PII redactor - masks emails, phones, long tokens in text. Tags: util.
Usage: python3 redact_pii.py [file]   (stdin if no file)"""
import re, sys
def main():
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    src = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", "[EMAIL]", src)
    src = re.sub(r"\\+?\\d[\\d\\s().-]{7,}\\d", "[PHONE]", src)
    src = re.sub(r"\\b[A-Za-z0-9_-]{32,}\\b", "[TOKEN]", src)
    sys.stdout.write(src)
if __name__ == "__main__":
    main()
'''

SCRIPTS["robots_sitemap"] = '''#!/usr/bin/env python3
"""robots.txt and sitemap parser. Tags: recon.
Usage: python3 robots_sitemap.py [domain]   (default: {{DOMAIN}})"""
import re, sys, urllib.request
DOMAIN = "{{DOMAIN}}"
def get(url):
    try:
        return urllib.request.urlopen(url, timeout=20).read().decode("utf8", "replace")
    except Exception as e:
        return "# fetch failed: %s" % e
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    base = "https://" + d
    robots = get(base + "/robots.txt")
    print("## robots.txt"); print(robots[:2000])
    for sm in re.findall(r"Sitemap:\\s*(\\S+)", robots, re.I):
        print("## sitemap:", sm); print(get(sm)[:2000])
if __name__ == "__main__":
    main()
'''

SCRIPTS["header_grab"] = '''#!/usr/bin/env python3
"""HTTP security header checker. Tags: recon.
Usage: python3 header_grab.py <url>"""
import sys, urllib.request
CHECKS = ["content-security-policy", "strict-transport-security",
          "x-content-type-options", "x-frame-options",
          "referrer-policy", "permissions-policy"]
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: header_grab.py <url>")
    try:
        r = urllib.request.urlopen(sys.argv[1], timeout=20)
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    print("status:", r.status)
    hdrs = {k.lower(): v for k, v in r.headers.items()}
    for c in CHECKS:
        print("%-28s %s" % (c, "PRESENT" if c in hdrs else "MISSING"))
if __name__ == "__main__":
    main()
'''

SCRIPTS["spintax_expand"] = '''#!/usr/bin/env python3
"""Spintax expander - {a|b|c} to N variants. Tags: util.
Usage: python3 spintax_expand.py '{Hello|Hi} {there|friend}' [count]"""
import itertools, re, sys
def expand(s, n=5):
    parts = re.split(r"(\\{[^{}]*\\})", s)
    opts = [p[1:-1].split("|") if p.startswith("{") else [p] for p in parts]
    out = []
    for combo in itertools.islice(itertools.product(*opts), n):
        out.append("".join(combo))
    return out
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: spintax_expand.py '{a|b}' [count]")
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    for v in expand(sys.argv[1], n):
        print(v)
if __name__ == "__main__":
    main()
'''

SCRIPTS["ip_rdap"] = '''#!/usr/bin/env python3
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
'''

SCRIPTS["tls_cert_inspect"] = '''#!/usr/bin/env python3
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
'''

SCRIPTS["favicon_hash"] = '''#!/usr/bin/env python3
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
'''

SCRIPTS["wayback_firstseen"] = '''#!/usr/bin/env python3
"""Wayback first-seen - earliest archived snapshot of a URL. Tags: recon.
Usage: python3 wayback_firstseen.py [url]   (default: https://{{DOMAIN}})"""
import json, sys, urllib.request, urllib.parse
DOMAIN = "{{DOMAIN}}"
def main():
    u = sys.argv[1] if len(sys.argv) > 1 else "https://" + DOMAIN
    url = ("https://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(u) +
           "&output=json&filter=statuscode:200&limit=5")
    rows = json.load(urllib.request.urlopen(url, timeout=30))
    if len(rows) < 2:
        sys.exit("no snapshots found for " + u)
    ts = rows[1][1]
    print("url:       ", u)
    print("first seen: %s-%s-%s %s:%s:%s UTC" % (ts[0:4], ts[4:6], ts[6:8], ts[8:10], ts[10:12], ts[12:14]))
    print("snapshot:   https://web.archive.org/web/%s/%s" % (ts, u))
    print("total 200s: %d (capped at 5 shown)" % (len(rows) - 1))
if __name__ == "__main__":
    main()
'''

SCRIPTS["wayback_diff"] = '''#!/usr/bin/env python3
"""Wayback diff - unified diff of a URL between two snapshots. Tags: reporting.
Usage: python3 wayback_diff.py <url> <ts1> <ts2>   (timestamps like 20200101)"""
import difflib, re, sys, urllib.request
def text_of(url):
    html = urllib.request.urlopen(url, timeout=30).read().decode("utf8", "replace")
    html = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", html)
    txt = re.sub(r"<[^>]+>", " ", html)
    txt = re.sub(r"\\s+", " ", txt)
    return [s.strip() for s in txt.split(". ") if s.strip()]
def main():
    if len(sys.argv) < 4:
        sys.exit("usage: wayback_diff.py <url> <ts1> <ts2>")
    u, t1, t2 = sys.argv[1], sys.argv[2], sys.argv[3]
    a = text_of("https://web.archive.org/web/%s/%s" % (t1, u))
    b = text_of("https://web.archive.org/web/%s/%s" % (t2, u))
    diff = list(difflib.unified_diff(a, b, fromfile=t1, tofile=t2, lineterm=""))
    if diff:
        print("\\n".join(diff))
    else:
        print("no text differences")
if __name__ == "__main__":
    main()
'''

SCRIPTS["github_repo_files"] = '''#!/usr/bin/env python3
"""GitHub repo file lister - all files via the git trees API, no token. Tags: recon.
Usage: python3 github_repo_files.py <owner/repo> [branch]"""
import json, sys, urllib.request, urllib.parse
UA = {"User-Agent": "redops-ops/1.0"}
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: github_repo_files.py <owner/repo> [branch]")
    repo = sys.argv[1].strip("/")
    branch = sys.argv[2] if len(sys.argv) > 2 else None
    if not branch:
        r = urllib.request.Request("https://api.github.com/repos/" + repo, headers=UA)
        branch = json.load(urllib.request.urlopen(r, timeout=20))["default_branch"]
    url = ("https://api.github.com/repos/" + repo + "/git/trees/" +
           urllib.parse.quote(branch) + "?recursive=1")
    req = urllib.request.Request(url, headers=UA)
    try:
        tree = json.load(urllib.request.urlopen(req, timeout=30))["tree"]
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    files = sorted(t["path"] for t in tree if t["type"] == "blob")
    for f in files:
        print(f)
    print("files: %d  (branch %s)" % (len(files), branch), file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["email_header_analyze"] = '''#!/usr/bin/env python3
"""Email header analyzer - Received chain, From, auth results from a .eml. Tags: forensics.
Usage: python3 email_header_analyze.py [file.eml]   (stdin if no file)"""
import email, sys
from email import policy
def main():
    raw = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else sys.stdin.buffer.read()
    msg = email.message_from_bytes(raw, policy=policy.default)
    print("From:       ", msg.get("From", "-"))
    print("Return-Path:", msg.get("Return-Path", "-"))
    print("Date:       ", msg.get("Date", "-"))
    print("## Received chain (oldest first)")
    hops = msg.get_all("Received", [])
    for r in reversed(hops):
        print("  " + " ".join(str(r).split()))
    if not hops:
        print("  none")
    print("## Authentication-Results")
    auth = msg.get_all("Authentication-Results", [])
    for a in auth:
        print("  " + " ".join(str(a).split()))
    if not auth:
        print("  none present")
if __name__ == "__main__":
    main()
'''

SCRIPTS["username_platform_check"] = '''#!/usr/bin/env python3
"""Username platform check - GET profile URLs, report HTTP status each. Tags: handles.
Usage: python3 username_platform_check.py <username>"""
import sys, urllib.request, urllib.parse, urllib.error
PLATFORMS = [("Steam", "https://steamcommunity.com/id/{}"),
             ("Xbox", "https://xboxgamertag.com/search/{}"),
             ("PSN", "https://psnprofiles.com/{}"),
             ("Twitch", "https://www.twitch.tv/{}"),
             ("Reddit", "https://www.reddit.com/user/{}"),
             ("GitHub", "https://github.com/{}"),
             ("X", "https://x.com/{}"),
             ("YouTube", "https://www.youtube.com/@{}"),
             ("Instagram", "https://www.instagram.com/{}/"),
             ("TikTok", "https://www.tiktok.com/@{}"),
             ("Pinterest", "https://www.pinterest.com/{}/"),
             ("Spotify", "https://open.spotify.com/user/{}")]
def check(url):
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    try:
        r = urllib.request.urlopen(req, timeout=15)
        extra = "" if r.url == url else " -> " + r.url
        return "HTTP %d%s" % (r.status, extra)
    except urllib.error.HTTPError as e:
        return "HTTP %d" % e.code
    except Exception as e:
        return "ERR %s" % type(e).__name__
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: username_platform_check.py <username>")
    u = urllib.parse.quote(sys.argv[1])
    for name, tpl in PLATFORMS:
        print("%-10s %s" % (name + ":", check(tpl.format(u))))
    print("# status only - a 200 is a lead, not identity proof", file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["ssl_expiry_watch"] = '''#!/usr/bin/env python3
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
'''

SCRIPTS["csp_parse"] = '''#!/usr/bin/env python3
"""CSP parser - fetches Content-Security-Policy, flags weak directives. Tags: recon.
Usage: python3 csp_parse.py <url>"""
import sys, urllib.request
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: csp_parse.py <url>")
    try:
        r = urllib.request.urlopen(sys.argv[1], timeout=20)
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    csp = r.headers.get("Content-Security-Policy")
    if not csp:
        print("CSP: MISSING")
        return
    print("raw:", csp[:400])
    low = csp.lower()
    flags = []
    if "'unsafe-inline'" in low:
        flags.append("unsafe-inline present")
    if "'unsafe-eval'" in low:
        flags.append("unsafe-eval present")
    if " *" in low or low.startswith("*"):
        flags.append("wildcard source")
    if " http:" in low:
        flags.append("plain-http source")
    if "default-src" not in low:
        flags.append("no default-src fallback")
    print("verdict:", "WEAK - " + "; ".join(flags) if flags else "no obvious weaknesses")
if __name__ == "__main__":
    main()
'''

SCRIPTS["redirect_chain"] = '''#!/usr/bin/env python3
"""Redirect chain tracer - manual hop-by-hop, no auto-follow. Tags: recon.
Usage: python3 redirect_chain.py <url>"""
import sys, urllib.request, urllib.parse, urllib.error
class NoFollow(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: redirect_chain.py <url>")
    url = sys.argv[1]
    opener = urllib.request.build_opener(NoFollow)
    for hop in range(10):
        req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
        try:
            r = opener.open(req, timeout=15)
            print("%d. %s -> HTTP %d (final)" % (hop + 1, url, r.status))
            break
        except urllib.error.HTTPError as e:
            loc = e.headers.get("Location")
            print("%d. %s -> HTTP %d -> %s" % (hop + 1, url, e.code, loc))
            if not loc or hop == 9:
                break
            url = urllib.parse.urljoin(url, loc)
if __name__ == "__main__":
    main()
'''

SCRIPTS["page_text_extract"] = '''#!/usr/bin/env python3
"""Page text extractor - strips tags/scripts, prints clean text. Tags: utilities.
Usage: python3 page_text_extract.py <url>"""
import re, sys, urllib.request
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: page_text_extract.py <url>")
    try:
        html = urllib.request.urlopen(sys.argv[1], timeout=20).read().decode("utf8", "replace")
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    html = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", html)
    html = re.sub(r"<!--.*?-->", " ", html)
    txt = re.sub(r"<[^>]+>", " ", html)
    txt = re.sub(r"[ \\t]+", " ", txt)
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    print("\\n".join(lines))
if __name__ == "__main__":
    main()
'''

SCRIPTS["email_auth_summary"] = '''#!/usr/bin/env python3
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
'''

SCRIPTS["handle_similarity"] = '''#!/usr/bin/env python3
"""Handle similarity - difflib pairs >= 0.8 across two lists. Tags: handles.
Usage: python3 handle_similarity.py <list1> <list2>   (files, or comma-separated)"""
import difflib, sys
def load(arg):
    try:
        return [l.strip() for l in open(arg) if l.strip()]
    except OSError:
        return [h.strip() for h in arg.split(",") if h.strip()]
def main():
    if len(sys.argv) < 3:
        sys.exit("usage: handle_similarity.py <list1> <list2>")
    a, b = load(sys.argv[1]), load(sys.argv[2])
    hits = 0
    for x in a:
        for y in b:
            if x.lower() == y.lower():
                continue
            r = difflib.SequenceMatcher(None, x.lower(), y.lower()).ratio()
            if r >= 0.8:
                print("%.2f  %s  <->  %s" % (r, x, y))
                hits += 1
    print("pairs >= 0.80: %d" % hits, file=sys.stderr)
if __name__ == "__main__":
    main()
'''

SCRIPTS["bulk_status"] = '''#!/usr/bin/env python3
"""Bulk URL status - code, final URL, ms for each URL. Tags: utilities.
Usage: python3 bulk_status.py [file] [url ...]   (stdin if nothing given)"""
import sys, time, urllib.request, urllib.error
def check(url):
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    try:
        r = urllib.request.urlopen(req, timeout=15)
        ms = int((time.time() - t0) * 1000)
        return r.status, r.url, ms
    except urllib.error.HTTPError as e:
        return e.code, url, int((time.time() - t0) * 1000)
    except Exception:
        return "ERR", url, int((time.time() - t0) * 1000)
def main():
    urls, args = [], sys.argv[1:]
    if args:
        try:
            urls += [l.strip() for l in open(args[0]) if l.strip()]
            args = args[1:]
        except OSError:
            pass
        urls += args
    if not urls:
        urls = [l.strip() for l in sys.stdin if l.strip()]
    if not urls:
        sys.exit("usage: bulk_status.py [file] [url ...]")
    for u in urls:
        code, final, ms = check(u)
        extra = "" if final == u else "  -> " + final
        print("%-6s %5dms  %s%s" % (code, ms, u, extra))
if __name__ == "__main__":
    main()
'''

SCRIPTS["security_txt"] = '''#!/usr/bin/env python3
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
'''

SCRIPTS["robots_parse"] = '''#!/usr/bin/env python3
"""Robots.txt parser - lists Disallow paths, Sitemaps, rule counts per agent. Tags: recon.
Usage: python3 robots_parse.py [domain]   (default: {{DOMAIN}})"""
import sys, urllib.request, urllib.error
from collections import Counter
DOMAIN = "{{DOMAIN}}"
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    req = urllib.request.Request("https://" + d + "/robots.txt",
                                 headers={"User-Agent": "redops-ops/1.0"})
    try:
        body = urllib.request.urlopen(req, timeout=20).read(262144).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        print("robots.txt: HTTP %d" % e.code)
        return
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    agent, counts, disallows, sitemaps = "*", Counter(), [], []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            agent = v
        elif k == "disallow":
            counts[agent] += 1
            if v:
                disallows.append((agent, v))
        elif k == "sitemap":
            sitemaps.append(v)
    print("robots.txt: %d lines" % len(body.splitlines()))
    print("rules per agent:")
    for a, c in counts.most_common():
        print("  %-22s %d disallows" % (a, c))
    print("disallow paths (%d):" % len(disallows))
    for a, p in disallows[:60]:
        print("  [%s] %s" % (a, p))
    if len(disallows) > 60:
        print("  ... and %d more" % (len(disallows) - 60))
    print("sitemaps (%d):" % len(sitemaps))
    for s in sitemaps:
        print("  " + s)
if __name__ == "__main__":
    main()
'''

SCRIPTS["http_headers_audit"] = '''#!/usr/bin/env python3
"""HTTP security header audit - PASS/MISSING score for security headers. Tags: recon.
Usage: python3 http_headers_audit.py <url>"""
import sys, urllib.request
CHECKS = [
    ("Content-Security-Policy", "blocks XSS / injection"),
    ("Strict-Transport-Security", "forces HTTPS"),
    ("X-Frame-Options", "blocks clickjacking"),
    ("X-Content-Type-Options", "stops MIME sniffing"),
    ("Referrer-Policy", "limits referrer leakage"),
    ("Permissions-Policy", "restricts browser features"),
]
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: http_headers_audit.py <url>")
    req = urllib.request.Request(sys.argv[1], headers={"User-Agent": "redops-ops/1.0"})
    try:
        r = urllib.request.urlopen(req, timeout=20)
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    h, score = r.headers, 0
    for name, why in CHECKS:
        v = h.get(name)
        if v:
            score += 1
            print("PASS    %-28s %s" % (name, v[:80]))
        else:
            print("MISSING %-28s (%s)" % (name, why))
    srv = h.get("Server")
    print("note: Server header discloses '%s'" % srv[:60] if srv else "note: Server header absent (good)")
    print("score: %d/%d" % (score, len(CHECKS)))
if __name__ == "__main__":
    main()
'''

SCRIPTS["tld_variants"] = '''#!/usr/bin/env python3
"""Typosquat watchlist generator - omission, doubling, swaps, ascii lookalikes, TLD swaps. Tags: recon.
Usage: python3 tld_variants.py [domain]   (default: {{DOMAIN}})"""
import sys
DOMAIN = "{{DOMAIN}}"
TLDS = ["com", "net", "org", "io", "co", "info", "biz", "online", "site", "app"]
SWAPS = {"a": ["4", "@"], "e": ["3"], "i": ["1", "l"], "l": ["1", "i"],
         "o": ["0"], "s": ["5", "$"], "t": ["7"], "g": ["9"], "b": ["8"]}
def name_variants(name):
    out = []
    for i in range(len(name)):
        out.append(name[:i] + name[i+1:])
    for i in range(len(name)):
        out.append(name[:i] + name[i] + name[i:])
    for i in range(len(name) - 1):
        out.append(name[:i] + name[i+1] + name[i] + name[i+2:])
    for i, ch in enumerate(name):
        for rep in SWAPS.get(ch.lower(), []):
            out.append(name[:i] + rep + name[i+1:])
    seen, uniq = set(), []
    for v in out:
        if v and v != name and v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq
def main():
    d = (sys.argv[1] if len(sys.argv) > 1 else DOMAIN).lower().strip()
    name, tld = d.rsplit(".", 1) if "." in d else (d, "com")
    n = 0
    for v in name_variants(name):
        n += 1
        print("%3d. %s.%s" % (n, v, tld))
    for t in TLDS:
        if t != tld:
            n += 1
            print("%3d. %s.%s" % (n, name, t))
    print("total: %d candidates" % n)
if __name__ == "__main__":
    main()
'''

SCRIPTS["github_user_repos"] = '''#!/usr/bin/env python3
"""GitHub user repo lister - public repos, stars, language, last updated. No token. Tags: recon.
Usage: python3 github_user_repos.py <username>"""
import json, sys, urllib.request, urllib.parse
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: github_user_repos.py <username>")
    url = "https://api.github.com/users/%s/repos?per_page=100&sort=updated" % urllib.parse.quote(sys.argv[1])
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0",
                                                "Accept": "application/vnd.github+json"})
    try:
        repos = json.load(urllib.request.urlopen(req, timeout=25))
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    if isinstance(repos, dict):
        sys.exit("github says: %s" % repos.get("message", "error"))
    for r in repos:
        print("%-42s stars:%-6d lang:%-12s updated:%s" % (
            r.get("full_name"), r.get("stargazers_count", 0),
            str(r.get("language")), str(r.get("updated_at", ""))[:10]))
    print("total: %d public repos" % len(repos))
if __name__ == "__main__":
    main()
'''

SCRIPTS["sitemap_urls"] = '''#!/usr/bin/env python3
"""Sitemap harvester - fetches /sitemap.xml, follows sitemapindex one level. Tags: recon.
Usage: python3 sitemap_urls.py [domain]   (default: {{DOMAIN}})"""
import re, sys, urllib.request, urllib.error
DOMAIN = "{{DOMAIN}}"
LOC = re.compile(r"<loc>\\s*([^<]+?)\\s*</loc>", re.I)
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "redops-ops/1.0"})
    return urllib.request.urlopen(req, timeout=25).read(4 * 1024 * 1024).decode("utf-8", "replace")
def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DOMAIN
    try:
        xml = get("https://" + d + "/sitemap.xml")
    except urllib.error.HTTPError as e:
        print("sitemap.xml: HTTP %d" % e.code)
        return
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    locs = LOC.findall(xml)
    urls = []
    if "<sitemapindex" in xml.lower():
        print("sitemapindex with %d child sitemaps" % len(locs))
        for sm in locs[:20]:
            try:
                urls.extend(LOC.findall(get(sm)))
            except Exception as e:
                print("  skip %s (%s)" % (sm[:60], e))
    else:
        urls = locs
    print("total urls: %d" % len(urls))
    for u in urls[:50]:
        print(u)
    if len(urls) > 50:
        print("... and %d more" % (len(urls) - 50))
if __name__ == "__main__":
    main()
'''

SCRIPTS["js_endpoints"] = '''#!/usr/bin/env python3
"""JS endpoint extractor - absolute URLs and /api/* paths from a JS file. Tags: recon.
Usage: python3 js_endpoints.py <js-url>"""
import re, sys, urllib.request
ABS = re.compile(r"[\\x22'](https?://[A-Za-z0-9._~:/?#@!$&()*+,;=%-]{4,200})[\\x22']")
API = re.compile(r"[\\x22'](/(?:api|v[0-9]|graphql)[A-Za-z0-9._~:/?#@!$&()*+,;=%-]{1,160})[\\x22']")
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: js_endpoints.py <js-url>")
    req = urllib.request.Request(sys.argv[1], headers={"User-Agent": "redops-ops/1.0"})
    try:
        body = urllib.request.urlopen(req, timeout=25).read(2 * 1024 * 1024).decode("utf-8", "replace")
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    absu = sorted(set(ABS.findall(body)))
    apis = sorted(set(API.findall(body)))
    print("absolute urls (%d):" % len(absu))
    for u in absu[:80]:
        print("  " + u)
    print("api-ish paths (%d):" % len(apis))
    for p in apis[:80]:
        print("  " + p)
if __name__ == "__main__":
    main()
'''

SCRIPTS["meta_extract"] = '''#!/usr/bin/env python3
"""Page metadata extractor - title, description, og: tags, generator. Tags: recon.
Usage: python3 meta_extract.py <url>"""
import html, re, sys, urllib.request
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
META = re.compile(r"<meta\\s+[^>]*>", re.I)
ATTR = re.compile(r"(\\w[\\w:-]*)\\s*=\\s*(?:\\x22([^\\x22]*)\\x22|'([^']*)'|([^\\s>]+))")
WANTED = ("description", "og:description", "og:title", "og:site_name",
          "generator", "author", "keywords", "twitter:description")
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: meta_extract.py <url>")
    req = urllib.request.Request(sys.argv[1], headers={"User-Agent": "redops-ops/1.0"})
    try:
        body = urllib.request.urlopen(req, timeout=25).read(1024 * 1024).decode("utf-8", "replace")
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    m = re.search(r"</head\\s*>", body, re.I)
    head = body[:m.start()] if m else body[:200000]
    t = TITLE.search(head)
    print("title: %s" % (html.unescape(t.group(1).strip()) if t else "(none)"))
    seen = set()
    for tag in META.findall(head):
        attrs = {}
        for k, v1, v2, v3 in ATTR.findall(tag):
            attrs[k.lower()] = v1 or v2 or v3
        name = attrs.get("name", "").lower() or attrs.get("property", "").lower()
        if name in WANTED and name not in seen and "content" in attrs:
            seen.add(name)
            print("%s: %s" % (name, html.unescape(attrs["content"])[:200]))
    if not seen:
        print("(no description/og:/generator meta found)")
if __name__ == "__main__":
    main()
'''

SCRIPTS["ufw_audit"] = '''#!/usr/bin/env python3
"""UFW firewall audit - default policies and overly-permissive rules on this box. Tags: hardening.
Usage: python3 ufw_audit.py"""
import shutil, subprocess

SENSITIVE = {"22": "ssh", "3389": "rdp", "5900": "vnc", "3306": "mysql",
             "5432": "postgres", "6379": "redis", "27017": "mongodb"}

def main():
    ufw = shutil.which("ufw")
    if not ufw:
        print("ufw: NOT INSTALLED on this box (no UFW-managed firewall).")
        print("verdict: UNKNOWN - install ufw or audit the firewall another way.")
        return
    try:
        p = subprocess.run([ufw, "status", "verbose"], capture_output=True,
                           text=True, timeout=20)
    except Exception as e:
        print("could not run ufw: %s" % e)
        return
    if "need to be root" in (p.stderr or "").lower():
        print("ufw: permission denied - re-run with sudo for a real audit.")
        print("verdict: UNKNOWN - insufficient privileges.")
        return
    lines = p.stdout.splitlines()
    if not lines:
        print("ufw: no output - is the service usable here?")
        return
    print("status line: %s" % lines[0].strip())
    if "inactive" in lines[0].lower():
        print("verdict: WARN - firewall is INACTIVE; no rules are enforced.")
        return
    warns = 0
    for ln in lines:
        if ln.startswith("Default:"):
            print(ln.strip())
            if "deny (incoming)" in ln:
                print("  -> PASS: default incoming policy is deny")
            else:
                print("  -> WARN: default incoming policy is not deny")
                warns += 1
    print("")
    print("%-22s %-10s %s" % ("TO", "ACTION", "FROM"))
    for ln in lines:
        parts = ln.split()
        if len(parts) >= 4 and parts[1] in ("ALLOW", "DENY", "REJECT", "LIMIT") \
                and parts[2] in ("IN", "OUT"):
            to = parts[0]
            action = parts[1] + " " + parts[2]
            frm = " ".join(parts[3:])
            port = to.split("/")[0].split(",")[0]
            flag = ""
            if frm.lower().startswith("anywhere") and port in SENSITIVE:
                flag = "  <-- WARN: %s open to anywhere" % SENSITIVE[port]
                warns += 1
            print("%-22s %-10s %s%s" % (to, action, frm, flag))
    print("")
    if warns:
        print("verdict: WARN - %d rule(s) to tighten" % warns)
    else:
        print("verdict: PASS - no overly-permissive rules found")

if __name__ == "__main__":
    main()
'''

SCRIPTS["ssh_audit"] = '''#!/usr/bin/env python3
"""sshd_config audit - PASS/WARN per hardening-relevant setting. Tags: hardening.
Usage: python3 ssh_audit.py [/path/to/sshd_config]"""
import os, sys

CHECKS = [
    ("permitrootlogin", ("no", "prohibit-password", "forced-commands-only"),
     "WARN", "root login should be 'no'"),
    ("passwordauthentication", ("no",), "WARN", "prefer key-only auth"),
    ("permitemptypasswords", ("no",), "WARN", "never allow empty passwords"),
    ("x11forwarding", ("no",), "INFO", "disable unless X11 is needed"),
    ("maxauthtries", None, "INFO", "lower is better (sshd default is 6)"),
    ("protocol", ("2",), "WARN", "protocol 1 is broken"),
    ("pubkeyauthentication", ("yes",), "INFO", "key auth should stay on"),
    ("challengeresponseauthentication", ("no",), "INFO", "disable unless needed"),
]

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "/etc/ssh/sshd_config"
    if not os.path.isfile(path):
        print("sshd_config not found at %s" % path)
        print("hint: ssh_audit.py /path/to/sshd_config")
        print("verdict: UNKNOWN - file not found.")
        return
    try:
        with open(path) as f:
            raw = f.read().splitlines()
    except PermissionError:
        print("permission denied reading %s - try sudo." % path)
        print("verdict: UNKNOWN - insufficient privileges.")
        return
    except OSError as e:
        print("could not read %s: %s" % (path, e))
        return
    vals = {}
    for ln in raw:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split(None, 1)
        if len(parts) == 2:
            vals.setdefault(parts[0].lower(), parts[1].strip())
    if not vals:
        print("no active directives parsed (file may be all comments).")
    bad = 0
    print("%-30s %-14s %s" % ("SETTING", "VALUE", "RESULT"))
    for directive, good, sev, note in CHECKS:
        v = vals.get(directive)
        if v is None:
            print("%-30s %-14s %s" % (directive, "(unset)", "INFO - using sshd default; " + note))
            continue
        if good is None:
            print("%-30s %-14s %s" % (directive, v, "INFO - " + note))
        elif v.lower() in good:
            print("%-30s %-14s %s" % (directive, v, "PASS"))
        else:
            print("%-30s %-14s %s" % (directive, v, sev + " - " + note))
            if sev == "WARN":
                bad += 1
    print("")
    if bad:
        print("verdict: WARN - %d setting(s) to tighten" % bad)
    else:
        print("verdict: PASS - key settings look hardened")

if __name__ == "__main__":
    main()
'''

SCRIPTS["entropy_audit"] = '''#!/usr/bin/env python3
"""Draw randomness audit - chi-square, runs test, mean/variance sanity. Tags: hardening.
Usage: cat draws.txt | python3 entropy_audit.py [file]   (one number per line)"""
import math, sys

def read_vals(src):
    vals = []
    for tok in src.read().replace(",", " ").split():
        try:
            vals.append(float(tok))
        except ValueError:
            pass
    return vals

def chi_square(vals, bins=10):
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return None
    counts = [0] * bins
    for v in vals:
        i = min(int((v - lo) / (hi - lo) * bins), bins - 1)
        counts[i] += 1
    exp = len(vals) / bins
    return sum((c - exp) ** 2 / exp for c in counts)

def runs_test(vals):
    n = len(vals)
    if n < 20:
        return None
    dirs = []
    for i in range(1, n):
        if vals[i] > vals[i - 1]:
            dirs.append(1)
        elif vals[i] < vals[i - 1]:
            dirs.append(-1)
    m = len(dirs)
    if m < 10:
        return None
    runs = 1
    for i in range(1, m):
        if dirs[i] != dirs[i - 1]:
            runs += 1
    expected = (2 * m - 1) / 3.0
    var = (16 * m - 29) / 90.0
    z = (runs - expected) / math.sqrt(var)
    return runs, expected, z

def main():
    close = False
    if len(sys.argv) > 1:
        try:
            src = open(sys.argv[1])
        except OSError as e:
            sys.exit("cannot open %s: %s" % (sys.argv[1], e))
        close = True
    else:
        src = sys.stdin
    try:
        vals = read_vals(src)
    finally:
        if close:
            src.close()
    print("values: %d" % len(vals))
    if len(vals) < 50:
        print("need at least 50 values for a meaningful audit.")
        return
    chi = chi_square(vals)
    if chi is None:
        print("chi-square: SKIPPED - all values identical (broken RNG or constant input)")
    else:
        print("chi-square (10 bins, df=9): %.2f" % chi)
        if chi > 21.67:
            print("  -> SKEWED at 99% level (critical 21.67)")
        elif chi > 16.92:
            print("  -> SUSPECT at 95% level (critical 16.92)")
        else:
            print("  -> consistent with uniform")
    r = runs_test(vals)
    if r is None:
        print("runs test: skipped (need >=20 values)")
    else:
        runs, exp, z = r
        print("runs test: %d runs (expected %.1f), z=%.2f" % (runs, exp, z))
        if abs(z) > 2.58:
            print("  -> SUSPECT ordering pattern (|z|>2.58)")
        else:
            print("  -> no trend detected")
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    print("mean: %.4f  variance: %.4f  min: %g  max: %g"
          % (mean, var, min(vals), max(vals)))

if __name__ == "__main__":
    main()
'''

SCRIPTS["bonus_abuse_hunt"] = '''#!/usr/bin/env python3
"""Bonus-abuse hunt - win-stacking, round-amount clustering, velocity spikes. Tags: hardening.
Usage: python3 bonus_abuse_hunt.py payouts.csv   (stdin ok; columns: user_id,amount,timestamp)"""
import csv, sys
from collections import defaultdict
from datetime import datetime, timedelta

def parse_ts(s):
    s = s.strip()
    try:
        return datetime.utcfromtimestamp(float(s))
    except (ValueError, OverflowError):
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def window_flags(evs, hours, limit, label):
    evs = sorted(evs, key=lambda x: x[1])
    for i in range(len(evs)):
        j = i
        while j < len(evs) and evs[j][1] - evs[i][1] <= timedelta(hours=hours):
            j += 1
        if j - i > limit:
            return (j - i, evs[i][1])
    return None

def main():
    close = False
    if len(sys.argv) > 1:
        try:
            src = open(sys.argv[1], newline="")
        except OSError as e:
            sys.exit("cannot open %s: %s" % (sys.argv[1], e))
        close = True
    else:
        src = sys.stdin
    rows, skipped = [], 0
    for rec in csv.reader(src):
        if len(rec) < 3 or not rec[0].strip():
            skipped += 1
            continue
        try:
            amt = float(rec[1])
        except ValueError:
            skipped += 1
            continue
        ts = parse_ts(rec[2])
        if ts is None:
            skipped += 1
            continue
        rows.append((rec[0].strip(), amt, ts))
    if close:
        src.close()
    print("payouts parsed: %d (skipped %d)" % (len(rows), skipped))
    if not rows:
        return
    by_user = defaultdict(list)
    for u, a, t in rows:
        by_user[u].append((a, t))

    print("\\n[a] users with >3 wins in 24h:")
    found = False
    for u in sorted(by_user):
        hit = window_flags(by_user[u], 24, 3, "wins")
        if hit:
            print("  FLAG %s: %d wins in 24h (from %s)" % (u, hit[0], hit[1].isoformat()))
            found = True
    if not found:
        print("  clean")

    print("\\n[b] round-number amount clustering:")
    roundn = [r for r in rows if r[1] > 0 and r[1] == int(r[1])]
    pct = 100.0 * len(roundn) / len(rows)
    print("  %.1f%% of payouts are whole numbers (%d/%d)" % (pct, len(roundn), len(rows)))
    if pct > 80 and len(rows) >= 20:
        print("  FLAG: heavy round-number clustering (bot-like or manual batching)")
    else:
        print("  ok")

    print("\\n[c] velocity spikes (>5 payouts to one user in an hour):")
    found = False
    for u in sorted(by_user):
        hit = window_flags(by_user[u], 1, 5, "payouts")
        if hit:
            print("  FLAG %s: %d payouts within an hour (from %s)" % (u, hit[0], hit[1].isoformat()))
            found = True
    if not found:
        print("  clean")

if __name__ == "__main__":
    main()
'''

SCRIPTS["dangling_dns"] = '''#!/usr/bin/env python3
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
        for n in str(r.get("name_value", "")).split("\\n"):
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
'''

SCRIPTS["ct_watch"] = '''#!/usr/bin/env python3
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
        issuer = (r.get("issuer_name") or "").replace("\\n", " ")
        sans = str(r.get("name_value", "")).replace("\\n", ", ")
        print("%s  id=%s" % (nb.strftime("%Y-%m-%d"), r.get("id")))
        print("   issuer: %s" % issuer[:120])
        print("   SANs: %s" % sans[:200])
    if len(certs) > 50:
        print("... and %d more" % (len(certs) - 50))
    print("")
    print("verify every issuer/SAN above - anything unrecognized may be rogue.")

if __name__ == "__main__":
    main()
'''

TAGS = {
    "ufw_audit": (["hardening"], "UFW firewall audit", "Default policies and overly-permissive rules on this box."),
    "ssh_audit": (["hardening"], "SSH config audit", "PASS/WARN per sshd setting: root login, passwords, forwarding."),
    "entropy_audit": (["hardening"], "Draw randomness audit", "Chi-square, runs test, and mean/variance for game draws."),
    "bonus_abuse_hunt": (["hardening"], "Bonus-abuse hunt", "Win-stacking, round-amount clustering, velocity spikes in payouts."),
    "dangling_dns": (["hardening"], "Dangling-DNS finder", "CNAMEs from crt.sh subdomains; flags third-party targets to verify."),
    "ct_watch": (["hardening"], "CT log watch", "Certs issued for your domain in the last 30 days, newest first."),
    "security_txt": (["recon"], "Security.txt checker", "Fetches /.well-known/security.txt and prints contacts and policy."),
    "robots_parse": (["recon"], "Robots.txt parser", "Disallow lines, sitemap URLs, and rule counts per user-agent."),
    "http_headers_audit": (["recon"], "HTTP header audit", "PASS/MISSING score for security headers on any URL."),
    "tld_variants": (["recon"], "Typosquat watchlist", "Lookalike domain variants: omissions, swaps, TLD changes."),
    "github_user_repos": (["recon"], "GitHub user repos", "Public repos for a username: stars, language, last updated. No token."),
    "sitemap_urls": (["recon"], "Sitemap harvester", "All URLs from /sitemap.xml, following sitemapindex one level."),
    "js_endpoints": (["recon"], "JS endpoint extractor", "Absolute URLs and /api/* paths hidden in a JavaScript file."),
    "meta_extract": (["recon"], "Page metadata extractor", "Title, description, og: tags, and generator from any page."),
    "subdomains_crt": (["recon"], "Subdomain enumerator", "Pull subdomains for a domain from certificate transparency logs."),
    "rdap_lookup": (["recon"], "RDAP domain lookup", "Registrar, creation date, and status for any domain."),
    "doh_resolve": (["recon"], "DNS-over-HTTPS resolver", "Resolve A/AAAA/MX/TXT records without touching local DNS."),
    "handle_variants": (["handles"], "Handle variant generator", "15 likely alias spellings for one handle."),
    "email_permutations": (["handles"], "Email permutation generator", "Likely address patterns for a first/last name."),
    "dork_pack": (["handles"], "Dork pack generator", "12 search queries targeting one handle across the web."),
    "ig_handle_extract": (["handles"], "IG handle extractor", "Pull @handles out of pasted HTML or text."),
    "snowflake_time": (["util"], "Discord snowflake decoder", "Snowflake IDs to UTC timestamps."),
    "exif_gps": (["forensics"], "EXIF GPS extractor", "Coordinates hidden in a JPEG, printed with a Maps link."),
    "pdf_metadata": (["forensics"], "PDF metadata extractor", "Author, creator, timestamps from a PDF's plain-text metadata."),
    "chisq_uniform": (["forensics"], "Chi-square uniformity test", "Is a list of winners consistent with a fair draw?"),
    "withdrawal_delays": (["forensics"], "Withdrawal delay analyzer", "Average/median/max payout delays from a CSV, flags slow rows."),
    "fee_outliers": (["forensics"], "Fee outlier finder", "Flags transactions charging far above the average fee."),
    "timeline_build": (["reporting"], "Timeline builder", "CSV of date,event rows into a clean markdown timeline."),
    "url_extract": (["handles"], "URL extractor", "Dedupe every link hiding in a block of text."),
    "platform_urls": (["handles"], "Platform URL builder", "One username to profile URLs on 8 platforms. Links only."),
    "wayback_list": (["recon"], "Wayback snapshot lister", "Archived snapshots of a domain via the CDX API."),
    "certspotter_poll": (["recon"], "Certificate transparency poller", "Diff today's subdomains against a baseline file."),
    "marker_counter": (["forensics"], "Keyword marker counter", "Fear/greed/despair signal counts in chat exports."),
    "dossier_skeleton": (["reporting"], "Dossier skeleton assembler", "A clean markdown case-file scaffold in one command."),
    "hash_file": (["util"], "File/string hasher", "SHA-256 and MD5 for integrity checks."),
    "redact_pii": (["util"], "PII redactor", "Masks emails, phones, and tokens before anything leaves the box."),
    "robots_sitemap": (["recon"], "robots.txt + sitemap parser", "What the site tells crawlers, verbatim."),
    "header_grab": (["recon"], "HTTP security header checker", "Which security headers a site sends or skips."),
    "spintax_expand": (["util"], "Spintax expander", "{a|b|c} templates into N plain variants."),
    "ip_rdap": (["recon"], "IP RDAP lookup", "Network name, country, and entities for any IPv4/IPv6 address."),
    "tls_cert_inspect": (["recon"], "TLS certificate inspector", "Subject, issuer, SANs, and days-to-expiry from a live TLS handshake."),
    "favicon_hash": (["recon"], "Favicon hasher", "SHA-256 plus murmur3-32 of a site's favicon for infrastructure matching."),
    "wayback_firstseen": (["recon"], "Wayback first-seen", "Earliest archived snapshot date for any URL."),
    "wayback_diff": (["reporting"], "Wayback diff", "Unified text diff of a page between two archive timestamps."),
    "github_repo_files": (["recon"], "GitHub repo file lister", "Every file in a public repo via the git trees API, no token needed."),
    "email_header_analyze": (["forensics"], "Email header analyzer", "Received chain and SPF/DKIM/DMARC results from a saved .eml."),
    "username_platform_check": (["handles"], "Username platform check", "Live HTTP status for a handle across 12 platforms. Status only."),
    "ssl_expiry_watch": (["recon"], "SSL expiry watch", "Days-to-expiry per host, flags anything under 30 days."),
    "csp_parse": (["recon"], "CSP parser", "Fetches Content-Security-Policy and flags unsafe-inline, wildcards, and gaps."),
    "redirect_chain": (["recon"], "Redirect chain tracer", "Hop-by-hop redirect path with the status code at each hop."),
    "page_text_extract": (["utilities"], "Page text extractor", "Clean readable text from any URL, tags and scripts stripped."),
    "email_auth_summary": (["recon"], "Email auth summary", "MX, SPF, DKIM, and DMARC for a domain in one DoH pass."),
    "handle_similarity": (["handles"], "Handle similarity", "Fuzzy-matches two handle lists, prints pairs scoring 0.80 or more."),
    "bulk_status": (["utilities"], "Bulk URL status", "Status code, final URL, and latency for a list of URLs."),
}

written, failed = 0, []
for sid, code in SCRIPTS.items():
    path = os.path.join(BASE, sid + ".py")
    with open(path, "w") as f:
        f.write(code)
    try:
        py_compile.compile(path, doraise=True)
        written += 1
    except py_compile.PyCompileError as e:
        failed.append((sid, str(e)))

print("wrote %d scripts, compile failures: %d" % (written, len(failed)))
for sid, err in failed:
    print("FAIL", sid, err)

import json
meta = [{"id": sid, "tags": TAGS[sid][0], "name": TAGS[sid][1], "desc": TAGS[sid][2],
         "code": SCRIPTS[sid]} for sid in SCRIPTS]
with open(os.path.join(BASE, "index.json"), "w") as f:
    json.dump(meta, f)
print("index.json written:", len(meta), "entries")
