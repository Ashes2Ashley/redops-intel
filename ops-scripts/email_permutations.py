#!/usr/bin/env python3
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
