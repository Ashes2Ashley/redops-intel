#!/usr/bin/env python3
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
