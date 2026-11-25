#!/usr/bin/env python3
"""Builds the themed section cards (About, Featured, Tech Stack, Achievements, Connect). Edit CONTENT below, then re-run."""
import html, os, textwrap

# ======================= EDIT YOUR CONTENT HERE =======================
ABOUT = [
    "Third-year B.E. Computer Engineering student at JSCOE, Pune",
    "Exploring Artificial Intelligence, Machine Learning & Data Science",
    "Interested in Python, AI/ML, Web Development & building real-world solutions",
    "Artist at heart – bringing creativity to code, design, and user experience",
    "Love collaborating, participating in hackathons, and learning new technologies",
]
FEATURED = {
    "title": "EcoQuest – Gamified Personal Carbon Footprint",
    "desc": "A sustainability-focused web application that encourages eco-friendly habits through gamification, personalized recommendations, XP, achievements, and leaderboards.",
    "bullets": ["Makes everyday environmental impact easier to understand",
                "Encourages sustainable habits through challenges and rewards"],
    "stack": ["React", "Vite", "Node.js", "Express", "SQLite"],
}
STACK = [
    ("PROGRAMMING LANGUAGES", [("Python","#3776ab"),("Java","#e76f00"),("C++","#00599c"),("C","#6e7681"),("JavaScript","#f0db4f"),("HTML","#e34c26"),("CSS","#a97bc4")]),
    ("WEB DEVELOPMENT", [("React","#61dafb"),("Next.js","#f2f2fa"),("Node.js","#6cc24a"),("Express","#8a8aa6"),("Bootstrap","#7952b3"),("Vite","#a855f7")]),
    ("AI, ML & DATA SCIENCE", [("scikit-learn","#f7931e"),("PyTorch","#ee4c2c"),("TensorFlow","#ff6f00"),("NumPy","#4dabcf"),("Pandas","#8a6ff0"),("Matplotlib","#3de0e0"),("XGBoost","#ec6b23"),("Streamlit","#ff4b4b")]),
    ("IOT & HARDWARE", [("Arduino","#00979d"),("ESP32","#e7352c")]),
    ("TOOLS & PLATFORMS", [("Git","#f05033"),("GitHub","#f2f2fa"),("VS Code","#3178c6"),("Anaconda","#44a833"),("Vercel","#f2f2fa"),("Figma","#ec4899"),("Jupyter","#f37626"),("Google Colab","#f9ab00"),("Kaggle","#20beff"),("Canva","#00c4cc")]),
]
ACHIEVEMENTS = [
    ("Best Outgoing Student 2025", "K. K. Wagh Polytechnic, Nashik"),
    ("NexBuildOn Hack 2026", "Top 20 among 1,000+ participants"),
    ("Grand Finale Selection", "Top 10 Live Demo"),
    ("Best Potential for Impact", "NexBuildOn Hack 2026 · EcoQuest"),
    ("Research Publication", "Smart Security System for Bike with Biometric Access and Mobile Application"),
    ("R3 Systems Internship", "NYC Taxi Fare Prediction using Python and XGBoost"),
]
CONNECT = [("linkedin", "LINKEDIN", "anusha-randive", "#0a66c2"), ("github", "GITHUB", "@ann-artist", "#f2f2fa")]
# =====================================================================

esc = lambda s: html.escape(str(s), quote=False)
ACC = ["#7c3aed", "#3de0e0", "#4dffa0", "#ec4899"]
W = 800
DEFS = ('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset=".5" stop-color="#3de0e0"/><stop offset="1" stop-color="#ec4899"/></linearGradient>'
        '<linearGradient id="s" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        "<style>text{font-family:'Segoe UI',system-ui,sans-serif;fill:#f2f2fa}.m{font-family:ui-monospace,Menlo,Consolas,monospace}.lbl{font-size:9px;letter-spacing:2px;fill:#6fa8ff}.mut{fill:#8a8aa6}.txt{fill:#c9c9dc}</style></defs>")

def svg(w, h, body, label):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{DEFS}{body}</svg>'
def panel(x, y, w, h, shine=False):
    s = f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="{h-2}" rx="14" fill="#0a0a14" stroke="url(#g)" stroke-width="2"/>'
    if shine:
        cid = f"c{x}_{y}"
        s += (f'<clipPath id="{cid}"><rect x="{x+1}" y="{y+1}" width="{w-2}" height="{h-2}" rx="14"/></clipPath><g clip-path="url(#{cid})"><rect x="-200" y="{y}" width="120" height="{h}" fill="url(#s)" transform="skewX(-20)">'
              f'<animate attributeName="x" values="-200;1000;1000" keyTimes="0;.45;1" dur="9s" repeatCount="indefinite"/></rect></g>')
    return s
def write(name, content):
    os.makedirs("assets", exist_ok=True)
    open(f"assets/{name}", "w", encoding="utf-8").write(content)

def chips(items, x0, y, maxw, color_of=None):
    s, x = "", x0
    for it in items:
        label, color = (it if isinstance(it, tuple) else (it, "#3de0e0"))
        w = int(34 + 6.7 * len(label))
        if x + w > x0 + maxw: x, y = x0, y + 34
        s += (f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="13" fill="#11111d" stroke="#1c1c2e"/><circle cx="{x+14}" cy="{y+13}" r="4" fill="{color}"/>'
              f'<text x="{x+25}" y="{y+17}" font-size="11" class="m txt">{esc(label)}</text>')
        x += w + 8
    return s, y + 26

# ---------- About ----------
y, body = 64, ""
for i, item in enumerate(ABOUT):
    for j, line in enumerate(textwrap.wrap(item, 96)):
        if j == 0: body += f'<circle cx="34" cy="{y-4}" r="3.5" fill="{ACC[i % 4]}"/>'
        body += f'<text x="48" y="{y}" font-size="13" class="txt">{esc(line)}</text>'; y += 19
    y += 9
h = y + 6
write("about.svg", svg(W, h, panel(0, 0, W, h, True) + '<text x="28" y="34" class="m lbl">ABOUT ME</text>' + body, "About me"))

# ---------- Featured ----------
b = '<text x="28" y="34" class="m lbl">FEATURED PROJECT</text>'
b += f'<text x="28" y="66" font-size="19" font-weight="800" style="fill:#3de0e0">{esc(FEATURED["title"])}</text>'
y = 92
for line in textwrap.wrap(FEATURED["desc"], 100):
    b += f'<text x="28" y="{y}" font-size="13" class="txt">{esc(line)}</text>'; y += 19
y += 8
for i, t in enumerate(FEATURED["bullets"]):
    b += f'<circle cx="34" cy="{y-4}" r="3.5" fill="{ACC[(i+1) % 4]}"/><text x="48" y="{y}" font-size="13" class="txt">{esc(t)}</text>'; y += 24
y += 4
b += f'<text x="28" y="{y+4}" class="m lbl">STACK</text>'
cs, ye = chips(FEATURED["stack"], 28, y + 14, 744)
b += cs; h = ye + 22
write("featured.svg", svg(W, h, panel(0, 0, W, h, True) + b, "Featured project"))

# ---------- Tech stack ----------
b, y = "", 0
for ci, (cat, items) in enumerate(STACK):
    cs, ye = chips(items, 28, y + 44, 744)
    ph = ye - y + 20
    b += panel(0, y, W, ph, ci == 0) + f'<text x="28" y="{y+28}" class="m lbl">{esc(cat)}</text>' + cs
    y += ph + 12
write("tech-stack.svg", svg(W, y - 12, b, "Tech stack"))

# ---------- Achievements ----------
b = '<text x="4" y="14" class="m lbl">ACHIEVEMENTS &amp; EXPERIENCE</text><rect x="4" y="24" width="120" height="2" rx="1" fill="url(#g)"/>'
y0 = 42; rowh = 0
for i, (t, d) in enumerate(ACHIEVEMENTS):
    x, yy = (i % 2) * 406, y0 + (i // 2) * 114
    b += panel(x, yy, 394, 102) + f'<text x="{x+18}" y="{yy+26}" class="m lbl">{i+1:02d}</text><text x="{x+18}" y="{yy+50}" font-size="14" font-weight="700">{esc(t)}</text>'
    for j, line in enumerate(textwrap.wrap(d, 52)[:2]):
        b += f'<text x="{x+18}" y="{yy+72+j*15}" font-size="11.5" class="mut">{esc(line)}</text>'
    b += f'<circle cx="{x+368}" cy="{yy+26}" r="4" fill="{ACC[i % 4]}"/>'
H = y0 + 114 * ((len(ACHIEVEMENTS) + 1) // 2) - 12
write("achievements.svg", svg(W, H, b, "Achievements and experience"))

# ---------- Connect buttons ----------
for key, name, handle, color in CONNECT:
    b = (panel(0, 0, 260, 56, True) + f'<circle cx="28" cy="28" r="6" fill="{color}"/><text x="46" y="24" class="m lbl">{name}</text>'
         f'<text x="46" y="42" font-size="13" font-weight="600">{esc(handle)}</text><text x="236" y="34" font-size="15" text-anchor="end" style="fill:#3de0e0">↗</text>')
    write(f"connect-{key}.svg", svg(260, 56, b, name))
print("sections generated")
