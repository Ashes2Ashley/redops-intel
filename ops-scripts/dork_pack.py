#!/usr/bin/env python3
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
