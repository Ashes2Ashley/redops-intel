#!/bin/bash
# deploy-all.sh — REDOPS one-command deploy pipeline.
# Rebuilds, verifies, deploys redops-intel, then proves the live site works.
# Usage: bash ~/workspace/redops-intel/deploy-all.sh
# Fails LOUDLY on any step. Safe to re-run.
set -euo pipefail

BASE="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE"

echo "=== [1/6] build ==="
python3 build.py
echo "=== [2/6] assemble ==="
python3 assemble.py
echo "=== [3/6] syntax check ==="
node --check worker.js
echo "=== [4/6] deploy ==="
python3 deploy.py 2>/dev/null | grep -v "route:" | grep -v "TEAM-KEY" || true

echo "=== [5/6] waiting for edge propagation (25s) ==="
sleep 25

echo "=== [6/6] live verification ==="
fail=0

# master key must ALWAYS work (stable across deploys; read from local file, never hardcoded)
mkey=$(cat ~/workspace/redops-intel/master-key.txt 2>/dev/null)
code=$(curl -s --max-time 30 -X POST --data-urlencode "pass=$mkey" https://intel.kodakgp.com/login -c /tmp/redops_deploy_cj.txt -o /dev/null -w "%{http_code}")
if [ "$code" = "302" ]; then echo "OK   master key login -> 302"; else echo "FAIL master key login -> $code"; fail=1; fi

code=$(curl -s --max-time 30 -b /tmp/redops_deploy_cj.txt https://intel.kodakgp.com/api/watch -o /dev/null -w "%{http_code}")
if [ "$code" = "200" ]; then echo "OK   master session /api/watch -> 200"; else echo "FAIL master session -> $code"; fail=1; fi

# team passphrase rotates every deploy — verify the CURRENT one
if [ -f team-key.txt ]; then
  PW=$(cat team-key.txt)
  code=$(curl -s --max-time 30 -X POST --data-urlencode "pass=$PW" https://intel.kodakgp.com/login -o /dev/null -w "%{http_code}")
  if [ "$code" = "302" ]; then echo "OK   team passphrase login -> 302"; else echo "FAIL team passphrase -> $code"; fail=1; fi
else
  echo "WARN team-key.txt missing — cannot verify team passphrase"; fail=1
fi

# dashboard page serves with the mask + maxmode
code=$(curl -s --max-time 30 -b /tmp/redops_deploy_cj.txt https://intel.kodakgp.com/ -o /tmp/redops_deploy_page.html -w "%{http_code}")
if [ "$code" = "200" ]; then echo "OK   dashboard page -> 200"; else echo "FAIL dashboard page -> $code"; fail=1; fi
for marker in 'id="maxmode"' 'id="t-extw"' 'id="t-extg"' 'maskbreathe'; do
  if grep -q "$marker" /tmp/redops_deploy_page.html; then echo "OK   page contains $marker"; else echo "FAIL page missing $marker"; fail=1; fi
done

# rate limit sanity: login page still served
code=$(curl -s --max-time 30 https://intel.kodakgp.com/login -o /dev/null -w "%{http_code}")
if [ "$code" = "200" ]; then echo "OK   lock page -> 200"; else echo "FAIL lock page -> $code"; fail=1; fi

echo ""
if [ "$fail" = "0" ]; then
  echo "DEPLOY COMPLETE — all checks green."
  echo "(access codes are never printed — see team-key.txt on this machine only)"
else
  echo "DEPLOY VERIFICATION FAILED — see FAIL lines above."
  exit 1
fi
