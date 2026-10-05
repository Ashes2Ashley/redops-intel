#!/usr/bin/env python3
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
