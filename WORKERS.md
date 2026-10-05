# REDOPS worker operations — HOWTO

## One-command deploy

```bash
bash ~/workspace/redops-intel/deploy-all.sh
```

That single command runs the full pipeline and proves the result:

1. **build** — compiles the dashboard from `template.html` + `data.json`
2. **assemble** — injects the app, login gate, baselines and secrets wiring into `worker.js`
3. **syntax check** — `node --check` on the worker (a broken script never ships)
4. **deploy** — uploads to Cloudflare (`redops-intel` on the account), sets secrets
5. **propagation wait** — 25s for the edge to converge
6. **live verification** — master-key login, session API call, team-passphrase login,
   dashboard page fetch, marker checks (`maxmode`, both External tabs, mask),
   lock-page check. Any failure aborts LOUDLY.

## Passphrases

- **Team passphrase is generated once and reused.** It is created on the first
  deploy and stored in `~/workspace/redops-intel/team-key.txt`; later deploys
  keep the same one (delete that file to force a fresh one). It is never
  printed — read it from that file on this machine only.
  Your old browser session stops working after a deploy — sign in again.
- **Master key never changes.** It survives every deploy and is the stable way
  back in. The verification step tests it every run.

## Rollback

If a deploy ever misbehaves: Cloudflare dashboard → Workers & Pages →
`redops-intel` → Deployments → pick the previous version → Rollback.
The 15-minute watch cron survives deploys untouched.

## Enrolling another worker in this pipeline

Today the pipeline manages `redops-intel` (the only worker whose source lives here).
To enroll another worker (e.g. one of the `runehall-*` workers):

1. Put its source in `~/workspace/workers/<name>/` with its own `deploy.py`
   (copy the pattern from `~/workspace/redops-intel/deploy.py`).
2. Add a matching verify block to `deploy-all.sh` (login/endpoint check).
3. List it in the Linked Workers tab data (`EXTW` in `template.html`) if it should
   appear in the dashboard.

## OPSEC posture of the intel worker

- Every route except `/login` requires the team cookie or master-key session.
  APIs return `401 unauthorized` without it; the dashboard 302-redirects to `/login`.
- The lock page is deliberately bland ("Restricted — Authorized access only").
  It advertises nothing about REDOPS.
- `/login` is rate-limited: >12 failed attempts per IP per 5 minutes → `429`
  for 5 minutes. Brute force is impractical.
- Responses carry `nosniff`, `DENY` framing, `no-referrer`, and a strict CSP.
- Intel data (`data.json`) is baked into the worker and only served post-auth.
- The Discord webhook secret lives as a worker secret, never in the page.
- Residual exposure to close (Cloudflare dashboard, one minute):
  Workers & Pages → `redops-intel` → Settings → **disable `workers.dev`**
  so the worker is reachable ONLY via `intel.kodakgp.com`.
