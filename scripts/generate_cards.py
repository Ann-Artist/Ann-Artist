#!/usr/bin/env python3
"""Builds assets/collector-profile.svg from live GitHub data (profile photo, stats, pinned repos, languages, contributions)."""
import base64, html, json, os, textwrap, urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "Ann-Artist")
TOKEN = os.environ.get("GITHUB_TOKEN")
COLORS = {"TypeScript":"#3178c6","JavaScript":"#f0db4f","HTML":"#e34c26","PHP":"#4f5b93","CSS":"#a97bc4","Python":"#3776ab",
          "Java":"#e76f00","C++":"#00599c","C":"#6e7681","Jupyter Notebook":"#da5b0b","Shell":"#89e051"}
col = lambda n: COLORS.get(n, "#8a8aa6")
esc = lambda s: html.escape(str(s or ""), quote=False)

def req(url, data=None):
    r = urllib.request.Request(url, data=data, headers={"User-Agent": "card-gen", "Accept": "application/vnd.github+json"})
    if TOKEN: r.add_header("Authorization", f"Bearer {TOKEN}")
    return urllib.request.urlopen(r, timeout=30)
def api(path):
    with req("https://api.github.com" + path) as r: return json.load(r)
def graphql(q):
    with req("https://api.github.com/graphql", json.dumps({"query": q}).encode()) as r: return json.load(r)["data"]["user"]

# ---------------- fetch ----------------
user = api(f"/users/{USER}")
repos, page = [], 1
while True:
    b = api(f"/users/{USER}/repos?per_page=100&type=owner&sort=pushed&page={page}")
    repos += b
    if len(b) < 100: break
    page += 1
own = [r for r in repos if not r["fork"]]
stars = sum(r["stargazers_count"] for r in own)

langs = {}
for r in own:
    try:
        for k, v in api(f"/repos/{USER}/{r['name']}/languages").items(): langs[k] = langs.get(k, 0) + v
    except Exception: pass
tot = sum(langs.values()) or 1
pcts = [(n, max(1, round(v * 100 / tot))) for n, v in sorted(langs.items(), key=lambda kv: -kv[1])[:5]]

avatar = ""
try:
    url = user["avatar_url"] + ("&" if "?" in user["avatar_url"] else "?") + "s=240"
    with req(url) as r:
        avatar = f"data:{r.headers.get_content_type()};base64," + base64.b64encode(r.read()).decode()
except Exception as e: print("avatar failed:", e)

pinned, weeks = [], []
try:
    u = graphql('{user(login:"%s"){pinnedItems(first:4,types:REPOSITORY){nodes{... on Repository{name description stargazerCount forkCount primaryLanguage{name}}}}'
                'contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}' % USER)
    pinned = [{"name": n["name"], "description": n["description"], "stars": n["stargazerCount"], "forks": n["forkCount"],
               "language": (n["primaryLanguage"] or {}).get("name")} for n in u["pinnedItems"]["nodes"]]
    cal = u["contributionsCollection"]["contributionCalendar"]
    total_contrib = cal["totalContributions"]
    weeks = [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]]
except Exception as e: print("graphql failed:", e); total_contrib = None
if not pinned:
    pinned = [{"name": r["name"], "description": r["description"], "stars": r["stargazers_count"], "forks": r["forks_count"],
               "language": r["language"]} for r in own if r["name"].lower() != USER.lower()][:4]

# streaks
days = [c for w in weeks for c in w]
best = run = 0
for c in days:
    run = run + 1 if c else 0; best = max(best, run)
cur, seq = 0, days[:]
if seq and seq[-1] == 0: seq = seq[:-1]
for c in reversed(seq):
    if c: cur += 1
    else: break

print(f"{USER}: repos={user['public_repos']} followers={user['followers']} stars={stars} contrib={total_contrib} streak={cur}/{best} pinned={[p['name'] for p in pinned]} langs={pcts}")

# ---------------- render ----------------
W = 800
name = (user.get("name") or USER).split()[0]
tag = " · ".join(n for n, _ in pcts[:2]) + " developer" if pcts else "Developer"
bio = user.get("bio") or "Developer & artist"
since = user["created_at"][:4]
year = datetime.now(timezone.utc).year
out = []
def panel(x, y, w, h): return f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="{h-2}" rx="14" fill="#0a0a14" stroke="url(#g)" stroke-width="2"/>'
def stat(x, y, val, label, c):
    return (f'<rect x="{x}" y="{y}" width="240" height="56" rx="10" fill="#11111d" stroke="#1c1c2e"/><text x="{x+16}" y="{y+32}" font-size="28" font-weight="800" style="fill:{c}">{esc(val)}</text>'
            f'<text x="{x+16}" y="{y+48}" font-size="8" letter-spacing="2" class="m mut">{label}</text>')

# hero
rows = "".join(f'<rect x="14" y="{170+i*20}" width="12" height="12" rx="2" fill="{col(n)}"/><text x="33" y="{180+i*20}" font-size="10" font-weight="600">{esc(n)}</text>'
               f'<text x="176" y="{180+i*20}" font-size="9" text-anchor="end" class="m mut">{p} PWR</text>' for i, (n, p) in enumerate(pcts[:3]))
art = (f'<image xlink:href="{avatar}" x="14" y="36" width="162" height="104" preserveAspectRatio="xMidYMid slice" clip-path="url(#cc)" opacity=".85"/>' if avatar
       else f'<text x="95" y="108" font-size="56" font-weight="800" text-anchor="middle" style="fill:#3de0e0;opacity:.55">{esc(name[0])}</text>')
out.append(f'''<rect width="{W}" height="290" rx="18" fill="#05050a"/>
<g transform="translate(40 24) rotate(-2 90 120)"><rect width="190" height="244" rx="14" fill="url(#holo)"/><rect x="3" y="3" width="184" height="238" rx="12" fill="#080810"/>
<text x="14" y="26" font-size="15" font-weight="700">{esc(name)}</text><text x="176" y="25" font-size="9" text-anchor="end" class="m" style="fill:#f5c542">★ {stars}</text>
<rect x="14" y="36" width="162" height="104" rx="8" fill="url(#art)"/>{art}
<text x="14" y="158" font-size="7" letter-spacing="1" class="m" style="fill:#6fa8ff">COMMON · {user['public_repos']} REPOS · SINCE {since}</text>{rows}</g>
<text x="272" y="62" class="m lbl">COLLECTOR'S EDITION · {year}</text><text x="272" y="106" font-size="42" font-weight="800">@{esc(USER.lower())}</text>
<text x="272" y="130" font-size="13" class="mut">{esc(tag)}</text>
{stat(272,150,stars,'STARS','#4dffa0')}{stat(524,150,user['followers'],'FOLLOWERS','#4dffa0')}
{stat(272,216,total_contrib if total_contrib is not None else '–','CONTRIBUTIONS','#3de0e0')}{stat(524,216,cur,'DAY STREAK','#3de0e0')}''')

# bio panel
y = 306
lines = textwrap.wrap(bio, 58)[:2]
bio_txt = "".join(f'<text x="28" y="{y+80+i*18}" font-size="12" style="fill:#c9c9dc">{esc(l)}</text>' for i, l in enumerate(lines))
meta = " · ".join(x for x in [user.get("location"), f"{user['followers']} followers", f"{user['public_repos']} repositories", f"★ {stars} stars"] if x)
out.append(panel(0, y, W, 130) + f'<text x="28" y="{y+30}" class="m lbl">COLLECTOR CARD</text><text x="28" y="{y+62}" font-size="24" font-weight="800">{esc(name)}</text>{bio_txt}'
           f'<text x="28" y="{y+118}" font-size="9" class="m" style="fill:#6fa8ff">{esc(meta)}</text>'
           + (f'<image xlink:href="{avatar}" x="676" y="{y+23}" width="84" height="84" preserveAspectRatio="xMidYMid slice" clip-path="url(#ac)"/>' if avatar else '')
           + f'<circle cx="718" cy="{y+65}" r="43" fill="none" stroke="#3de0e0" stroke-width="3"/>')
out.append(f'<clipPath id="ac"><circle cx="718" cy="{y+65}" r="42"/></clipPath>')

# pinned repo cards
y = 452
for i, p in enumerate(pinned[:4]):
    x, yy = (i % 2) * 406, y + (i // 2) * 130
    d = textwrap.wrap(p["description"] or "No description", 50)[:2]
    if len(textwrap.wrap(p["description"] or "", 50)) > 2: d[1] = d[1][:46] + "..."
    dt = "".join(f'<text x="{x+18}" y="{yy+68+j*14}" font-size="10" class="mut">{esc(l)}</text>' for j, l in enumerate(d))
    lang = (f'<rect x="{x+130}" y="{yy+97}" width="12" height="12" rx="3" fill="{col(p["language"])}"/><text x="{x+148}" y="{yy+107}" font-size="10" style="fill:#c9c9dc">{esc(p["language"])}</text>' if p["language"] else "")
    out.append(panel(x, yy, 394, 118) + f'<text x="{x+18}" y="{yy+26}" class="m lbl">CARD {i+1:02d}</text><text x="{x+18}" y="{yy+48}" font-size="14" font-weight="700" class="m">{esc(p["name"][:30])}</text>{dt}'
               f'<text x="{x+18}" y="{yy+107}" font-size="10" class="m mut">★ {p["stars"]}   forks {p["forks"]}</text>{lang}')
y += 130 * ((len(pinned[:4]) + 1) // 2) + 6

# powers
if pcts:
    h = 62 + len(pcts) * 32 + 14; mx = max(p for _, p in pcts)
    s = panel(0, y, W, h) + f'<text x="28" y="{y+34}" class="m lbl">POWERS</text>'
    for i, (n, p) in enumerate(pcts):
        yy = y + 58 + i * 32
        s += (f'<rect x="28" y="{yy}" width="14" height="14" rx="3" fill="{col(n)}"/><text x="52" y="{yy+12}" font-size="13" font-weight="600">{esc(n)}</text>'
              f'<rect x="170" y="{yy+2}" width="540" height="11" rx="5.5" fill="#1c1c30"/><rect x="170" y="{yy+2}" width="0" height="11" rx="5.5" fill="{col(n)}"><animate attributeName="width" from="0" to="{int(540*p/mx*.95)}" dur="1.4s" begin=".2s" fill="freeze"/></rect>'
              f'<text x="772" y="{yy+12}" font-size="11" text-anchor="end" class="m mut">{p}%</text>')
    out.append(s); y += h + 16

# season
if weeks:
    wk = weeks[-26:]; mxc = max((c for w in wk for c in w), default=1) or 1
    lvl = lambda c: 0 if c == 0 else min(4, 1 + int(3 * (c - 1) / max(mxc - 1, 1) + .5))
    cl = ["#14142a", "#2a1f6b", "#5b34c9", "#3de0e0", "#4dffa0"]
    s = panel(0, y, W, 160) + f'<text x="28" y="{y+34}" class="m lbl">SEASON · 26 WEEKS</text>'
    for wi, w in enumerate(wk):
        for di, c in enumerate(w):
            s += f'<rect x="{28+wi*12}" y="{y+52+di*14}" width="10" height="10" rx="2" fill="{cl[lvl(c)]}"/>'
    for i, (lab, val) in enumerate([("CURRENT STREAK", f"{cur} days"), ("BEST STREAK", f"{best} days"), ("CONTRIBUTIONS THIS YEAR", total_contrib)]):
        s += f'<text x="440" y="{y+60+i*38}" font-size="8" letter-spacing="2" class="m mut">{lab}</text><text x="440" y="{y+80+i*38}" font-size="20" font-weight="800">{val}</text>'
    out.append(s); y += 176

H = y
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(USER)} collector profile">
<defs>
<linearGradient id="holo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c3aed"><animate attributeName="stop-color" values="#7c3aed;#3de0e0;#ec4899;#7c3aed" dur="6s" repeatCount="indefinite"/></stop><stop offset=".5" stop-color="#3de0e0"><animate attributeName="stop-color" values="#3de0e0;#4dffa0;#7c3aed;#3de0e0" dur="6s" repeatCount="indefinite"/></stop><stop offset="1" stop-color="#ec4899"><animate attributeName="stop-color" values="#ec4899;#7c3aed;#3de0e0;#ec4899" dur="6s" repeatCount="indefinite"/></stop></linearGradient>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset=".5" stop-color="#3de0e0"/><stop offset="1" stop-color="#ec4899"/></linearGradient>
<linearGradient id="art" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16301f"/><stop offset="1" stop-color="#0b1a2a"/></linearGradient>
<clipPath id="cc"><rect x="14" y="36" width="162" height="104" rx="8"/></clipPath>
<style>text{{font-family:'Segoe UI',system-ui,sans-serif;fill:#f2f2fa}}.m{{font-family:ui-monospace,Menlo,Consolas,monospace}}.lbl{{font-size:9px;letter-spacing:2px;fill:#6fa8ff}}.mut{{fill:#8a8aa6}}</style>
</defs>
{chr(10).join(out)}
</svg>'''
os.makedirs("assets", exist_ok=True)
open("assets/collector-profile.svg", "w", encoding="utf-8").write(svg)
