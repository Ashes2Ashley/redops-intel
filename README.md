# REDOPS Intel — locked team dashboard (Cloudflare Worker)

`redops-intel` serves the REDOPS intelligence dashboard: mission board, case
dossiers, people search, relationship map, link vault, dork builder, timeline,
plus the Set Kit, War Room, and Fortress stations.

Live at: `https://shemhamforash.cloutscape.org/` (backup: `https://intel.kodakgp.com/`)

## Layout

```
redops-intel/
├── template.html     # dashboard source (all stations)
├── login.html        # passphrase gate page
├── assemble.py       # SOURCE OF TRUTH — rebuilds worker.js from template
├── worker.js         # generated; do not edit directly (assemble overwrites)
├── build.py          # build step
├── deploy.py         # upload worker + set INTEL_PASS secret + attach routes
├── deploy-all.sh     # full pipeline: build → assemble → check → deploy → verify
├── data.json         # case dossiers embedded in the dashboard
├── ops-scripts/      # defensive hardening/audit scripts served by Fortress
├── make_ops_scripts.py
├── war-batch2.inc / war-room-test.js
└── baseline.json
```

## Auth

Passphrase gate (cookie `ro_auth`, HttpOnly/Secure/SameSite=Strict).
The passphrase is stored as the Worker secret `INTEL_PASS` (set by `deploy.py`);
the team copy is kept out of this repo.

## Rebuild / redeploy

```bash
cd ~/workspace/redops-intel && python3 build.py && python3 assemble.py && python3 deploy.py
```

`assemble.py` rebuilds `worker.js` from its inline template on every deploy —
direct edits to `worker.js` are wiped. The login page lives in `login.html`;
`/api/*` endpoints live in the `assemble.py` template.

## Stations (plain-English name / codename)

- Mission Board / overview — stats + ranked watch list (live `/api/pulse|watch|dns`)
- Case Files / dossiers — full case reports with confidence grades
- People Search / trace — full-text search across all dossiers
- Relationship Map / web — per-individual matrix tables
- Link Vault / urls — URLs with context
- Dork Builder / dork forge — handle → Google dorks as clickable links
- Timeline / history — domain/infra timeline
- Set Kit — Vector Forge, Conditioning Lab, Script Vault, Offline Field Agent, Voice Lab
- War Room — triaged 100-item arsenal (defensive planning only)
- Fortress — edge-posture table, hardening checklist, defensive scripts

Every finding carries a confidence label: VERIFIED / CORROBORATED / DEBUNKED /
STALE / UNVERIFIABLE / CONTESTED / LEAD. No mock data.
