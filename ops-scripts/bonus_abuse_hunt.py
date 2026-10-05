#!/usr/bin/env python3
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

    print("\n[a] users with >3 wins in 24h:")
    found = False
    for u in sorted(by_user):
        hit = window_flags(by_user[u], 24, 3, "wins")
        if hit:
            print("  FLAG %s: %d wins in 24h (from %s)" % (u, hit[0], hit[1].isoformat()))
            found = True
    if not found:
        print("  clean")

    print("\n[b] round-number amount clustering:")
    roundn = [r for r in rows if r[1] > 0 and r[1] == int(r[1])]
    pct = 100.0 * len(roundn) / len(rows)
    print("  %.1f%% of payouts are whole numbers (%d/%d)" % (pct, len(roundn), len(rows)))
    if pct > 80 and len(rows) >= 20:
        print("  FLAG: heavy round-number clustering (bot-like or manual batching)")
    else:
        print("  ok")

    print("\n[c] velocity spikes (>5 payouts to one user in an hour):")
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
