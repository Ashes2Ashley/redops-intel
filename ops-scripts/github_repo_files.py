#!/usr/bin/env python3
"""GitHub repo file lister - all files via the git trees API, no token. Tags: recon.
Usage: python3 github_repo_files.py <owner/repo> [branch]"""
import json, sys, urllib.request, urllib.parse
UA = {"User-Agent": "redops-ops/1.0"}
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: github_repo_files.py <owner/repo> [branch]")
    repo = sys.argv[1].strip("/")
    branch = sys.argv[2] if len(sys.argv) > 2 else None
    if not branch:
        r = urllib.request.Request("https://api.github.com/repos/" + repo, headers=UA)
        branch = json.load(urllib.request.urlopen(r, timeout=20))["default_branch"]
    url = ("https://api.github.com/repos/" + repo + "/git/trees/" +
           urllib.parse.quote(branch) + "?recursive=1")
    req = urllib.request.Request(url, headers=UA)
    try:
        tree = json.load(urllib.request.urlopen(req, timeout=30))["tree"]
    except Exception as e:
        sys.exit("fetch failed: %s" % e)
    files = sorted(t["path"] for t in tree if t["type"] == "blob")
    for f in files:
        print(f)
    print("files: %d  (branch %s)" % (len(files), branch), file=sys.stderr)
if __name__ == "__main__":
    main()
