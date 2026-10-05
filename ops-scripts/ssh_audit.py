#!/usr/bin/env python3
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
