#!/usr/bin/env python3
"""Assemble worker.js: passphrase gate + dashboard."""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(BASE, "template.html"), encoding="utf-8").read()
data = open(os.path.join(BASE, "data.json"), encoding="utf-8").read()
json.loads(data)  # validate

LOGIN = open(os.path.join(BASE, "login.html"), encoding="utf-8").read()

worker = """const DATA = __DATA__;
const APP_HTML = __APP__;
const LOGIN_HTML = __LOGIN__;

function seq(a, b) {
  a = String(a); b = String(b);
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}
function authed(req, PASS, MASTER) {
  const c = req.headers.get("Cookie") || "";
  const m = c.match(/(?:^|;\\s*)ro_auth=([^;]+)/);
  if (!m) return false;
  const v = decodeURIComponent(m[1]);
  return (MASTER && seq(v, MASTER)) || (PASS && seq(v, PASS));
}
const SEC = "max-age=2592000; Path=/; HttpOnly; Secure; SameSite=Strict";
const SECH = { "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer" };
const RL = new Map();
function rlAllow(ip){ const now=Date.now(); let e=RL.get(ip);
  if(e && e.ban>now) return false;
  if(!e || now-e.t0>300000){ e={n:0,t0:now,ban:0}; RL.set(ip,e); }
  return true; }
function rlFail(ip){ const e=RL.get(ip)||{n:0,t0:Date.now(),ban:0}; e.n++;
  if(e.n>12) e.ban=Date.now()+300000; RL.set(ip,e); }
function rlClear(ip){ RL.delete(ip); }
const BASELINE = __BASELINE__;

function jx(o, s) {
  return new Response(JSON.stringify(o), { status: s || 200,
    headers: Object.assign({ "Content-Type": "application/json" }, SECH) });
}
// ---- Cloudflare account proxy (needs CF_API_TOKEN secret; set via `redops cf-publish`) ----
const CF_ACCT = "3d6c06df593089a953cc119dd6faf6be";
async function cfGet(env, path) {
  const r = await fetch("https://api.cloudflare.com/client/v4" + path, {
    headers: { "Authorization": "Bearer " + (env.CF_API_TOKEN || ""), "User-Agent": "redops-intel/1.0" }
  });
  const t = await r.text();
  let j = null; try { j = JSON.parse(t); } catch (e) {}
  return { status: r.status, ok: r.ok && j && j.success, json: j };
}
function cfName(n) {
  n = String(n || "");
  return /^[A-Za-z0-9_-]{1,64}$/.test(n) ? n : null;
}
async function cfInspect(env, name) {
  const out = { name: name, settings: null, bindings: null, routes: [] };
  const s = await cfGet(env, "/accounts/" + CF_ACCT + "/workers/scripts/" + name + "/settings");
  if (s.json && s.json.result) out.settings = s.json.result;
  const b = await cfGet(env, "/accounts/" + CF_ACCT + "/workers/scripts/" + name + "/bindings");
  if (b.json && b.json.result) out.bindings = b.json.result.map(function (x) { return { name: x.name, type: x.type }; });
  const zones = ["af4c9924aae3cf8b1df792cfeb51ba71", "f6f7b901c0cf6921f178747285420703"];
  for (const z of zones) {
    try {
      const r = await cfGet(env, "/zones/" + z + "/workers/routes");
      if (r.json && r.json.result) {
        for (const rt of r.json.result) if (rt.script === name) out.routes.push({ pattern: rt.pattern, zone: z });
      }
    } catch (e) {}
  }
  return out;
}
async function cfSource(env, name) {
  const r = await fetch("https://api.cloudflare.com/client/v4/accounts/" + CF_ACCT + "/workers/scripts/" + name, {
    headers: { "Authorization": "Bearer " + (env.CF_API_TOKEN || ""), "User-Agent": "redops-intel/1.0" }
  });
  const buf = await r.arrayBuffer();
  const bytes = new Uint8Array(buf);
  let text = "";
  try { text = new TextDecoder().decode(bytes.slice(0, 120000)); } catch (e) {}
  const ctype = r.headers.get("content-type") || "";
  if (ctype.indexOf("multipart") >= 0) {
    const m = ctype.match(/boundary=([^;]+)/);
    if (m) {
      const parts = text.split("--" + m[1].replace(/"/g, ""));
      let best = "";
      for (const q of parts) {
        const idx = q.indexOf("\\r\\n\\r\\n");
        if (idx > 0 && q.length > best.length && !/content-type: application/(zip|gzip)/i.test(q)) best = q.slice(idx + 4);
      }
      text = best;
    }
  }
  return { name: name, bytes: bytes.length, truncated: text.length >= 60000, source: text.slice(0, 60000) };
}
function sigOf(h) {
  const names = [["content-security-policy","csp"],["permissions-policy","perm"],
    ["referrer-policy","ref"],["x-content-type-options","nosniff"],
    ["x-frame-options","frame"],["strict-transport-security","hsts"]];
  return names.map(([n, s]) => s + "=" + (h.get(n) ? "1" : "0")).join(";")
    + "|clen=" + (h.get("content-length") || "?");
}
async function pulseCheck() {
  const out = { ts: new Date().toISOString(), targets: {} };
  const urls = [["site","https://runehall.com/"],["robots","https://runehall.com/robots.txt"]];
  for (const [name, url] of urls) {
    try {
      const r = await fetch(url, { redirect: "manual",
        headers: { "User-Agent": "REDOPS-pulse/1.0" } });
      const h = r.headers;
      out.targets[name] = { status: r.status,
        hsts: !!h.get("strict-transport-security"),
        csp: !!h.get("content-security-policy"),
        perm: !!h.get("permissions-policy"),
        referrer: h.get("referrer-policy") || null,
        nosniff: !!h.get("x-content-type-options"),
        frame: h.get("x-frame-options") || null,
        sig: Math.floor(r.status/100) + "xx|" + sigOf(h) };
    } catch (e) { out.targets[name] = { error: String(e).slice(0,120) }; }
  }
  return out;
}
async function dnsCheck() {
  const qs = [["runehall.com","A"],["runehall.com","MX"],["runehall.com","TXT"],
    ["runehall.com","NS"],["_dmarc.runehall.com","TXT"],
    ["zmail._domainkey.runehall.com","TXT"]];
  const out = { ts: new Date().toISOString(), records: {} };
  for (const [n, t] of qs) {
    try {
      const r = await fetch("https://dns.google/resolve?name=" +
        encodeURIComponent(n) + "&type=" + t);
      const j = await r.json();
      out.records[n + " " + t] = (j.Answer || []).map(a => a.data);
    } catch (e) { out.records[n + " " + t] = ["error"]; }
  }
  return out;
}

export default {
  async fetch(req, env) {
    const PASS = env.INTEL_PASS || "";
    const MASTER = env.MASTER_KEY || "";
    const url = new URL(req.url);
    const p = url.pathname;
    if (p === "/login" && req.method === "POST") {
      const ip = req.headers.get("CF-Connecting-IP") || "x";
      if (!rlAllow(ip)) {
        return new Response(LOGIN_HTML.replace("__ERR__", "Too many attempts. Try again in a few minutes."),
          { status: 429, headers: Object.assign({ "Content-Type": "text/html; charset=utf-8", "Content-Security-Policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:;" }, SECH) });
      }
      let ok = false;
      try {
        const fd = await req.formData();
        const pw = (fd.get("pass") || "").toString();
        const viaMaster = MASTER !== "" && seq(pw, MASTER);
        ok = viaMaster || (seq(pw, PASS) && PASS !== "");
        if (ok) {
          rlClear(ip);
          return new Response("ok", { status: 302,
            headers: { "Location": "/", "Set-Cookie": "ro_auth=" + encodeURIComponent(viaMaster ? MASTER : PASS) + "; " + SEC } });
        }
      } catch (e) {}
      rlFail(ip);
      return new Response(LOGIN_HTML.replace("__ERR__", "Wrong passphrase."),
        { status: 401, headers: Object.assign({ "Content-Type": "text/html; charset=utf-8", "Content-Security-Policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:;" }, SECH) });
    }
    if (p === "/logout") {
      return new Response("locked", { status: 302,
        headers: { "Location": "/login", "Set-Cookie": "ro_auth=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Strict" } });
    }
    if (p === "/login") {
      return new Response(LOGIN_HTML.replace("__ERR__", url.searchParams.get("e") ? "Wrong passphrase." : ""),
        { headers: Object.assign({ "Content-Type": "text/html; charset=utf-8", "Content-Security-Policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:;" }, SECH) });
    }
    if (p.startsWith("/api/")) {
      if (!authed(req, PASS, MASTER)) return jx({ ok: false, error: "unauthorized" }, 401);
      if (p === "/api/pulse") return jx(await pulseCheck());
      if (p === "/api/dns") return jx(await dnsCheck());
      if (p === "/api/watch") return jx({ armed: true, cadence: "15m",
        sink: (env.REDOPS_HOOK || "") ? "discord" : "unset",
        baseline: (BASELINE && BASELINE.sig) || null });
      if (p === "/api/feed" && req.method === "POST") {
        const hook = env.REDOPS_HOOK || "";
        if (!hook) return jx({ ok: false, need: "webhook" }, 501);
        let b = {};
        try { b = await req.json(); } catch (e) {}
        const cs = String(b.callsign || "op").slice(0, 24);
        const tx = String(b.text || "").slice(0, 1500);
        if (!tx.trim()) return jx({ ok: false, need: "text" }, 400);
        const dr = await fetch(hook, { method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: "**[" + cs + "]** " + tx }) });
        return jx({ ok: dr.ok, status: dr.status });
      }
      if (p === "/api/cf/status") return jx({ configured: !!(env.CF_API_TOKEN || "") });
      if (p === "/api/cf/workers") {
        if (!env.CF_API_TOKEN) return jx({ ok: false, need: "cf-publish" }, 501);
        const r = await cfGet(env, "/accounts/" + CF_ACCT + "/workers/scripts");
        const list = (r.json && r.json.result) || [];
        return jx({ ok: true, workers: list.map(function (w) {
          return { id: w.id, created_on: w.created_on, modified_on: w.modified_on };
        }) });
      }
      if (p === "/api/cf/inspect") {
        if (!env.CF_API_TOKEN) return jx({ ok: false, need: "cf-publish" }, 501);
        const name = cfName(url.searchParams.get("name"));
        if (!name) return jx({ ok: false, error: "bad name" }, 400);
        return jx({ ok: true, inspect: await cfInspect(env, name) });
      }
      if (p === "/api/cf/source") {
        if (!env.CF_API_TOKEN) return jx({ ok: false, need: "cf-publish" }, 501);
        const name = cfName(url.searchParams.get("name"));
        if (!name) return jx({ ok: false, error: "bad name" }, 400);
        return jx({ ok: true, src: await cfSource(env, name) });
      }
      return jx({ ok: false, error: "not found" }, 404);
    }
    if (!authed(req, PASS, MASTER)) {
      return Response.redirect(url.origin + "/login", 302);
    }
    if (p === "/" || p === "/index.html") {
      return new Response(APP_HTML, { headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Security-Policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:;",
        "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer" } });
    }
    return new Response("not found", { status: 404, headers: SECH });
  },
  async scheduled(event, env, ctx) {
    ctx.waitUntil((async () => {
      try {
        const p = await pulseCheck();
        const s = p.targets.site || {};
        const cur = s.sig || "none";
        const base = (BASELINE && BASELINE.sig) || "";
        if (base && cur !== base) {
          const hook = env.REDOPS_HOOK || "";
          const msg = ":rotating_light: **REDOPS WATCH** — runehall.com changed.\\nBaseline: `" + base + "`\\nNow: `" + cur + "` (HTTP " + s.status + ")";
          if (hook) await fetch(hook, { method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: msg }) });
        }
      } catch (e) {}
    })());
  }
};
"""
worker = worker.replace("__DATA__", "null")  # data goes into APP_HTML instead
_bp = os.path.join(BASE, "baseline.json")
worker = worker.replace("__BASELINE__",
    open(_bp, encoding="utf-8").read() if os.path.exists(_bp) else "null")
# escape </script inside JSON strings so embedded script code can't break out of the page's <script> block;
# JSON.parse restores the real characters, so generated .py downloads stay byte-correct
html = html.replace("__DATA__", data.replace("</script", "<\\/script"))
worker = worker.replace("__APP__", json.dumps(html))
worker = worker.replace("__LOGIN__", json.dumps(LOGIN))

out = os.path.join(BASE, "worker.js")
open(out, "w", encoding="utf-8").write(worker)
print("worker.js written:", os.path.getsize(out) // 1024, "KB")
