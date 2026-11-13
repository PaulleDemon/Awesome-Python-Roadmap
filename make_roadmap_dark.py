"""Generate the dark Python Roadmap graphics.

Outputs (in ./assets):
  roadmap-dark.svg / .png           tall version for the GitHub README
  roadmap-dark-16x9.svg / .png      1920x1080 overview for video
  instagram/slide-01.png ...        1080x1350 Instagram carousel

Edit STAGES below and re-run:  python make_roadmap_dark.py
PNG export needs `rsvg-convert` (librsvg) on your PATH.
"""
import math
import os
import shutil
import subprocess
from html import escape

FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'DejaVu Sans Mono', Consolas, monospace"

BG = "#0b1220"
CARD = "#131c2e"
CARD_EDGE = "#243049"
TEXT = "#e8edf6"
MUTED = "#93a1b8"

CAT = {"core": "#4b8bbe", "track": "#ffd43b", "ai": "#a78bfa"}

STAGES = [
    dict(n=0, title="Getting Started", eps="1–3", cat="core",
         topics=["Why Python?", "Install Python & VS Code", "Terminal basics",
                 "REPL vs scripts", "print() & comments"],
         project="Your first Python script",
         key=["Setup", "REPL", "First script"]),
    dict(n=1, title="Python Basics", eps="4–10", cat="core",
         topics=["Variables & data types", "Operators", "Strings & f-strings",
                 "Input & type conversion", "if / elif / else", "match-case",
                 "for & while loops", "break & continue"],
         project="Guessing Game + Calculator",
         key=["Variables", "Conditionals", "Loops"]),
    dict(n=2, title="Data Structures", eps="11–17", cat="core",
         topics=["Lists", "Tuples & unpacking", "Sets", "Dictionaries",
                 "Comprehensions", "Intro to Big-O"],
         project="Contact Book / To-Do CLI",
         key=["Lists & tuples", "Sets & dicts", "Comprehensions"]),
    dict(n=3, title="Functions & Modules", eps="18–25", cat="core",
         topics=["Functions & return", "*args & **kwargs", "Scope & nonlocal",
                 "lambda, map, filter", "Recursion", "Standard library",
                 "pip & venv", "requirements.txt"],
         project="Password Generator + Quiz",
         key=["Functions", "Modules", "pip & venv"]),
    dict(n=4, title="Intermediate & OOP", eps="26–36", cat="core",
         topics=["Exceptions", "Files: CSV, JSON", "Dates & times",
                 "Regular expressions", "Classes & objects",
                 "Inheritance & super()", "Dunder & dataclasses",
                 "Generators", "Decorators", "Context managers", "Type hints"],
         project="Library Management System",
         key=["Exceptions & files", "OOP", "Decorators"]),
    dict(n=5, title="Tools & Best Practices", eps="37–42", cat="core",
         topics=["Git & GitHub", "Debugging & logging", "PEP 8 & Ruff",
                 "Testing with pytest", "pyproject & uv", "threading & asyncio"],
         project="CHECKPOINT: core done, pick a track",
         key=["Git", "pytest", "Packaging"]),
    dict(n=6, title="GUI Development", eps="43–49", cat="track",
         topics=["Tkinter widgets", "Layouts & events", "Dialogs & menus",
                 "CustomTkinter", "PyUIBuilder (drag & drop)", "PySide6 (Qt)", "PyInstaller"],
         project="Expense Tracker desktop app",
         key=["Tkinter", "PyUIBuilder", "PySide6"]),
    dict(n=7, title="NumPy & Data", eps="50–57", cat="track",
         topics=["Jupyter Notebooks", "NumPy arrays", "Slicing & masks",
                 "Broadcasting", "Pandas DataFrames", "Cleaning & groupby",
                 "Matplotlib", "Seaborn"],
         project="EDA on a real dataset",
         key=["NumPy", "Pandas", "Matplotlib"]),
    dict(n=8, title="Web Development", eps="58–67", cat="track",
         topics=["HTTP, HTML & JSON", "requests & APIs", "Web scraping",
                 "SQL & SQLite", "Flask & Jinja2", "SQLAlchemy & auth",
                 "FastAPI & Pydantic", "Django & admin", "Docker & deployment"],
         project="Blog or URL Shortener API",
         key=["Flask", "FastAPI", "Django"]),
    dict(n=9, title="ML & AI Basics", eps="68–77", cat="ai",
         topics=["ML concepts", "Maths with NumPy",
                 "Linear regression", "Classification", "Metrics & validation",
                 "Pipelines", "K-Means clustering", "Neural nets (PyTorch)",
                 "LLM APIs & embeddings"],
         project="CAPSTONE: ML-powered web app",
         key=["scikit-learn", "PyTorch", "LLM APIs"]),
]

NEXT = ["Data Science", "Deep Learning", "Automation & DevOps",
        "Game Dev", "Cybersecurity", "DSA & Interviews"]


def t(x, y, s, size, fill=TEXT, weight=400, anchor="start", family=FONT,
      spacing=0, opacity=1):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{spacing}" '
            f'opacity="{opacity}">{escape(s)}</text>')


def logo(cx, cy, s=1.0):
    w, r, g = 34 * s, 9 * s, 6 * s
    return (f'<rect x="{cx - w - g/2:.1f}" y="{cy - w - g/2:.1f}" width="{w:.1f}" '
            f'height="{w:.1f}" rx="{r:.1f}" fill="#4b8bbe"/>'
            f'<rect x="{cx + g/2:.1f}" y="{cy + g/2:.1f}" width="{w:.1f}" '
            f'height="{w:.1f}" rx="{r:.1f}" fill="#ffd43b"/>'
            f'<rect x="{cx - w/2:.1f}" y="{cy - w/2:.1f}" width="{w:.1f}" '
            f'height="{w:.1f}" rx="{r:.1f}" fill="none" stroke="{TEXT}" '
            f'stroke-width="{3*s:.1f}"/>')


def backdrop(W, H, glow_h=700):
    return ('<defs>'
            '<radialGradient id="glow" cx="50%" cy="0%" r="70%">'
            '<stop offset="0" stop-color="#1d3a63" stop-opacity="0.9"/>'
            f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>'
            '<pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">'
            '<circle cx="2" cy="2" r="1.2" fill="#ffffff" opacity="0.05"/></pattern>'
            '</defs>'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>'
            f'<rect width="{W}" height="{H}" fill="url(#dots)"/>'
            f'<rect width="{W}" height="{glow_h}" fill="url(#glow)"/>')


def project_parts(p):
    if p.startswith("CHECKPOINT: "):
        return "CHECKPOINT", p[12:]
    if p.startswith("CAPSTONE: "):
        return "CAPSTONE", p[10:]
    return "PROJECT", p


# --------------------------------------------------------------------------
# Tall README version
# --------------------------------------------------------------------------
def tall():
    W = 1400
    SPINE = W / 2
    CW, GAP_X, OFFSET, GAP_Y, ROW = 580, 70, 150, 36, 34
    out = []

    top = 380
    ys, hs = [], []
    for i, st in enumerate(STAGES):
        rows = math.ceil(len(st["topics"]) / 2)
        h = 132 + rows * ROW + 74
        y = top if i == 0 else ys[-1] + OFFSET
        if i >= 2:
            y = max(y, ys[i - 2] + hs[i - 2] + GAP_Y)
        ys.append(y)
        hs.append(h)
    body_end = max(y + h for y, h in zip(ys, hs))
    H = int(body_end + 270)

    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}">')
    out.append(backdrop(W, H))
    out.append('<defs><linearGradient id="spine" gradientUnits="userSpaceOnUse" '
               f'x1="0" y1="{ys[0]}" x2="0" y2="{body_end + 60}">'
               '<stop offset="0" stop-color="#4b8bbe"/>'
               '<stop offset="0.55" stop-color="#4b8bbe"/>'
               '<stop offset="0.62" stop-color="#ffd43b"/>'
               '<stop offset="0.86" stop-color="#ffd43b"/>'
               '<stop offset="0.93" stop-color="#a78bfa"/>'
               '<stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>')

    out.append(logo(SPINE, 92, 1.25))
    out.append(t(SPINE, 205, "PYTHON ROADMAP", 76, weight=800, anchor="middle",
                 spacing=3))
    out.append(t(SPINE, 252, "The complete learning roadmap for students & developers",
                 26, fill=MUTED, anchor="middle"))
    leg = [("core", "Core: everyone"), ("track", "Tracks: GUI, Data, Web"),
           ("ai", "AI: needs Data + Web")]
    for k, (c, s) in enumerate(leg):
        x = SPINE - 470 + k * 330
        out.append(f'<circle cx="{x}" cy="324" r="9" fill="{CAT[c]}"/>')
        out.append(t(x + 20, 331, s, 20, fill=MUTED))

    out.append(f'<line x1="{SPINE}" y1="{ys[0]}" x2="{SPINE}" y2="{body_end + 60}" '
               f'stroke="url(#spine)" stroke-width="8" stroke-linecap="round" opacity="0.9"/>')

    for i, st in enumerate(STAGES):
        y, h = ys[i], hs[i]
        col = CAT[st["cat"]]
        left = i % 2 == 0
        cx = SPINE - GAP_X - CW if left else SPINE + GAP_X
        ny = y + 46
        edge = cx + CW if left else cx
        out.append(f'<line x1="{SPINE}" y1="{ny}" x2="{edge}" y2="{ny}" '
                   f'stroke="{col}" stroke-width="3" stroke-dasharray="6 6" opacity="0.8"/>')
        out.append(f'<rect x="{cx}" y="{y}" width="{CW}" height="{h}" rx="20" '
                   f'fill="{CARD}" stroke="{CARD_EDGE}" stroke-width="1.5"/>')
        out.append(f'<rect x="{cx}" y="{y}" width="{CW}" height="8" rx="4" fill="{col}"/>')
        out.append(t(cx + 32, y + 50, f'STAGE {st["n"]}', 17, fill=col, weight=700,
                     spacing=2.5))
        out.append(t(cx + 32, y + 94, st["title"], 34, weight=800))
        colw = (CW - 64) / 2
        for k, topic in enumerate(st["topics"]):
            r, c = divmod(k, 2)
            tx, yy = cx + 32 + c * colw, y + 140 + r * ROW
            out.append(f'<circle cx="{tx + 5}" cy="{yy - 7}" r="4.5" fill="{col}"/>')
            out.append(t(tx + 20, yy, topic.replace(" (drag & drop)", ""), 20,
                         opacity=0.92))
        py = y + h - 58
        tag, label = project_parts(st["project"])
        out.append(f'<rect x="{cx + 20}" y="{py}" width="{CW - 40}" height="40" rx="10" '
                   f'fill="{col}" fill-opacity="0.13" stroke="{col}" stroke-opacity="0.5"/>')
        out.append(t(cx + 36, py + 27, tag, 15, fill=col, weight=800, spacing=1.5))
        tagw = {"PROJECT": 92, "CHECKPOINT": 122, "CAPSTONE": 106}[tag]
        out.append(t(cx + 36 + tagw, py + 27, label, 19, weight=600))
        out.append(f'<circle cx="{SPINE}" cy="{ny}" r="34" fill="{BG}" stroke="{col}" '
                   f'stroke-width="6"/>')
        out.append(t(SPINE, ny + 12, str(st["n"]), 32, weight=800, anchor="middle",
                     fill=col))

    fy = body_end + 60
    out.append(f'<circle cx="{SPINE}" cy="{fy}" r="22" fill="#a78bfa"/>')
    out.append(t(SPINE, fy + 75, "WHAT'S NEXT?", 30, weight=800, anchor="middle",
                 spacing=2))
    chip_w = [len(s) * 11.5 + 44 for s in NEXT]
    x = SPINE - (sum(chip_w) + 14 * (len(NEXT) - 1)) / 2
    for s, w in zip(NEXT, chip_w):
        out.append(f'<rect x="{x}" y="{fy + 105}" width="{w}" height="44" rx="22" '
                   f'fill="none" stroke="{CARD_EDGE}" stroke-width="2"/>')
        out.append(t(x + w / 2, fy + 134, s, 19, fill=MUTED, weight=600, anchor="middle"))
        x += w + 14
    out.append('</svg>')
    return "\n".join(out)


# --------------------------------------------------------------------------
# 16:9 version
# --------------------------------------------------------------------------
def wide():
    W, H = 1920, 1080
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">', backdrop(W, H, 900)]
    out.append(logo(150, 110, 1.05))
    out.append(t(240, 112, "PYTHON ROADMAP", 64, weight=800, spacing=2))
    out.append(t(242, 160, "From print() to machine learning",
                 26, fill=MUTED))
    xs = [215 + k * 350 for k in range(5)]
    y1, y2 = 340, 730
    pos = [(x, y1) for x in xs] + [(x, y2) for x in reversed(xs)]
    d = (f"M {xs[0] - 120} {y1} L {xs[4]} {y1} "
         f"C {xs[4] + 230} {y1}, {xs[4] + 230} {y2}, {xs[4]} {y2} L {xs[0] - 120} {y2}")
    out.append(f'<path d="{d}" fill="none" stroke="#243049" stroke-width="22" '
               f'stroke-linecap="round"/>')
    out.append(f'<path d="{d}" fill="none" stroke="#3a4a6b" stroke-width="3" '
               f'stroke-dasharray="14 14" stroke-linecap="round"/>')
    for st, (x, y) in zip(STAGES, pos):
        col = CAT[st["cat"]]
        out.append(f'<circle cx="{x}" cy="{y}" r="50" fill="{BG}" stroke="{col}" '
                   f'stroke-width="8"/>')
        out.append(t(x, y + 16, str(st["n"]), 44, weight=800, anchor="middle", fill=col))
        out.append(t(x, y + 98, st["title"], 28, weight=800, anchor="middle")
                   .replace('<text ', f'<text paint-order="stroke" stroke="{BG}" '
                            f'stroke-width="10" ', 1))
        for k, kt in enumerate(st["key"]):
            out.append(t(x, y + 140 + k * 30, kt, 21, fill=MUTED, anchor="middle"))
    x = 105
    for c, s in (("core", "Core Python"), ("track", "Specialisation tracks"),
                 ("ai", "Machine Learning & AI")):
        out.append(f'<circle cx="{x + 10}" cy="1022" r="11" fill="{CAT[c]}"/>')
        out.append(t(x + 32, 1030, s, 23, weight=600))
        x += 70 + len(s) * 12.5
    out.append('</svg>')
    return "\n".join(out)


# --------------------------------------------------------------------------
# Instagram carousel (1080 x 1350, 4:5)
# --------------------------------------------------------------------------
IW, IH = 1080, 1350


def ig_frame(page, total, current_stage=None):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{IW}" height="{IH}" '
           f'viewBox="0 0 {IW} {IH}">', backdrop(IW, IH, 600)]
    # progress dots
    if current_stage is not None:
        gap = 34
        x0 = IW / 2 - gap * 4.5
        for k, st in enumerate(STAGES):
            col = CAT[st["cat"]]
            if k == current_stage:
                out.append(f'<rect x="{x0 + k*gap - 14}" y="62" width="28" height="12" '
                           f'rx="6" fill="{col}"/>')
            else:
                out.append(f'<circle cx="{x0 + k*gap}" cy="68" r="6" fill="{col}" '
                           f'opacity="{0.9 if k < current_stage else 0.25}"/>')
    out.append(t(IW - 60, IH - 50, f"{page} / {total}", 22, fill=MUTED, weight=600,
                 anchor="end", family=MONO))
    return out


def ig_cover(total):
    out = ig_frame(1, total)
    out.append(logo(IW / 2, 120, 1.1))
    out.append(t(IW / 2, 245, "PYTHON ROADMAP", 74, weight=800, anchor="middle",
                 spacing=2))
    out.append(t(IW / 2, 295, "For students & developers", 28, fill=MUTED,
                 anchor="middle"))
    # vertical timeline
    sx, top, step = 200, 380, 86
    out.append(f'<line x1="{sx}" y1="{top}" x2="{sx}" y2="{top + step*9}" '
               f'stroke="#243049" stroke-width="8" stroke-linecap="round"/>')
    for k, st in enumerate(STAGES):
        col = CAT[st["cat"]]
        y = top + k * step
        out.append(f'<circle cx="{sx}" cy="{y}" r="28" fill="{BG}" stroke="{col}" '
                   f'stroke-width="5"/>')
        out.append(t(sx, y + 10, str(st["n"]), 26, weight=800, anchor="middle", fill=col))
        out.append(t(sx + 56, y + 11, st["title"], 32, weight=700))
    out.append(t(60, IH - 50, "Swipe for each stage  →", 22, fill=MUTED, weight=600))
    out.append('</svg>')
    return "\n".join(out)


def ig_stage(st, page, total):
    col = CAT[st["cat"]]
    out = ig_frame(page, total, st["n"])
    # heading
    out.append(f'<circle cx="138" cy="215" r="58" fill="{BG}" stroke="{col}" '
               f'stroke-width="8"/>')
    out.append(t(138, 233, str(st["n"]), 54, weight=800, anchor="middle", fill=col))
    out.append(t(230, 182, f'STAGE {st["n"]}', 22, fill=col,
                 weight=700, spacing=2.5))
    size = 58 if len(st["title"]) <= 18 else 52
    out.append(t(228, 248, st["title"], size, weight=800))
    # card
    n = len(st["topics"])
    cy0, cy1 = 330, 1110
    out.append(f'<rect x="60" y="{cy0}" width="{IW-120}" height="{cy1-cy0}" rx="28" '
               f'fill="{CARD}" stroke="{CARD_EDGE}" stroke-width="2"/>')
    out.append(f'<rect x="60" y="{cy0}" width="{IW-120}" height="10" rx="5" fill="{col}"/>')
    out.append(t(104, cy0 + 70, "WHAT YOU'LL LEARN", 20, fill=MUTED, weight=700,
                 spacing=2.5))
    avail = cy1 - cy0 - 130
    row = min(92, avail / n)
    fs = 38 if row >= 80 else (34 if row >= 60 else 31)
    start = cy0 + 140 + (avail - row * n) / 3
    for k, topic in enumerate(st["topics"]):
        y = start + k * row
        out.append(f'<circle cx="114" cy="{y - 11}" r="7" fill="{col}"/>')
        out.append(t(144, y, topic, fs, opacity=0.95))
    # project bar
    tag, label = project_parts(st["project"])
    py = 1140
    out.append(f'<rect x="60" y="{py}" width="{IW-120}" height="96" rx="20" '
               f'fill="{col}" fill-opacity="0.13" stroke="{col}" stroke-opacity="0.55" '
               f'stroke-width="2"/>')
    out.append(t(100, py + 40, tag, 19, fill=col, weight=800, spacing=2))
    out.append(t(100, py + 76, label, 30, weight=700))
    out.append('</svg>')
    return "\n".join(out)


def ig_next(total):
    out = ig_frame(total, total)
    out.append(f'<circle cx="{IW/2}" cy="220" r="30" fill="#a78bfa"/>')
    out.append(t(IW / 2, 350, "WHAT'S NEXT?", 72, weight=800, anchor="middle",
                 spacing=2))
    out.append(t(IW / 2, 405, "Where Python can take you after the roadmap", 28,
                 fill=MUTED, anchor="middle"))
    for k, s in enumerate(NEXT):
        y = 500 + k * 126
        out.append(f'<rect x="140" y="{y}" width="{IW-280}" height="92" rx="46" '
                   f'fill="{CARD}" stroke="{CARD_EDGE}" stroke-width="2"/>')
        out.append(t(IW / 2, y + 58, s, 34, weight=700, anchor="middle"))
    out.append('</svg>')
    return "\n".join(out)


def render(svg, path_noext):
    with open(path_noext + ".svg", "w", encoding="utf-8") as f:
        f.write(svg)
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-o", path_noext + ".png", path_noext + ".svg"],
                       check=True)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    assets = os.path.join(here, "assets")
    ig = os.path.join(assets, "instagram")
    os.makedirs(ig, exist_ok=True)
    render(tall(), os.path.join(assets, "roadmap-dark"))
    render(wide(), os.path.join(assets, "roadmap-dark-16x9"))
    total = len(STAGES) + 2
    slides = [ig_cover(total)] + [ig_stage(st, i + 2, total)
                                  for i, st in enumerate(STAGES)] + [ig_next(total)]
    for i, svg in enumerate(slides, 1):
        render(svg, os.path.join(ig, f"slide-{i:02d}"))
    print("done:", total, "instagram slides")


if __name__ == "__main__":
    main()
