#!/usr/bin/env python3
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
        if len(parts) >= 4 and parts[1] in ("ALLOW", "DENY", "REJECT", "LIMIT")                 and parts[2] in ("IN", "OUT"):
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
