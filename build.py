#!/usr/bin/env python3
"""Build redops-intel worker.js from the OSINT case files."""
import json, re, os

OSINT = os.path.expanduser("~/workspace/osint/abuse-osint")

def read(name):
    with open(os.path.join(OSINT, name), encoding="utf-8") as f:
        return f.read()

DOSSIER_FILES = [
    ("Master Report — graded cross-correlation", "runehall-master-report.md"),
    ("Business-Logic Flaw Assessment", "runehall-business-logic.md"),
    ("Infrastructure Assessment — verified, no-mock-data", "runehall-infrastructure-assessment.md"),
    ("Behavioral Evaluation — chat analysis", "runehall-behavioral-evaluation.md"),
    ("Relationship Matrices — 33 individuals", "runehall-relationship-matrices.md"),
    ("Discord Sweep — server harvest", "runehall-discord-sweep.md"),
    ("Discord Handle Roster", "runehall-discord-handles.md"),
    ("Deep-Dive Dorking — 64 handles", "runehall-deepdive-dorking.md"),
    ("Instagram Extraction — 114 handles", "runehall-ig-handles.md"),
    ("Cross-Platform Enumeration", "runehall-crossplatform-enumeration.md"),
    ("Public Username List", "runehall-public-usernames.md"),
]
dossiers = [{"title": t, "file": fn, "text": read(fn)} for t, fn in DOSSIER_FILES]

# ---- parse relationship matrices into structured JSON ----
mat_src = read("runehall-relationship-matrices.md")
individuals = []
for sec in re.split(r"\n## ", mat_src):
    m = re.match(r"([^\n—]+?)(?:\s*—\s*([^\n]+))?\n", sec)
    if not m:
        continue
    name = m.group(1).strip()
    if name.startswith("#") or "CALIBRATION" in name:
        continue
    profile = (m.group(2) or "").strip()
    rows = []
    for line in sec.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("| ---") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 5 and cells[0].lower() not in ("connected to",):
            rows.append({"to": cells[0], "type": cells[1], "strength": cells[2],
                         "evidence": cells[3], "psych": cells[4]})
    # also grab non-table profile paragraph
    body = re.sub(r"\|.*\|", "", sec)
    individuals.append({"name": name, "profile": profile, "rows": rows})

# ---- URL vault from behavioral section C ----
beh = read("runehall-behavioral-evaluation.md")
sec_c = beh.split("## C. URL/domain inventory")[1].split("## D.")[0]
urls = []
seen = set()
for line in sec_c.splitlines():
    s = line.strip().lstrip("- ").strip()
    if not s:
        continue
    m = re.search(r"((?:https?://)?[a-zA-Z0-9.-]+\.[a-z]{2,}(?:/[^\s)>\]]*)?)", s)
    if not m:
        continue
    u = m.group(1).rstrip(".,;")
    key = u.lower()
    if key in seen:
        continue
    seen.add(key)
    if not u.startswith("http"):
        u = "https://" + u
    urls.append({"url": u, "context": s[:220]})

watchlist = [
    {"rank": 1, "target": "CheapGP ↔ BangBangBang ↔ Cmarge93", "why": "Operator liquidity node + $40k/yr gold buyer gambling large + record 1.05B win whale trading billions with the shop. The gold-flow cluster."},
    {"rank": 2, "target": "Orkla", "why": "Community-described site-owner figure ('mayor of runehall'). Never bets. Best owner-candidate handle."},
    {"rank": 3, "target": "lceChicken / humble_fb", "why": "Scam pattern across Sythe ($378 BTC→OSGP report) and in-server reports. Multi-venue."},
    {"rank": 4, "target": "Swerte", "why": "Active Sythe OSRS-account seller inside the player base. Multi-account risk."},
    {"rank": 5, "target": "MissMaeve ↔ Sly (andopanda)", "why": "Repeated same-lobby high-stake battles. Linked-operator or ritual rivalry."},
    {"rank": 6, "target": "Carter", "why": "Won 3 of the biggest prizes in the 50B Christmas Mega Raffle. Extreme concentration."},
    {"rank": 7, "target": "huntingvoids", "why": "3 spots in one 10B raffle ($430) + withdrawal complaints + probed Orkla's identity."},
    {"rank": 8, "target": "willace777", "why": "Polarizing whale: PayPal debt claims, 250M CheapGP deal fallout, pigeon12 summit."},
    {"rank": 9, "target": "pigeon12", "why": "Brokered the 'Murk x Willace summit'. Ownership-adjacent connector."},
    {"rank": 10, "target": "Tokyorandom", "why": "Won 50B Halloween grand prize; unknown to regulars and to CheapGP."},
]

timeline = [
    {"date": "2013", "event": "runehall.com is a Chinese RuneScape fan wiki, “符文殿 (Runehall)” (Wayback)."},
    {"date": "2016–2017", "event": "Domain parked / “under development” (Wayback)."},
    {"date": "2021-03", "event": "CheapGP opens its Sythe gold shop (1,300 vouches to date)."},
    {"date": "2022-02-06", "event": "runehall.com re-registered — casino era begins (WHOIS)."},
    {"date": "2022-10-05", "event": "Earliest casino snapshot: “RuneHall — The #1 Runescape gambling Casino” (Wayback)."},
    {"date": "2024-03-21", "event": "runefair.com first archived — fairness verifier launches ~2 yrs after the casino."},
    {"date": "2024-12", "event": "Sythe scam report: lceChicken $378 BTC→OSGP swap (Discord humble_fb)."},
    {"date": "2026-09 → 10", "event": "This investigation: 64 handles enumerated, dork sweep (9 bridges), 114 IG handles, Discord sweep (18/24 matched), behavioral evaluation, relationship matrices."},
]

DORKS = [
    ('Exact handle', '"{h}"'),
    ('Site mention', 'site:runehall.com "{h}"'),
    ('Sythe', 'site:sythe.org "{h}"'),
    ('Discord link', '"{h}" discord'),
    ('Telegram', '"{h}" telegram'),
    ('GitHub', '"{h}" github'),
    ('Pastebins', '"{h}" site:pastebin.com OR site:pastes.io OR site:psbdmp.ws'),
    ('Breach dumps', '"{h}" site:breachforums.io OR site:leakforum.io'),
    ('Reddit', 'site:reddit.com "{h}" runehall'),
    ('Twitter/X', 'site:x.com "{h}" OR site:twitter.com "{h}"'),
    ('YouTube', 'site:youtube.com "{h}"'),
    ('Twitch', 'site:twitch.tv "{h}"'),
]

# ops scripts: load + compile-verify every script before bundling
OPS_DIR = os.path.join(os.path.dirname(__file__), "ops-scripts")
ops_scripts = []
_ops_index = json.load(open(os.path.join(OPS_DIR, "index.json"), encoding="utf-8"))
for _m in _ops_index:
    _code = open(os.path.join(OPS_DIR, _m["id"] + ".py"), encoding="utf-8").read()
    compile(_code, _m["id"] + ".py", "exec")  # syntax-clean guarantee; fails the build otherwise
    ops_scripts.append({"id": _m["id"], "tags": _m["tags"], "name": _m["name"],
                        "desc": _m["desc"], "code": _code})
print("ops_scripts bundled:", len(ops_scripts))

data = {"dossiers": dossiers, "individuals": individuals, "urls": urls,
        "watchlist": watchlist, "timeline": timeline, "dorks": DORKS,
        "ops_scripts": ops_scripts,
        "stats": {"handles": 64, "ig_handles": 114, "discord_members": 3381,
                  "bridges": 9, "leads": 32, "matched": "18/24",
                  "urls": len(urls), "individuals": len(individuals)}}

with open(os.path.join(os.path.dirname(__file__), "data.json"), "w") as f:
    json.dump(data, f)
print("data.json written:", len(json.dumps(data)) // 1024, "KB;",
      len(individuals), "individuals,", len(urls), "urls")
