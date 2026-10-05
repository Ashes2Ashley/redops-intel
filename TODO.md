# REDOPS TODO

- [ ] Upgrade team auth to Cloudflare Access (email allow-list) for team use
- [ ] data.json refresh pipeline — dossiers are a point-in-time snapshot;
      automate re-runs of the recon suite into fresh case files
- [ ] Fortress: remediate the live baseline findings in order —
      game-site response headers first, then DMARC, then CSP/HSTS
- [ ] Scheduled rotation for INTEL_PASS / MASTER_KEY
      (currently generated once and reused)
- [ ] Master-key login is now backed by the MASTER_KEY Worker secret;
      the old hardcoded value is dead and purged from history
