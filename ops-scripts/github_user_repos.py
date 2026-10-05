#!/usr/bin/env python3
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
