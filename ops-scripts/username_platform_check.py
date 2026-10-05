#!/usr/bin/env python3
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
