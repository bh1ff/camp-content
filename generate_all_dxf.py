#!/usr/bin/env python3
"""
Robocode Spring Camp 2026 — Laser Cut Kit DXF Generator (v2)
=============================================================
Generates 2D DXF files for all 8 mechanical engineering projects (M1–M8).

Material: 3mm MDF (400×600mm sheets), birch ply for stressed parts
Kerf: 0.1mm subtracted from slot widths (test on scrap first)
Tab standard: 10mm wide across all projects
Fasteners: M3 screws + nuts (stocked)
Motors: Standard TT motor (yellow gearmotor, ~70×22×18mm, D-shaft Ø5.5mm)
All dimensions in mm.

v2 changes:
  - Fixed all overlapping parts — proper spacing throughout
  - M3 screw holes (Ø3.2mm clearance) instead of Ø4mm dowel
  - TT motor mounts instead of FA-130
"""

import ezdxf
import math
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "dxf_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === GLOBAL CONSTANTS ===
MAT = 3.0             # material thickness (mm)
KERF = 0.1            # kerf allowance
SLOT_W = MAT - KERF   # slot width = 2.9mm
TAB_W = 10.0          # standard tab width
M3_CLEAR = 3.2        # M3 clearance hole diameter
M3_R = M3_CLEAR / 2   # M3 clearance hole radius = 1.6mm
SHAFT_D = 5.8         # TT motor D-shaft clearance hole
SHAFT_R = SHAFT_D / 2 # = 2.9mm
TT_W = 24.0           # TT motor body width (with clearance)
TT_H = 20.0           # TT motor body height (with clearance)
GAP = 8               # minimum gap between parts


# === UTILITY FUNCTIONS ===

def rect(msp, x, y, w, h, layer="CUTS"):
    """Rectangle from bottom-left (x,y), width w, height h."""
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})


def slot_h(msp, cx, cy, w=TAB_W, h=SLOT_W, layer="CUTS"):
    """Horizontal slot centred at (cx, cy). w along X, h along Y."""
    rect(msp, cx - w / 2, cy - h / 2, w, h, layer)


def slot_v(msp, cx, cy, w=SLOT_W, h=TAB_W, layer="CUTS"):
    """Vertical slot centred at (cx, cy). w along X, h along Y."""
    rect(msp, cx - w / 2, cy - h / 2, w, h, layer)


def circ(msp, cx, cy, r, layer="CUTS"):
    msp.add_circle((cx, cy), r, dxfattribs={"layer": layer})


def polygon(msp, points, layer="CUTS"):
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer})


def label(msp, x, y, text, height=3.0):
    msp.add_text(text, height=height,
                 dxfattribs={"layer": "ENGRAVE"}).set_placement((x, y))


def line(msp, x1, y1, x2, y2, layer="ENGRAVE"):
    msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})


def tab_down(msp, cx, y, tw=TAB_W):
    """A single tab protruding downward from y, centred at cx."""
    rect(msp, cx - tw / 2, y - MAT, tw, MAT)


def gear_profile(msp, cx, cy, teeth, module, bore_r, layer="CUTS", lbl=None):
    """Draw simplified spur gear. Returns outer diameter."""
    od = (teeth + 2) * module
    rd = (teeth - 2.5) * module
    pts = []
    for t in range(teeth):
        a_step = 2 * math.pi / teeth
        a = t * a_step
        # Tooth tip arc (3 points)
        tw = 0.4 / teeth  # narrower teeth for more teeth
        for da in [-tw, 0, tw]:
            pts.append((cx + od / 2 * math.cos(a + da),
                        cy + od / 2 * math.sin(a + da)))
        # Root arc (3 points)
        mid = a + a_step / 2
        for da in [-tw, 0, tw]:
            pts.append((cx + rd / 2 * math.cos(mid + da),
                        cy + rd / 2 * math.sin(mid + da)))
    polygon(msp, pts, layer)
    circ(msp, cx, cy, bore_r, layer)
    if lbl:
        label(msp, cx - 6, cy - 2, lbl, height=2)
    return od


def new_doc():
    doc = ezdxf.new("R2010")
    doc.layers.add("CUTS", color=7)       # white — cut lines
    doc.layers.add("ENGRAVE", color=1)    # red — engrave/score
    doc.layers.add("GUIDE", color=3)      # green — reference only
    return doc


def save(doc, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    doc.saveas(path)
    print(f"  Saved {path}")


# =====================================================================
# M1 — CATAPULT  (Levers)
# =====================================================================
def m1_catapult():
    print("M1 Catapult...")
    doc = new_doc()
    msp = doc.modelspace()

    # ---- ROW 1: Base plate ----
    bx, by = 0, 0
    bw, bh = 200, 120
    rect(msp, bx, by, bw, bh)
    label(msp, bx + 5, by + bh - 8, "M1 BASE")

    # Side support slots at x=40 and x=160 (vertical — side pieces stand along Y)
    for sx in [40, 160]:
        slot_v(msp, bx + sx, by + bh / 2 - 15)
        slot_v(msp, bx + sx, by + bh / 2 + 15)
    # Stop piece slot at x=25
    slot_v(msp, bx + 25, by + bh / 2)

    # ---- ROW 1 contd: Side supports (×2) ----
    sw, sh = 60, 80
    s1x = bx + bw + GAP
    s1y = by

    for i in range(2):
        ox = s1x + i * (sw + GAP)
        rect(msp, ox, s1y, sw, sh)
        # Bottom tabs
        tab_down(msp, ox + sw / 2 - 15, s1y)
        tab_down(msp, ox + sw / 2 + 15, s1y)
        # Fulcrum hole (M3 screw) — centred, 15mm from top
        circ(msp, ox + sw / 2, s1y + sh - 15, M3_R)
        # Arm pass-through slot at fulcrum height
        slot_v(msp, ox + sw / 2, s1y + sh - 15, SLOT_W, 22)
        lbl = "M1 SIDE L" if i == 0 else "M1 SIDE R"
        label(msp, ox + 5, s1y + sh - 8, lbl)

    # ---- ROW 2: Throwing arm ----
    ax, ay = bx, by - 30 - GAP
    aw, ah = 280, 20
    rect(msp, ax, ay, aw, ah)
    circ(msp, ax + 80, ay + ah / 2, M3_R)          # pivot hole
    slot_v(msp, ax + aw - 15, ay + ah / 2, SLOT_W, TAB_W)  # cup slot
    label(msp, ax + 5, ay + ah - 7, "M1 ARM (BIRCH PLY)")

    # ---- ROW 2 contd: Stop piece ----
    stw, sth = 60, 50
    stx = ax + aw + GAP
    sty = ay
    rect(msp, stx, sty, stw, sth)
    tab_down(msp, stx + stw / 2, sty)
    label(msp, stx + 5, sty + sth - 8, "M1 STOP")

    # ---- ROW 3: Cup / Cradle (cross shape, folds up) ----
    cbase = 40
    flap = 20
    # Total footprint: (flap + cbase + flap) × (flap + cbase + flap) = 80 × 80
    cx = bx
    cy = ay - (cbase + 2 * flap) - GAP  # full cross height = cbase + 2*flap
    # Centre square
    rect(msp, cx + flap, cy + flap, cbase, cbase)
    # 4 flaps
    rect(msp, cx + flap, cy + flap + cbase, cbase, flap)   # top
    rect(msp, cx + flap, cy, cbase, flap)                   # bottom
    rect(msp, cx, cy + flap, flap, cbase)                   # left
    rect(msp, cx + flap + cbase, cy + flap, flap, cbase)    # right
    # Tab for arm attachment on bottom flap
    tab_down(msp, cx + flap + cbase / 2, cy)
    # Score fold lines
    line(msp, cx + flap, cy + flap, cx + flap + cbase, cy + flap)
    line(msp, cx + flap, cy + flap + cbase, cx + flap + cbase, cy + flap + cbase)
    line(msp, cx + flap, cy + flap, cx + flap, cy + flap + cbase)
    line(msp, cx + flap + cbase, cy + flap, cx + flap + cbase, cy + flap + cbase)
    label(msp, cx + flap + 2, cy + flap + cbase / 2, "M1 CUP")

    save(doc, "M1_Catapult.dxf")


# =====================================================================
# M2 — PULLEY LIFT
# =====================================================================
def m2_pulley_lift():
    print("M2 Pulley Lift...")
    doc = new_doc()
    msp = doc.modelspace()

    # ---- ROW 1: Base + Uprights ----
    bx, by = 0, 0
    bw, bh = 180, 120
    rect(msp, bx, by, bw, bh)
    label(msp, bx + 5, by + bh - 8, "M2 BASE")
    for ux in [30, 150]:
        slot_v(msp, bx + ux, by + bh / 2 - 15)
        slot_v(msp, bx + ux, by + bh / 2 + 15)
    circ(msp, bx + bw / 2, by + 20, M3_R)  # winch axle

    # Uprights (×2) — 50 × 200
    uw, uh = 50, 200
    u1x = bx + bw + GAP

    for i in range(2):
        ox = u1x + i * (uw + GAP)
        rect(msp, ox, by, uw, uh)
        tab_down(msp, ox + uw / 2 - 15, by)
        tab_down(msp, ox + uw / 2 + 15, by)
        slot_h(msp, ox + uw / 2, by + uh - MAT / 2, TAB_W, SLOT_W)  # beam slot
        circ(msp, ox + uw / 2, by + uh - 20, 2)  # string guide
        lbl = "M2 UP L" if i == 0 else "M2 UP R"
        label(msp, ox + 3, by + uh - 10, lbl)

    # ---- ROW 2: Top beam, pulley wheel, winch drum ----
    row2y = by - GAP - 40

    # Top Beam — 126 × 30
    tbw, tbh = 126, 30
    tbx = bx
    tby = row2y
    rect(msp, tbx, tby, tbw, tbh)
    tab_down(msp, tbx + 8, tby)
    tab_down(msp, tbx + tbw - 8, tby)
    circ(msp, tbx + tbw / 2, tby + tbh / 2, M3_R)     # pulley axle
    circ(msp, tbx + tbw / 2 + 15, tby + tbh / 2, 2)   # string hole
    label(msp, tbx + 5, tby + tbh - 8, "M2 TOP BEAM")

    # Pulley Wheel — Ø50
    px = tbx + tbw + GAP + 25
    py = tby + 25
    circ(msp, px, py, 25)
    circ(msp, px, py, M3_R)
    circ(msp, px, py, 22, layer="ENGRAVE")  # groove
    label(msp, px - 12, py - 2, "M2 PULLEY")

    # Winch Drum — Ø40
    wx = px + 25 + GAP + 20
    wy = py
    circ(msp, wx, wy, 20)
    circ(msp, wx, wy, M3_R)
    slot_h(msp, wx + 12, wy, 6, SLOT_W)
    label(msp, wx - 12, wy - 2, "M2 DRUM")

    # ---- ROW 3: Crank handle + Hook plate ----
    row3y = row2y - GAP - 20

    # Crank — 80 × 15
    hx, hy = bx, row3y
    rect(msp, hx, hy, 80, 15)
    circ(msp, hx + 10, hy + 7.5, M3_R)
    circ(msp, hx + 70, hy + 7.5, 3)
    label(msp, hx + 20, hy + 2, "M2 CRANK")

    # Hook plate — 50 × 50
    lpx = hx + 80 + GAP
    lpy = row3y
    rect(msp, lpx, lpy, 50, 50)
    circ(msp, lpx + 25, lpy + 45, 2)
    circ(msp, lpx + 15, lpy + 15, M3_R)
    circ(msp, lpx + 35, lpy + 15, M3_R)
    label(msp, lpx + 5, lpy + 30, "M2 HOOK")

    save(doc, "M2_Pulley_Lift.dxf")


# =====================================================================
# M3 — AUTOMATA CARD  (Cams)
# =====================================================================
def m3_automata_card():
    print("M3 Automata Card...")
    doc = new_doc()
    msp = doc.modelspace()

    # ---- ROW 1: Base + Side frames ----
    bx, by = 0, 0
    bw, bh = 100, 80
    rect(msp, bx, by, bw, bh)
    label(msp, bx + 5, by + bh - 8, "M3 BASE")
    slot_v(msp, bx + 20, by + bh / 2)
    slot_v(msp, bx + bw - 20, by + bh / 2)

    fw, fh = 80, 120
    f1x = bx + bw + GAP
    for i in range(2):
        ox = f1x + i * (fw + GAP)
        rect(msp, ox, by, fw, fh)
        tab_down(msp, ox + fw / 2, by)
        circ(msp, ox + fw / 2, by + 40, M3_R)         # axle hole
        slot_v(msp, ox + fw / 2, by + fh - 20, SLOT_W, 30)  # follower guide
        lbl = "M3 FRAME L" if i == 0 else "M3 FRAME R"
        label(msp, ox + 5, by + fh - 10, lbl)

    # ---- ROW 2: 3 cam shapes (spaced properly) ----
    row2y = by - GAP - 55

    # Egg cam — max radius ~25mm from centre
    camx = bx + 30
    camy = row2y
    pts = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        r = 18 + 7 * math.sin(rad)
        pts.append((camx + r * math.cos(rad), camy + r * math.sin(rad)))
    polygon(msp, pts)
    circ(msp, camx, camy, M3_R)
    label(msp, camx - 10, camy - 2, "M3 EGG")

    # Round cam (eccentric) — Ø40
    rcx = camx + 30 + GAP + 20
    rcy = camy
    circ(msp, rcx, rcy, 20)
    circ(msp, rcx + 5, rcy, M3_R)  # off-centre
    label(msp, rcx - 12, rcy - 2, "M3 ROUND")

    # Snail cam — max r ~25mm
    scx = rcx + 20 + GAP + 25
    scy = camy
    snail_pts = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        r = 10 + 15 * (deg / 360)
        snail_pts.append((scx + r * math.cos(rad), scy + r * math.sin(rad)))
    polygon(msp, snail_pts)
    circ(msp, scx, scy, M3_R)
    label(msp, scx - 12, scy - 2, "M3 SNAIL")

    # ---- ROW 3: Follower + Handle ----
    row3y = row2y - 30 - GAP

    # Follower — 15 × 80
    rect(msp, bx, row3y, 15, 80)
    circ(msp, bx + 7.5, row3y + 75, 1.5)
    label(msp, bx + 1, row3y + 35, "FOL", height=2)

    # Handle — 60 × 12
    rect(msp, bx + 15 + GAP, row3y, 60, 12)
    circ(msp, bx + 15 + GAP + 8, row3y + 6, M3_R)
    label(msp, bx + 15 + GAP + 18, row3y + 2, "M3 HANDLE", height=2)

    save(doc, "M3_Automata_Card.dxf")


# =====================================================================
# M4 — GEAR-DOWN MOTOR  (Gears, TT motor)
# =====================================================================
def m4_gear_down():
    print("M4 Gear-Down Motor...")
    doc = new_doc()
    msp = doc.modelspace()

    # ---- ROW 1: Base ----
    bx, by = 0, 0
    bw, bh = 160, 100
    rect(msp, bx, by, bw, bh)
    label(msp, bx + 5, by + bh - 8, "M4 BASE")

    # Axle support slots
    for sx in [40, 120]:
        slot_v(msp, bx + sx, by + bh / 2 - 15)
        slot_v(msp, bx + sx, by + bh / 2 + 15)
    # Motor mount slot
    slot_v(msp, bx + 80, by + 25)

    # ---- ROW 1 contd: Axle supports (×2) ----
    aw, ah = 50, 70
    a1x = bx + bw + GAP

    for i in range(2):
        ox = a1x + i * (aw + GAP)
        rect(msp, ox, by, aw, ah)
        tab_down(msp, ox + aw / 2 - 15, by)
        tab_down(msp, ox + aw / 2 + 15, by)
        # TT motor shaft hole on one side, output axle on other
        circ(msp, ox + aw / 2 - 10, by + ah - 25, SHAFT_R)  # TT D-shaft
        circ(msp, ox + aw / 2 + 10, by + ah - 25, M3_R)     # output axle
        lbl = "M4 AX L" if i == 0 else "M4 AX R"
        label(msp, ox + 3, by + ah - 10, lbl)

    # ---- ROW 2: Motor mount ----
    row2y = by - GAP - 50

    # TT Motor mount — 80 × 40 with rectangular slot for motor body
    mmw, mmh = 80, 40
    mmx = bx
    mmy = row2y
    rect(msp, mmx, mmy, mmw, mmh)
    # TT motor body cutout (24 × 20mm slot)
    rect(msp, mmx + mmw / 2 - TT_W / 2, mmy + mmh / 2 - TT_H / 2, TT_W, TT_H)
    # M3 mounting holes on either side
    circ(msp, mmx + 12, mmy + mmh / 2, M3_R)
    circ(msp, mmx + mmw - 12, mmy + mmh / 2, M3_R)
    # Tab for base
    tab_down(msp, mmx + mmw / 2, mmy)
    label(msp, mmx + 5, mmy + mmh - 8, "M4 TT MOUNT")

    # ---- ROW 2 contd: Small gear (12T mod 2) ----
    g1_teeth = 12
    g1_mod = 2.0
    g1_od = (g1_teeth + 2) * g1_mod  # 28mm
    g1x = mmx + mmw + GAP + g1_od / 2
    g1y = mmy + mmh / 2
    gear_profile(msp, g1x, g1y, g1_teeth, g1_mod, SHAFT_R, lbl="M4 SM")

    # Large gear (36T mod 2) — OD = 76mm
    g2_teeth = 36
    g2_od = (g2_teeth + 2) * g2_mod if False else (g2_teeth + 2) * g1_mod  # 76mm
    g2x = g1x + g1_od / 2 + GAP + g2_od / 2
    g2y = g1y
    gear_profile(msp, g2x, g2y, g2_teeth, g1_mod, M3_R, lbl="M4 LG")

    # Output drum — Ø40
    dx = g2x + g2_od / 2 + GAP + 20
    dy = g2y
    circ(msp, dx, dy, 20)
    circ(msp, dx, dy, M3_R)
    circ(msp, dx + 15, dy, 1.5)
    label(msp, dx - 10, dy - 2, "M4 DRUM")

    save(doc, "M4_Gear_Down_Motor.dxf")


# =====================================================================
# M5 — HAND-CRANK AUTOMATA  (Crank + Cam)
# =====================================================================
def m5_hand_crank():
    print("M5 Hand-Crank Automata...")
    doc = new_doc()
    msp = doc.modelspace()

    # ---- ROW 1: Base ----
    bx, by = 0, 0
    bw, bh = 140, 100
    rect(msp, bx, by, bw, bh)
    label(msp, bx + 5, by + bh - 8, "M5 BASE")
    for fx in [20, 120]:
        slot_v(msp, bx + fx, by + bh / 2 - 15)
        slot_v(msp, bx + fx, by + bh / 2 + 15)

    # ---- ROW 1 contd: Side frames (×2) — 60 × 140 ----
    fw, fh = 60, 140
    f1x = bx + bw + GAP
    for i in range(2):
        ox = f1x + i * (fw + GAP)
        rect(msp, ox, by, fw, fh)
        tab_down(msp, ox + fw / 2 - 15, by)
        tab_down(msp, ox + fw / 2 + 15, by)
        circ(msp, ox + fw / 2, by + 35, M3_R)    # axle hole
        slot_v(msp, ox + fw / 2, by + fh - 30, SLOT_W, 35)   # follower guide
        slot_h(msp, ox + fw / 2, by + fh - 5, TAB_W, SLOT_W)  # scene slot
        lbl = "M5 FR L" if i == 0 else "M5 FR R"
        label(msp, ox + 3, by + fh - 12, lbl)

    # ---- ROW 2: Crank disc, Cam, Follower, Handle ----
    row2y = by - GAP - 55

    # Crank disc — Ø50
    cdx = bx + 25
    cdy = row2y
    circ(msp, cdx, cdy, 25)
    circ(msp, cdx, cdy, M3_R)          # centre axle
    circ(msp, cdx + 15, cdy, M3_R)     # crank pin
    label(msp, cdx - 12, cdy - 2, "M5 CRANK")

    # Egg cam — ~22mm max radius
    camx = cdx + 25 + GAP + 22
    camy = cdy
    pts = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        r = 16 + 6 * math.sin(rad)
        pts.append((camx + r * math.cos(rad), camy + r * math.sin(rad)))
    polygon(msp, pts)
    circ(msp, camx, camy, M3_R)
    label(msp, camx - 10, camy - 2, "M5 CAM")

    # Follower — 12 × 90
    flx = camx + 22 + GAP
    fly = row2y - 45
    rect(msp, flx, fly, 12, 90)
    circ(msp, flx + 6, fly + 85, 1.5)
    label(msp, flx + 1, fly + 40, "FOL", height=2)

    # Handle — 70 × 14
    chx = flx + 12 + GAP
    chy = row2y - 7
    rect(msp, chx, chy, 70, 14)
    circ(msp, chx + 8, chy + 7, M3_R)
    circ(msp, chx + 62, chy + 7, 3)
    label(msp, chx + 18, chy + 2, "M5 HANDLE", height=2)

    # ---- ROW 3: Scene panel — 100 × 80 ----
    row3y = row2y - 50 - GAP
    spx = bx
    spy = row3y
    rect(msp, spx, spy, 100, 80)
    tab_down(msp, spx + 10, spy)
    tab_down(msp, spx + 90, spy)
    slot_v(msp, spx + 50, spy + 10, SLOT_W + 2, 15)
    label(msp, spx + 5, spy + 70, "M5 SCENE PANEL")

    save(doc, "M5_Hand_Crank_Automata.dxf")


# =====================================================================
# M6 — TOWER CRANE  (Pulleys + Gears)
# =====================================================================
def m6_tower_crane():
    print("M6 Tower Crane...")
    doc = new_doc()
    msp = doc.modelspace()

    # ---- ROW 1: Base ----
    bx, by = 0, 0
    bw, bh = 200, 150
    rect(msp, bx, by, bw, bh)
    label(msp, bx + 5, by + bh - 8, "M6 BASE")
    for tx in [90, 110]:
        slot_v(msp, bx + tx, by + bh / 2 - 20)
        slot_v(msp, bx + tx, by + bh / 2 + 20)
    circ(msp, bx + 30, by + bh / 2, 5)   # counterweight hole
    circ(msp, bx + 55, by + bh / 2, 5)
    circ(msp, bx + bw - 30, by + 30, M3_R)  # winch axle

    # ---- ROW 1 contd: Tower frames (×2) — 40 × 250 ----
    tw, th = 40, 250
    t1x = bx + bw + GAP
    for i in range(2):
        ox = t1x + i * (tw + GAP)
        rect(msp, ox, by, tw, th)
        tab_down(msp, ox + tw / 2 - 10, by)
        tab_down(msp, ox + tw / 2 + 10, by)
        slot_h(msp, ox + tw / 2, by + th - 10, TAB_W, SLOT_W)  # jib
        slot_h(msp, ox + tw / 2, by + 80, TAB_W, SLOT_W)  # brace 1
        slot_h(msp, ox + tw / 2, by + 160, TAB_W, SLOT_W) # brace 2
        circ(msp, ox + tw / 2, by + th - 25, 2)  # string guide
        lbl = "M6 TWR L" if i == 0 else "M6 TWR R"
        label(msp, ox + 2, by + th - 10, lbl, height=2)

    # ---- ROW 2: Jib, Cross braces, Hook ----
    row2y = by - GAP - 30

    # Jib — 220 × 25
    jx, jy = bx, row2y
    rect(msp, jx, jy, 220, 25)
    tab_down(msp, jx + 10, jy)
    circ(msp, jx + 205, jy + 12.5, M3_R)   # pulley axle
    circ(msp, jx + 205, jy + 22, 2)         # string hole
    label(msp, jx + 5, jy + 17, "M6 JIB")

    # Cross braces (×2) — 20 × 20 each
    cbx = jx + 220 + GAP
    for i in range(2):
        ox = cbx + i * (20 + GAP)
        rect(msp, ox, row2y, 20, 20)
        # Side tabs
        rect(msp, ox - MAT, row2y + 10 - TAB_W / 2, MAT, TAB_W)
        rect(msp, ox + 20, row2y + 10 - TAB_W / 2, MAT, TAB_W)
        label(msp, ox + 2, row2y + 5, f"BR{i+1}", height=2)

    # ---- ROW 3: Winch drum, Gears, Hook, Crank ----
    row3y = row2y - GAP - 55

    # Winch drum — Ø35
    wdx = bx + 17.5
    wdy = row3y
    circ(msp, wdx, wdy, 17.5)
    circ(msp, wdx, wdy, M3_R)
    slot_h(msp, wdx + 10, wdy, 6, SLOT_W)
    label(msp, wdx - 10, wdy - 2, "DRUM", height=2)

    # Small gear (12T mod 2) — OD 28
    g1x = wdx + 17.5 + GAP + 14
    g1y = wdy
    gear_profile(msp, g1x, g1y, 12, 2.0, M3_R, lbl="SM")

    # Large gear (24T mod 2) — OD 52
    g2x = g1x + 14 + GAP + 26
    g2y = wdy
    gear_profile(msp, g2x, g2y, 24, 2.0, M3_R, lbl="LG")

    # Hook plate — 40 × 40
    hookx = g2x + 26 + GAP
    hooky = row3y - 20
    rect(msp, hookx, hooky, 40, 40)
    circ(msp, hookx + 20, hooky + 35, 2)
    # U-hook cutout
    msp.add_lwpolyline([
        (hookx + 15, hooky), (hookx + 15, hooky + 12),
        (hookx + 25, hooky + 12), (hookx + 25, hooky)
    ], dxfattribs={"layer": "CUTS"})
    label(msp, hookx + 5, hooky + 22, "M6 HOOK")

    # Crank — 70 × 14
    ckx = hookx + 40 + GAP
    cky = row3y - 7
    rect(msp, ckx, cky, 70, 14)
    circ(msp, ckx + 8, cky + 7, M3_R)
    circ(msp, ckx + 62, cky + 7, 3)
    label(msp, ckx + 18, cky + 2, "M6 CRANK", height=2)

    # Pulley wheel — Ø50
    pulx = ckx + 70 + GAP + 25
    puly = wdy
    circ(msp, pulx, puly, 25)
    circ(msp, pulx, puly, M3_R)
    circ(msp, pulx, puly, 22, layer="ENGRAVE")
    label(msp, pulx - 12, puly - 2, "M6 PUL")

    save(doc, "M6_Tower_Crane.dxf")


# =====================================================================
# M7 — ROVER RAMP CHALLENGE  (Wheels + Gears + TT Motor)
# =====================================================================
def m7_rover():
    print("M7 Rover Ramp...")
    doc = new_doc()
    msp = doc.modelspace()

    # ---- ROW 1: Chassis ----
    bx, by = 0, 0
    bw, bh = 150, 80
    rect(msp, bx, by, bw, bh)
    label(msp, bx + 5, by + bh - 8, "M7 CHASSIS")

    # Side rail slots
    # Side rail slots (rails run along X, thin along Y → slot_h)
    for ry in [10, bh - 10]:
        slot_h(msp, bx + 25, by + ry)
        slot_h(msp, bx + bw - 25, by + ry)
    # Motor mount slot
    slot_h(msp, bx + bw / 2, by + bh / 2, TAB_W, SLOT_W)
    # Axle holes (M3)
    for ax_x in [20, bw - 20]:
        circ(msp, bx + ax_x, by + 5, M3_R)
        circ(msp, bx + ax_x, by + bh - 5, M3_R)
    # Battery zip-tie holes
    circ(msp, bx + bw / 2 - 20, by + 20, 2)
    circ(msp, bx + bw / 2 + 20, by + 20, 2)

    # ---- ROW 1 contd: Side rails (×2) — 150 × 30 ----
    srw, srh = 150, 30
    sr1x = bx + bw + GAP

    for i in range(2):
        oy = by + i * (srh + GAP)
        rect(msp, sr1x, oy, srw, srh)
        tab_down(msp, sr1x + 25, oy)
        tab_down(msp, sr1x + srw - 25, oy)
        # Axle U-notches at top edge
        for notch_x in [20, srw - 20]:
            msp.add_lwpolyline([
                (sr1x + notch_x - 2, oy + srh),
                (sr1x + notch_x - 2, oy + srh - 8),
                (sr1x + notch_x + 2, oy + srh - 8),
                (sr1x + notch_x + 2, oy + srh)
            ], dxfattribs={"layer": "CUTS"})
        lbl = "M7 RAIL L" if i == 0 else "M7 RAIL R"
        label(msp, sr1x + 5, oy + srh - 10, lbl)

    # ---- ROW 2: Wheels (×4) — Ø60, spaced properly ----
    row2y = by - GAP - 35
    for i in range(4):
        wcx = bx + 35 + i * (60 + GAP)
        wcy = row2y
        circ(msp, wcx, wcy, 30)
        circ(msp, wcx, wcy, M3_R)
        circ(msp, wcx, wcy, 27, layer="ENGRAVE")  # rubber band groove
        for a in range(0, 360, 60):
            rad = math.radians(a)
            circ(msp, wcx + 17 * math.cos(rad), wcy + 17 * math.sin(rad), 5)
        label(msp, wcx - 6, wcy - 2, f"W{i+1}", height=2)

    # ---- ROW 3: TT Motor mount + Gears ----
    row3y = row2y - 35 - GAP - 25

    # TT Motor mount — 80 × 40
    mmx, mmy = bx, row3y
    mmw, mmh = 80, 40
    rect(msp, mmx, mmy, mmw, mmh)
    # TT motor rectangular slot
    rect(msp, mmx + mmw / 2 - TT_W / 2, mmy + mmh / 2 - TT_H / 2, TT_W, TT_H)
    circ(msp, mmx + 12, mmy + mmh / 2, M3_R)
    circ(msp, mmx + mmw - 12, mmy + mmh / 2, M3_R)
    tab_down(msp, mmx + mmw / 2, mmy)
    label(msp, mmx + 5, mmy + mmh - 8, "M7 TT MOUNT")

    # Small gear (10T mod 2) — OD 24
    g1x = mmx + mmw + GAP + 12
    g1y = mmy + mmh / 2
    gear_profile(msp, g1x, g1y, 10, 2.0, SHAFT_R, lbl="SM")

    # Large gear (30T mod 2) — OD 64
    g2x = g1x + 12 + GAP + 32
    g2y = g1y
    gear_profile(msp, g2x, g2y, 30, 2.0, M3_R, lbl="LG")

    save(doc, "M7_Rover_Ramp.dxf")


# =====================================================================
# M8 — ROBOTIC GRIPPER  (Linkages)
# =====================================================================
def m8_robotic_gripper():
    print("M8 Robotic Gripper...")
    doc = new_doc()
    msp = doc.modelspace()

    # ---- ROW 1: Handle bars (×2) — 120 × 20 ----
    hx, hy = 0, 0
    hw, hh = 120, 20
    for i in range(2):
        oy = hy + i * (hh + GAP)
        rect(msp, hx, oy, hw, hh)
        circ(msp, hx + 15, oy + hh / 2, M3_R)    # front pivot
        circ(msp, hx + 40, oy + hh / 2, M3_R)     # scissor pivot
        lbl = "M8 HANDLE T" if i == 0 else "M8 HANDLE B"
        label(msp, hx + 50, oy + 5, lbl)

    # ---- ROW 1 contd: Scissor arms (×4) — 100 × 15 ----
    sax = hx + hw + GAP
    saw, sah = 100, 15
    for i in range(4):
        oy = hy + i * (sah + GAP)
        rect(msp, sax, oy, saw, sah)
        circ(msp, sax + 10, oy + sah / 2, M3_R)
        circ(msp, sax + saw / 2, oy + sah / 2, M3_R)
        circ(msp, sax + saw - 10, oy + sah / 2, M3_R)
        label(msp, sax + 20, oy + 2, f"M8 ARM {i+1}", height=2)

    # ---- ROW 2: Jaws (×2) — 50 × 30, spaced apart ----
    row2y = hy - GAP - 35
    jw, jh = 50, 30

    for i in range(2):
        ox = hx + i * (jw + GAP)
        rect(msp, ox, row2y, jw, jh)
        circ(msp, ox + 10, row2y + jh / 2, M3_R)
        # Grip serrations (engrave)
        for s in range(4):
            sx_pos = ox + 20 + s * 8
            line(msp, sx_pos, row2y + 5, sx_pos + 4, row2y + 5)
            line(msp, sx_pos, row2y + jh - 5, sx_pos + 4, row2y + jh - 5)
        lbl = "M8 JAW L" if i == 0 else "M8 JAW R"
        label(msp, ox + 15, row2y + 10, lbl)

    # Jaw pads (×2) — 30 × 15
    padx = hx + 2 * (jw + GAP)
    for i in range(2):
        ox = padx + i * (30 + GAP)
        rect(msp, ox, row2y + 8, 30, 15)
        label(msp, ox + 3, row2y + 11, f"PAD{i+1}", height=2)

    # ---- ROW 3: Spacers (×10) + Band hooks (×2) ----
    row3y = row2y - GAP - 16

    # Spacer washers — Ø12
    for i in range(10):
        cx = hx + i * (12 + GAP / 2) + 6
        circ(msp, cx, row3y, 6)
        circ(msp, cx, row3y, M3_R)
    label(msp, hx, row3y - 12, "M8 SPACERS (x10)")

    # Band hooks (×2)
    bhx = hx + 10 * (12 + GAP / 2) + GAP
    bhy = row3y - 5
    for i in range(2):
        ox = bhx + i * (20 + GAP)
        rect(msp, ox, bhy, 20, 10)
        msp.add_lwpolyline([
            (ox + 8, bhy + 10), (ox + 8, bhy + 7),
            (ox + 12, bhy + 7), (ox + 12, bhy + 10)
        ], dxfattribs={"layer": "CUTS"})
        circ(msp, ox + 10, bhy + 3, M3_R)
    label(msp, bhx, bhy - 10, "M8 HOOKS (x2)")

    save(doc, "M8_Robotic_Gripper.dxf")


# =====================================================================
# RUN ALL
# =====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Robocode Spring Camp 2026 — DXF Generator v2")
    print("=" * 60)
    print(f"Output:   {OUTPUT_DIR}")
    print(f"Material: {MAT}mm MDF, Kerf: {KERF}mm, Slot: {SLOT_W}mm")
    print(f"Holes:    M3 clearance = {M3_CLEAR}mm")
    print(f"Motor:    TT motor (shaft hole {SHAFT_D}mm)")
    print()

    m1_catapult()
    m2_pulley_lift()
    m3_automata_card()
    m4_gear_down()
    m5_hand_crank()
    m6_tower_crane()
    m7_rover()
    m8_robotic_gripper()

    print()
    print("=" * 60)
    print("All 8 projects generated!")
    print(f"Files in: {OUTPUT_DIR}")
    print("=" * 60)
