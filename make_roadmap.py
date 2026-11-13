"""Generate the Python Developer Roadmap graphics.

Outputs (in ./assets):
  roadmap.svg / roadmap.png              tall version for the GitHub README
  roadmap-16x9.svg / roadmap-16x9.png    1920x1080 overview for video

Edit STAGES below and re-run:  python make_roadmap.py
PNG export needs `rsvg-convert` (librsvg) on your PATH.
"""
import math
import os
import shutil
import subprocess
from html import escape

FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"

BG = "#f7f8fa"
INK = "#151515"
GREY = "#5b6270"
BLUE = "#2b6fd6"
MAIN = "#fff03a"      # stage boxes
SUB = "#fde8a6"       # topic boxes
NOTE = "#ffffff"

STAGES = [
    dict(n=0, title="Getting Started", eps="1–3",
         topics=["Why Python?", "Installing Python", "VS Code Setup",
                 "Terminal Basics", "REPL vs Scripts", "print() & Comments"],
         project="Your First Script", key=["Setup", "REPL", "First script"]),
    dict(n=1, title="Python Basics", eps="4–10",
         topics=["Variables & Data Types", "Operators", "Strings & f-strings",
                 "Input & Type Conversion", "Conditionals", "match-case",
                 "for & while Loops", "break & continue"],
         project="Guessing Game + Calculator",
         key=["Variables", "Conditionals", "Loops"]),
    dict(n=2, title="Data Structures", eps="11–17",
         topics=["Lists", "Tuples", "Sets", "Dictionaries",
                 "Comprehensions", "Big-O Basics"],
         project="Contact Book CLI",
         key=["Lists & Tuples", "Sets & Dicts", "Comprehensions"]),
    dict(n=3, title="Functions & Modules", eps="18–25",
         topics=["Functions", "*args & **kwargs", "Variable Scope",
                 "Lambdas", "map / filter / sorted", "Recursion",
                 "Standard Library", "pip & venv"],
         project="Password Generator + Quiz",
         key=["Functions", "Modules", "pip & venv"]),
    dict(n=4, title="Intermediate Python & OOP", eps="26–36",
         topics=["Exceptions", "File Handling", "Dates & Times",
                 "Regular Expressions", "Classes & Objects", "Inheritance",
                 "Dunder Methods", "Dataclasses", "Iterators & Generators",
                 "Decorators", "Context Managers", "Type Hints"],
         project="Library Management System",
         key=["Exceptions & Files", "OOP", "Decorators"]),
    dict(n=5, title="Tools & Best Practices", eps="37–42",
         topics=["Git & GitHub", "Debugging & Logging", "PEP 8 & Ruff",
                 "Testing with pytest", "pyproject.toml & uv",
                 "Threading & asyncio"],
         project=None, key=["Git", "pytest", "Packaging"]),
    dict(n=6, title="GUI Development", eps="43–49",
         topics=["Tkinter Widgets", "Layouts & Events", "Dialogs & Menus",
                 "CustomTkinter", "PyUIBuilder (drag & drop)", "PySide6 (Qt)", "PyInstaller"],
         project="Expense Tracker App", key=["Tkinter", "PyUIBuilder", "PySide6"]),
    dict(n=7, title="NumPy & Data", eps="50–57",
         topics=["Jupyter Notebooks", "NumPy Arrays", "Indexing & Masks",
                 "Broadcasting", "Pandas DataFrames", "Cleaning & groupby",
                 "Matplotlib", "Seaborn"],
         project="Analyse a Real Dataset", key=["NumPy", "Pandas", "Matplotlib"]),
    dict(n=8, title="Web Development", eps="58–67",
         topics=["HTTP & JSON", "requests & APIs", "Web Scraping",
                 "SQL & SQLite", "Flask", "SQLAlchemy & Auth",
                 "FastAPI", "Django", "Docker & Deployment"],
         project="Blog or URL Shortener", key=["Flask", "FastAPI", "Django"]),
    dict(n=9, title="Machine Learning & AI", eps="68–77",
         topics=["ML Concepts", "Maths with NumPy", "Linear Regression",
                 "Classification", "Model Evaluation", "Pipelines",
                 "K-Means Clustering", "Neural Nets (PyTorch)",
                 "LLM APIs & Embeddings"],
         project="Capstone: ML Web App", key=["scikit-learn", "PyTorch", "LLM APIs"]),
]

NEXT = ["Data Science", "Deep Learning", "Automation & DevOps",
        "Game Development", "Cybersecurity", "DSA & Interviews"]


def t(x, y, s, size, fill=INK, weight=500, anchor="middle"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
            f'{escape(s)}</text>')


def box(x, y, w, h, fill, sw=2.6):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')


def dots(x1, y1, x2, y2):
    mx = (x1 + x2) / 2
    return (f'<path d="M {x1:.1f} {y1:.1f} C {mx:.1f} {y1:.1f}, {mx:.1f} {y2:.1f}, '
            f'{x2:.1f} {y2:.1f}" fill="none" stroke="{BLUE}" stroke-width="3.2" '
            f'stroke-linecap="round" stroke-dasharray="0.1 8.5"/>')


def check(cx, cy, r=11):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GREY}"/>'
            f'<path d="M {cx-5} {cy} l 3.5 3.8 l 6.5 -7.5" fill="none" stroke="#fff" '
            f'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')


# --------------------------------------------------------------------------
# Tall README version
# --------------------------------------------------------------------------
def tall():
    W = 1600
    CX = W / 2
    MW, MH = 440, 78             # stage box
    SW, SH, PITCH = 400, 52, 64  # topic boxes
    LX = 70                      # left column x
    RX = W - 70 - SW             # right column x
    body, spine_pts = [], []

    y = 450
    blocks = []
    for st in STAGES:
        n = len(st["topics"])
        left = st["topics"][: math.ceil(n / 2)]
        right = st["topics"][math.ceil(n / 2):]
        items_l = [(s, "topic") for s in left]
        items_r = [(s, "topic") for s in right]
        if st["project"]:
            (items_r if len(items_r) <= len(items_l) else items_l).append(
                (st["project"], "project"))
        rows = max(len(items_l), len(items_r))
        hblk = max(rows * PITCH - (PITCH - SH), MH)
        blocks.append((st, items_l, items_r, y, hblk))
        y += hblk + (230 if st["n"] == 5 else 120)
    # "keep exploring" block
    nl, nr = NEXT[:3], NEXT[3:]
    end_y = y
    end_h = 3 * PITCH - (PITCH - SH)
    H = int(end_y + end_h + 110)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="{BG}"/>']

    # ---- header ----
    out.append(f'<line x1="{CX}" y1="40" x2="{CX}" y2="140" stroke="{BLUE}" '
               f'stroke-width="3.2" stroke-linecap="round" stroke-dasharray="0.1 9"/>')
    out.append(t(CX, 222, "Python Developer", 54, weight=700))
    out.append(t(CX, 286, "Roadmap", 54, weight=700))

    # info box (left)
    out.append(box(LX, 70, 420, 300, NOTE, 2.6))
    out.append(t(LX + 30, 118, "How to follow this roadmap", 23, weight=700,
                 anchor="start"))
    tips = ["Stages 0–5 in order (core)", "Stages 6–8 in any order",
            "Stage 9 needs Stages 7 & 8", "Build each project before",
            "moving on"]
    yy = 168
    for k, s in enumerate(tips):
        if k != 4:
            out.append(check(LX + 42, yy - 7))
        out.append(t(LX + 66, yy, s, 21, anchor="start"))
        yy += 44 if k != 3 else 32

    # legend box (right)
    out.append(box(RX - 20, 70, 420, 300, NOTE, 2.6))
    out.append(t(RX + 10, 118, "Legend", 23, weight=700, anchor="start"))
    lg = [(MAIN, "Stage"), (SUB, "Topic"),
          (NOTE, "Project")]
    for k, (c, s) in enumerate(lg):
        by = 150 + k * 62
        out.append(box(RX + 10, by, 64, 38, c, 2.2))
        out.append(t(RX + 94, by + 26, s, 21, anchor="start"))

    # ---- spine ----
    first_mid = blocks[0][3] + blocks[0][4] / 2
    out.append(f'<line x1="{CX}" y1="318" x2="{CX}" y2="{end_y + end_h/2:.0f}" '
               f'stroke="{BLUE}" stroke-width="4"/>')

    # ---- stages ----
    for st, il, ir, by, hb in blocks:
        mcy = by + hb / 2
        mx, my = CX - MW / 2, mcy - MH / 2
        for items, side in ((il, "L"), (ir, "R")):
            ch = len(items) * PITCH - (PITCH - SH)
            top = mcy - ch / 2
            for k, (label, kind) in enumerate(items):
                bx = LX if side == "L" else RX
                byy = top + k * PITCH
                bcy = byy + SH / 2
                if side == "L":
                    out.append(dots(mx - 8, mcy, bx + SW + 8, bcy))
                else:
                    out.append(dots(mx + MW + 8, mcy, bx - 8, bcy))
                if kind == "topic":
                    out.append(box(bx, byy, SW, SH, SUB))
                    out.append(t(bx + SW / 2, bcy + 8, label, 21))
                else:
                    out.append(box(bx, byy, SW, SH, NOTE))
                    out.append(check(bx + 30, bcy))
                    out.append(t(bx + 54, bcy + 8, label, 21, weight=600,
                                 anchor="start"))
        out.append(box(mx, my, MW, MH, MAIN, 3))
        out.append(t(CX, my + 30, f'Stage {st["n"]}', 15,
                     fill="#4a4a3a", weight=600))
        out.append(t(CX, my + 60, st["title"], 25, weight=700))

        if st["n"] == 5:   # checkpoint note on the spine
            ny = by + hb + 68
            out.append(box(CX - 300, ny, 600, 92, NOTE, 2.6))
            out.append(t(CX, ny + 39, "Core Python complete", 21, weight=700))
            out.append(t(CX, ny + 69, "Pick a track below, or do all three", 19,
                         fill=GREY))

    # ---- keep exploring ----
    mcy = end_y + end_h / 2
    mx = CX - MW / 2
    for items, side in ((nl, "L"), (nr, "R")):
        for k, label in enumerate(items):
            bx = LX if side == "L" else RX
            byy = end_y + k * PITCH
            bcy = byy + SH / 2
            if side == "L":
                out.append(dots(mx - 8, mcy, bx + SW + 8, bcy))
            else:
                out.append(dots(mx + MW + 8, mcy, bx - 8, bcy))
            out.append(box(bx, byy, SW, SH, SUB))
            out.append(t(bx + SW / 2, bcy + 8, label, 21))
    out.append(box(mx, mcy - MH / 2, MW, MH, MAIN, 3))
    out.append(t(CX, mcy + 9, "Keep Exploring", 25, weight=700))

    out.append('</svg>')
    return "\n".join(out)


# --------------------------------------------------------------------------
# 16:9 version
# --------------------------------------------------------------------------
def wide():
    W, H = 1920, 1080
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    out.append(t(110, 140, "Python Developer Roadmap", 58, weight=700, anchor="start"))
    out.append(t(112, 190, "From the basics to machine learning",
                 24, fill=GREY, weight=500, anchor="start"))

    BW, BH = 300, 84
    xs = [230 + k * 365 for k in range(5)]
    y1, y2 = 380, 780
    pos = [(x, y1) for x in xs] + [(x, y2) for x in reversed(xs)]

    d = (f"M {xs[0] - 150} {y1} L {xs[4]} {y1} "
         f"C {xs[4] + 260} {y1}, {xs[4] + 260} {y2}, {xs[4]} {y2} "
         f"L {xs[0] - 150} {y2}")
    out.append(f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="4"/>')

    for st, (x, y) in zip(STAGES, pos):
        # topic card below
        ty = y + BH / 2 + 34
        out.append(f'<line x1="{x}" y1="{y + BH/2}" x2="{x}" y2="{ty}" stroke="{BLUE}" '
                   f'stroke-width="3.2" stroke-linecap="round" stroke-dasharray="0.1 8"/>')
        out.append(box(x - 120, ty, 240, 118, SUB, 2.4))
        for k, kt in enumerate(st["key"]):
            out.append(t(x, ty + 34 + k * 33, kt, 20))
        # stage box
        out.append(box(x - BW / 2, y - BH / 2, BW, BH, MAIN, 3))
        out.append(t(x, y - 9, f'Stage {st["n"]}', 15,
                     fill="#4a4a3a", weight=600))
        title = st["title"].replace("Intermediate Python & OOP", "Intermediate & OOP")
        out.append(t(x, y + 24, title, 23, weight=700))
    out.append('</svg>')
    return "\n".join(out)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    assets = os.path.join(here, "assets")
    os.makedirs(assets, exist_ok=True)
    for name, svg in (("roadmap", tall()), ("roadmap-16x9", wide())):
        svg_path = os.path.join(assets, f"{name}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        if shutil.which("rsvg-convert"):
            subprocess.run(["rsvg-convert", "-o", os.path.join(assets, f"{name}.png"),
                            svg_path], check=True)
        print("wrote", svg_path)


if __name__ == "__main__":
    main()
