#!/usr/bin/env python3
"""Deploy redops-intel worker: upload script, set passphrase secret, attach custom domain."""
import json, os, secrets, sys, urllib.request, urllib.error

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
import dynamic_credentials as dc

ACCT = "3d6c06df593089a953cc119dd6faf6be"
SCRIPT = "redops-intel"
HOST = "intel.kodakgp.com"
BASE = os.path.dirname(os.path.abspath(__file__))

def call(method, path, body=None, ctype="application/json"):
    url = "https://api.cloudflare.com" + path
    data = body.encode("utf-8") if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, method=method,
        headers={"Content-Type": ctype, "User-Agent": "muse-redops-deploy"})
    dc.add_surrogate_to_request(req, "custom.cloudflare",
                                allowed_hosts=["api.cloudflare.com"])
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return dc.read_json_response(resp)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} on {method} {path}: {e.read().decode()[:500]}",
              file=sys.stderr)
        sys.exit(1)

# 1. upload worker script as ES module (multipart + metadata)
import uuid
js = open(os.path.join(BASE, "worker.js"), encoding="utf-8").read()
boundary = "----muse" + uuid.uuid4().hex
meta = json.dumps({"main_module": "worker.js"}).encode()
parts = []
parts.append(("--" + boundary + '\r\nContent-Disposition: form-data; name="metadata"\r\n'
               'Content-Type: application/json\r\n\r\n').encode() + meta + b"\r\n")
parts.append(("--" + boundary + '\r\nContent-Disposition: form-data; name="worker.js"; filename="worker.js"\r\n'
               'Content-Type: application/javascript+module\r\n\r\n').encode()
             + js.encode() + b"\r\n")
parts.append(("--" + boundary + "--\r\n").encode())
body = b"".join(parts)
r = call("PUT", f"/client/v4/accounts/{ACCT}/workers/scripts/{SCRIPT}", body,
         "multipart/form-data; boundary=" + boundary)
print("upload:", r.get("success"))

# 2. passphrase secret (reuse existing team key so the crew isn't locked out)
keyfile = os.path.join(BASE, "team-key.txt")
if os.path.exists(keyfile):
    pw = open(keyfile).read().strip()
else:
    pw = secrets.token_urlsafe(18)
    open(keyfile, "w").write(pw + "\n")
r = call("PUT", f"/client/v4/accounts/{ACCT}/workers/scripts/{SCRIPT}/secrets",
         json.dumps({"name": "INTEL_PASS", "text": pw, "type": "secret_text"}))
print("secret_set:", r.get("success"))

# 2b. master key secret (generate once, reuse; never printed, never in repo)
mkeyfile = os.path.join(BASE, "master-key.txt")
if os.path.exists(mkeyfile):
    mkey = open(mkeyfile).read().strip()
else:
    mkey = secrets.token_urlsafe(24)
    open(mkeyfile, "w").write(mkey + "\n")
r = call("PUT", f"/client/v4/accounts/{ACCT}/workers/scripts/{SCRIPT}/secrets",
         json.dumps({"name": "MASTER_KEY", "text": mkey, "type": "secret_text"}))
print("master_secret_set:", r.get("success"))

# 3. attach intel.kodakgp.com via zone route + DNS (best-effort; the domain is
# already bound via dashboard, so a 403 here is fine)
ZONE = "af4c9924aae3cf8b1df792cfeb51ba71"
try:
    r = call("POST", f"/client/v4/zones/{ZONE}/workers/routes",
             json.dumps({"pattern": "intel.kodakgp.com/*", "script": SCRIPT}))
    print("route:", r.get("success"))
except SystemExit:
    print("route: skipped (already bound via dashboard)")
