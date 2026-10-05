#!/usr/bin/env python3
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
