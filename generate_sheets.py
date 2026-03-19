#!/usr/bin/env python3
"""
generate_sheets.py
Packs all laser-cut parts for each project onto 400x600mm MDF sheets
using a row-based nesting algorithm.

Outputs DXF and PNG files to ./sheets/
"""

import math
import os
import ezdxf
from ezdxf.enums import TextEntityAlignment
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Polygon
import numpy as np

# ── Constants ────────────────────────────────────────────────────────────────
SHEET_W = 400  # mm
SHEET_H = 600  # mm
MARGIN = 5     # mm from sheet edge
GAP = 3        # mm between parts

MDF_COLOR = "#00dcde"       # turquoise
BIRCH_COLOR = "#8B6914"     # brown
SHEET_BORDER_COLOR = "#888888"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sheets")

# DXF ACI (AutoCAD Color Index) approximations
ACI_TURQUOISE = 4   # cyan
ACI_BROWN = 30       # brown/dark yellow
ACI_LABEL = 7        # white (shows on dark) / black (shows on light)
ACI_BORDER = 9       # grey


# ── Part definitions ─────────────────────────────────────────────────────────
# Each part: (name, width, height, quantity, shape, material)
# shape: "rect" | "circle" | "egg_cam" | "snail_cam" | "cam_m5"
# For circles, width = diameter, height = diameter
# Tabs add small protrusions -- we add them to the bounding box

def make_parts(name, w, h, qty=1, shape="rect", material="MDF"):
    return [(name, w, h, qty, shape, material)]


PROJECTS = {
    "M1_Catapult": {
        "title": "M1 Catapult",
        "parts": [
            ("Base", 200, 120, 1, "rect", "MDF"),
            ("Side Support", 60+10, 80+3, 2, "rect", "MDF"),      # plus 10x3 tabs
            ("Arm", 280, 20, 1, "rect", "BIRCH"),
            ("Stop", 60+10, 50+3, 1, "rect", "MDF"),              # plus tab
            ("Cup Cross H", 80, 20, 1, "rect", "MDF"),            # cross piece 1
            ("Cup Cross V", 20, 80, 1, "rect", "MDF"),            # cross piece 2
            ("Cup Flap", 40, 20, 4, "rect", "MDF"),               # flaps
        ],
    },
    "M2_Pulley_Lift": {
        "title": "M2 Pulley Lift",
        "parts": [
            ("Base", 180, 120, 1, "rect", "MDF"),
            ("Upright", 50+10, 200+3, 2, "rect", "MDF"),          # plus tabs
            ("Top Beam", 126+10, 30+3, 1, "rect", "MDF"),         # plus tabs
            ("Pulley Wheel", 50, 50, 1, "circle", "MDF"),
            ("Winch Drum", 40, 40, 1, "circle", "MDF"),
            ("Crank", 80, 15, 1, "rect", "MDF"),
            ("Hook Plate", 50, 50, 1, "rect", "MDF"),
        ],
    },
    "M3_Automata_Card": {
        "title": "M3 Automata Card",
        "parts": [
            ("Base", 100, 80, 1, "rect", "MDF"),
            ("Side Frame", 80+10, 120+3, 2, "rect", "MDF"),       # plus tabs
            ("Egg Cam", 50, 36, 1, "egg_cam", "MDF"),
            ("Round Cam", 40, 40, 1, "circle", "MDF"),
            ("Snail Cam", 50, 50, 1, "snail_cam", "MDF"),
            ("Follower", 15, 80, 1, "rect", "MDF"),
            ("Handle", 60, 12, 1, "rect", "MDF"),
        ],
    },
    "M4_Gear_Down_Motor": {
        "title": "M4 Gear-Down Motor",
        "parts": [
            ("Base", 160, 100, 1, "rect", "MDF"),
            ("Axle Support", 50+10, 70+3, 2, "rect", "MDF"),      # plus tabs
            ("Motor Mount", 80+10, 40+3, 1, "rect", "MDF"),       # plus tab
            ("Small Gear", 28, 28, 1, "circle", "MDF"),
            ("Large Gear", 76, 76, 1, "circle", "MDF"),
            ("Drum", 40, 40, 1, "circle", "MDF"),
        ],
    },
    "M5_Hand_Crank_Automata": {
        "title": "M5 Hand-Crank Automata",
        "parts": [
            ("Base", 140, 100, 1, "rect", "MDF"),
            ("Side Frame", 60+10, 140+3, 2, "rect", "MDF"),       # plus tabs
            ("Crank Disc", 50, 50, 1, "circle", "MDF"),
            ("Cam", 44, 32, 1, "egg_cam", "MDF"),
            ("Follower", 12, 90, 1, "rect", "MDF"),
            ("Handle", 70, 14, 1, "rect", "MDF"),
            ("Scene Panel", 100, 80, 1, "rect", "MDF"),
        ],
    },
    "M6_Tower_Crane": {
        "title": "M6 Tower Crane",
        "parts": [
            ("Base", 200, 150, 1, "rect", "MDF"),
            ("Tower Frame", 40, 250, 2, "rect", "MDF"),
            ("Cross Brace", 20+10, 20+3, 2, "rect", "MDF"),       # plus tabs
            ("Jib", 220, 25, 1, "rect", "MDF"),
            ("Pulley", 50, 50, 1, "circle", "MDF"),
            ("Winch Drum", 35, 35, 1, "circle", "MDF"),
            ("Small Gear", 28, 28, 1, "circle", "MDF"),
            ("Large Gear", 52, 52, 1, "circle", "MDF"),
            ("Hook Plate", 40, 40, 1, "rect", "MDF"),
            ("Crank", 70, 14, 1, "rect", "MDF"),
        ],
    },
    "M7_Rover": {
        "title": "M7 Rover",
        "parts": [
            ("Chassis", 150, 80, 1, "rect", "MDF"),
            ("Side Rail", 150+10, 30+3, 2, "rect", "MDF"),        # plus tabs
            ("Wheel", 60, 60, 4, "circle", "MDF"),
            ("Motor Mount", 80+10, 40+3, 1, "rect", "MDF"),       # plus tab
            ("Small Gear", 24, 24, 1, "circle", "MDF"),
            ("Large Gear", 64, 64, 1, "circle", "MDF"),
        ],
    },
    "M8_Robotic_Gripper": {
        "title": "M8 Robotic Gripper",
        "parts": [
            ("Handle Bar", 120, 20, 2, "rect", "MDF"),
            ("Scissor Arm", 100, 15, 4, "rect", "MDF"),
            ("Jaw", 50, 30, 2, "rect", "MDF"),
            ("Jaw Pad", 30, 15, 2, "rect", "MDF"),
            ("Spacer", 12, 12, 10, "circle", "MDF"),
            ("Band Hook", 20, 10, 2, "rect", "MDF"),
        ],
    },
}


# ── Nesting algorithm ────────────────────────────────────────────────────────
def expand_parts(part_list):
    """Expand quantities into individual placement items."""
    expanded = []
    for (name, w, h, qty, shape, material) in part_list:
        for i in range(qty):
            label = f"{name}" if qty == 1 else f"{name} #{i+1}"
            expanded.append({
                "label": label,
                "w": w,
                "h": h,
                "shape": shape,
                "material": material,
            })
    return expanded


def nest_parts(parts, sheet_w, sheet_h, margin, gap):
    """
    Row-based packing: sort by height descending, pack left-to-right.
    Returns list of sheets, each sheet is a list of placed parts with x, y positions.
    """
    usable_w = sheet_w - 2 * margin
    usable_h = sheet_h - 2 * margin

    # Sort by height descending, then width descending
    sorted_parts = sorted(parts, key=lambda p: (-p["h"], -p["w"]))

    sheets = []
    current_sheet = []
    cursor_x = 0
    cursor_y = 0
    row_height = 0

    for part in sorted_parts:
        pw, ph = part["w"], part["h"]

        # Try to place in current row
        if cursor_x + pw <= usable_w and cursor_y + ph <= usable_h:
            part_placed = dict(part)
            part_placed["x"] = margin + cursor_x
            part_placed["y"] = margin + cursor_y
            current_sheet.append(part_placed)
            cursor_x += pw + gap
            row_height = max(row_height, ph)
        else:
            # Try starting a new row on current sheet
            cursor_x = 0
            cursor_y += row_height + gap
            row_height = 0

            if cursor_y + ph <= usable_h and cursor_x + pw <= usable_w:
                part_placed = dict(part)
                part_placed["x"] = margin + cursor_x
                part_placed["y"] = margin + cursor_y
                current_sheet.append(part_placed)
                cursor_x += pw + gap
                row_height = max(row_height, ph)
            else:
                # Start a new sheet
                sheets.append(current_sheet)
                current_sheet = []
                cursor_x = 0
                cursor_y = 0
                row_height = 0

                part_placed = dict(part)
                part_placed["x"] = margin + cursor_x
                part_placed["y"] = margin + cursor_y
                current_sheet.append(part_placed)
                cursor_x += pw + gap
                row_height = max(row_height, ph)

    if current_sheet:
        sheets.append(current_sheet)

    return sheets


# ── DXF drawing helpers ──────────────────────────────────────────────────────

def draw_gear_teeth_dxf(msp, cx, cy, outer_r, num_teeth, color):
    """Draw a simplified gear outline with teeth in DXF."""
    inner_r = outer_r - outer_r * 0.12  # tooth depth ~12% of radius
    tooth_angle = 2 * math.pi / num_teeth
    half_tooth = tooth_angle * 0.35

    points = []
    for i in range(num_teeth):
        angle = i * tooth_angle
        # Root start
        a1 = angle - half_tooth
        points.append((cx + inner_r * math.cos(a1), cy + inner_r * math.sin(a1)))
        # Tip start
        a2 = angle - half_tooth * 0.5
        points.append((cx + outer_r * math.cos(a2), cy + outer_r * math.sin(a2)))
        # Tip end
        a3 = angle + half_tooth * 0.5
        points.append((cx + outer_r * math.cos(a3), cy + outer_r * math.sin(a3)))
        # Root end
        a4 = angle + half_tooth
        points.append((cx + inner_r * math.cos(a4), cy + inner_r * math.sin(a4)))

    # Close the polyline
    points.append(points[0])
    msp.add_lwpolyline(points, dxfattribs={"color": color})


def draw_egg_cam_dxf(msp, cx, cy, w, h, color):
    """Draw an egg/teardrop cam shape as a polyline approximation."""
    points = []
    n = 64
    a_axis = w / 2
    b_axis = h / 2
    for i in range(n):
        t = 2 * math.pi * i / n
        # Egg shape: slightly offset ellipse
        r = a_axis * b_axis / math.sqrt(
            (b_axis * math.cos(t))**2 + (a_axis * math.sin(t))**2
        )
        # Add egg distortion (wider at one end)
        r *= (1 + 0.15 * math.cos(t))
        px = cx + r * math.cos(t)
        py = cy + r * math.sin(t)
        points.append((px, py))
    points.append(points[0])
    msp.add_lwpolyline(points, dxfattribs={"color": color})


def draw_snail_cam_dxf(msp, cx, cy, diameter, color):
    """Draw a snail (spiral) cam shape."""
    points = []
    n = 80
    r_min = diameter * 0.25
    r_max = diameter * 0.5
    for i in range(n):
        t = 2 * math.pi * i / n
        r = r_min + (r_max - r_min) * (t / (2 * math.pi))
        px = cx + r * math.cos(t)
        py = cy + r * math.sin(t)
        points.append((px, py))
    # Close with a straight line back
    points.append(points[0])
    msp.add_lwpolyline(points, dxfattribs={"color": color})


def is_gear(label):
    """Check if a part label indicates a gear."""
    lower = label.lower()
    return "gear" in lower


def num_teeth_for_gear(label, diameter):
    """Estimate tooth count from diameter (approx module 2)."""
    return max(8, int(diameter / 2.5))


def draw_part_dxf(msp, part, color):
    """Draw a single part in DXF."""
    x, y = part["x"], part["y"]
    w, h = part["w"], part["h"]
    shape = part["shape"]
    label = part["label"]

    if shape == "circle":
        cx = x + w / 2
        cy = y + h / 2
        r = w / 2

        if is_gear(label):
            nt = num_teeth_for_gear(label, w)
            draw_gear_teeth_dxf(msp, cx, cy, r, nt, color)
            # Centre hole
            msp.add_circle((cx, cy), 1.5, dxfattribs={"color": color})
        else:
            msp.add_circle((cx, cy), r, dxfattribs={"color": color})
            # Centre hole for wheels/pulleys/drums
            lower = label.lower()
            if any(kw in lower for kw in ["wheel", "pulley", "drum", "disc", "spacer", "crank"]):
                msp.add_circle((cx, cy), 1.5, dxfattribs={"color": color})

    elif shape == "egg_cam":
        cx = x + w / 2
        cy = y + h / 2
        draw_egg_cam_dxf(msp, cx, cy, w, h, color)
        msp.add_circle((cx, cy), 1.5, dxfattribs={"color": color})

    elif shape == "snail_cam":
        cx = x + w / 2
        cy = y + h / 2
        draw_snail_cam_dxf(msp, cx, cy, w, color)
        msp.add_circle((cx, cy), 1.5, dxfattribs={"color": color})

    else:  # rect
        msp.add_lwpolyline(
            [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)],
            dxfattribs={"color": color},
        )

    # Label text
    font_size = min(w, h) * 0.18
    font_size = max(3, min(font_size, 8))
    msp.add_text(
        label,
        height=font_size,
        dxfattribs={"color": ACI_LABEL},
    ).set_placement((x + w / 2, y + h / 2), align=TextEntityAlignment.MIDDLE_CENTER)


def create_dxf(project_key, title, sheets_data):
    """Create DXF file(s) for a project."""
    paths = []
    for sheet_idx, sheet_parts in enumerate(sheets_data):
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()

        # Set proper extents so viewers can render the file
        doc.header['$EXTMIN'] = (0, 0, 0)
        doc.header['$EXTMAX'] = (SHEET_W, SHEET_H, 0)

        # Register linetypes
        if 'DASHED' not in doc.linetypes:
            doc.linetypes.add("DASHED", pattern=[0.6, 0.5, -0.1])
        if 'DASHDOT' not in doc.linetypes:
            doc.linetypes.add("DASHDOT", pattern=[1.0, 0.5, -0.1, 0.0, -0.1])

        # Sheet boundary (dashed)
        msp.add_lwpolyline(
            [(0, 0), (SHEET_W, 0), (SHEET_W, SHEET_H), (0, SHEET_H), (0, 0)],
            dxfattribs={"color": ACI_BORDER, "linetype": "DASHED"},
        )

        # Usable area (margin)
        msp.add_lwpolyline(
            [
                (MARGIN, MARGIN),
                (SHEET_W - MARGIN, MARGIN),
                (SHEET_W - MARGIN, SHEET_H - MARGIN),
                (MARGIN, SHEET_H - MARGIN),
                (MARGIN, MARGIN),
            ],
            dxfattribs={"color": ACI_BORDER, "linetype": "DASHDOT"},
        )

        # Draw parts
        for part in sheet_parts:
            color = ACI_BROWN if part["material"] == "BIRCH" else ACI_TURQUOISE
            draw_part_dxf(msp, part, color)

        # Title block
        sheet_label = f"{title} - Sheet {sheet_idx + 1}/{len(sheets_data)}"
        msp.add_text(
            sheet_label,
            height=8,
            dxfattribs={"color": ACI_LABEL},
        ).set_placement((SHEET_W / 2, SHEET_H - 2), align=TextEntityAlignment.TOP_CENTER)

        # Material: 3mm MDF / 3mm Birch Ply
        msp.add_text(
            "Material: 3mm MDF (turquoise) / 3mm Birch Ply (brown)",
            height=4,
            dxfattribs={"color": ACI_LABEL},
        ).set_placement((SHEET_W / 2, SHEET_H - 12), align=TextEntityAlignment.TOP_CENTER)

        sheet_num = sheet_idx + 1
        fname = f"{project_key}_sheet{sheet_num}.dxf"
        fpath = os.path.join(OUTPUT_DIR, fname)
        doc.saveas(fpath)
        paths.append(fpath)
        print(f"  DXF: {fpath}")

    return paths


# ── PNG drawing helpers ──────────────────────────────────────────────────────

def draw_gear_teeth_png(ax, cx, cy, outer_r, num_teeth, color, lw=0.8):
    """Draw gear outline on matplotlib axes."""
    inner_r = outer_r - outer_r * 0.12
    tooth_angle = 2 * math.pi / num_teeth
    half_tooth = tooth_angle * 0.35

    xs, ys = [], []
    for i in range(num_teeth):
        angle = i * tooth_angle
        a1 = angle - half_tooth
        xs.append(cx + inner_r * math.cos(a1))
        ys.append(cy + inner_r * math.sin(a1))
        a2 = angle - half_tooth * 0.5
        xs.append(cx + outer_r * math.cos(a2))
        ys.append(cy + outer_r * math.sin(a2))
        a3 = angle + half_tooth * 0.5
        xs.append(cx + outer_r * math.cos(a3))
        ys.append(cy + outer_r * math.sin(a3))
        a4 = angle + half_tooth
        xs.append(cx + inner_r * math.cos(a4))
        ys.append(cy + inner_r * math.sin(a4))

    xs.append(xs[0])
    ys.append(ys[0])
    ax.plot(xs, ys, color=color, linewidth=lw)


def draw_egg_cam_png(ax, cx, cy, w, h, color, lw=0.8):
    """Draw egg cam on matplotlib axes."""
    n = 64
    a_axis = w / 2
    b_axis = h / 2
    xs, ys = [], []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        r = a_axis * b_axis / math.sqrt(
            (b_axis * math.cos(t))**2 + (a_axis * math.sin(t))**2
        )
        r *= (1 + 0.15 * math.cos(t))
        xs.append(cx + r * math.cos(t))
        ys.append(cy + r * math.sin(t))
    ax.plot(xs, ys, color=color, linewidth=lw)


def draw_snail_cam_png(ax, cx, cy, diameter, color, lw=0.8):
    """Draw snail cam on matplotlib axes."""
    n = 80
    r_min = diameter * 0.25
    r_max = diameter * 0.5
    xs, ys = [], []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        r = r_min + (r_max - r_min) * (min(t, 2 * math.pi) / (2 * math.pi))
        xs.append(cx + r * math.cos(t))
        ys.append(cy + r * math.sin(t))
    # Close
    xs.append(xs[0])
    ys.append(ys[0])
    ax.plot(xs, ys, color=color, linewidth=lw)


def draw_part_png(ax, part, color):
    """Draw a single part on matplotlib axes."""
    x, y = part["x"], part["y"]
    w, h = part["w"], part["h"]
    shape = part["shape"]
    label = part["label"]
    lw = 1.0

    fill_alpha = 0.10

    if shape == "circle":
        cx = x + w / 2
        cy = y + h / 2
        r = w / 2

        if is_gear(label):
            nt = num_teeth_for_gear(label, w)
            draw_gear_teeth_png(ax, cx, cy, r, nt, color, lw)
            circle_fill = plt.Circle((cx, cy), r * 0.88, facecolor=color,
                                     alpha=fill_alpha, edgecolor="none")
            ax.add_patch(circle_fill)
            centre = plt.Circle((cx, cy), 1.5, facecolor="none",
                                edgecolor=color, linewidth=0.5)
            ax.add_patch(centre)
        else:
            circle_outline = plt.Circle((cx, cy), r, facecolor=color,
                                        alpha=fill_alpha, edgecolor=color, linewidth=lw)
            ax.add_patch(circle_outline)
            lower = label.lower()
            if any(kw in lower for kw in ["wheel", "pulley", "drum", "disc", "spacer", "crank"]):
                centre = plt.Circle((cx, cy), 1.5, facecolor="none",
                                    edgecolor=color, linewidth=0.5)
                ax.add_patch(centre)

    elif shape == "egg_cam":
        cx = x + w / 2
        cy = y + h / 2
        draw_egg_cam_png(ax, cx, cy, w, h, color, lw)
        centre = plt.Circle((cx, cy), 1.5, facecolor="none",
                            edgecolor=color, linewidth=0.5)
        ax.add_patch(centre)

    elif shape == "snail_cam":
        cx = x + w / 2
        cy = y + h / 2
        draw_snail_cam_png(ax, cx, cy, w, color, lw)
        centre = plt.Circle((cx, cy), 1.5, facecolor="none",
                            edgecolor=color, linewidth=0.5)
        ax.add_patch(centre)

    else:  # rect
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="square,pad=0",
            facecolor=color, alpha=fill_alpha,
            edgecolor=color, linewidth=lw,
        )
        ax.add_patch(rect)

    # Label
    font_size = min(w, h) * 0.15
    font_size = max(3, min(font_size, 7))
    ax.text(
        x + w / 2, y + h / 2, label,
        ha="center", va="center",
        fontsize=font_size, color="#333333",
        fontweight="medium",
    )


def create_png(project_key, title, sheets_data):
    """Create PNG preview(s) for a project."""
    paths = []
    for sheet_idx, sheet_parts in enumerate(sheets_data):
        fig, ax = plt.subplots(1, 1, figsize=(8, 12), dpi=150)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        ax.set_xlim(-10, SHEET_W + 10)
        ax.set_ylim(-20, SHEET_H + 20)
        ax.set_aspect("equal")
        ax.axis("off")

        # Sheet boundary (dashed)
        border = mpatches.FancyBboxPatch(
            (0, 0), SHEET_W, SHEET_H,
            boxstyle="square,pad=0",
            facecolor="#fafafa", edgecolor=SHEET_BORDER_COLOR,
            linewidth=1.2, linestyle="--",
        )
        ax.add_patch(border)

        # Margin area (light dotted)
        margin_rect = mpatches.FancyBboxPatch(
            (MARGIN, MARGIN), SHEET_W - 2 * MARGIN, SHEET_H - 2 * MARGIN,
            boxstyle="square,pad=0",
            facecolor="none", edgecolor="#cccccc",
            linewidth=0.5, linestyle=":",
        )
        ax.add_patch(margin_rect)

        # Draw parts
        for part in sheet_parts:
            color = BIRCH_COLOR if part["material"] == "BIRCH" else MDF_COLOR
            draw_part_png(ax, part, color)

        # Title
        sheet_label = f"{title} -- Sheet {sheet_idx + 1}/{len(sheets_data)}"
        ax.text(
            SHEET_W / 2, SHEET_H + 8, sheet_label,
            ha="center", va="bottom",
            fontsize=11, fontweight="bold", color="#222222",
        )

        # Dimensions label
        ax.text(
            SHEET_W / 2, -8,
            f"400 x 600 mm MDF sheet | 3 mm thick | 5 mm margin | 3 mm gap",
            ha="center", va="top",
            fontsize=6, color="#888888",
        )

        # Legend
        legend_y = -15
        ax.plot([10, 25], [legend_y, legend_y], color=MDF_COLOR, linewidth=2)
        ax.text(28, legend_y, "MDF", fontsize=5, va="center", color="#555555")
        ax.plot([60, 75], [legend_y, legend_y], color=BIRCH_COLOR, linewidth=2)
        ax.text(78, legend_y, "Birch Ply", fontsize=5, va="center", color="#555555")

        plt.tight_layout()

        sheet_num = sheet_idx + 1
        fname = f"{project_key}_sheet{sheet_num}.png"
        fpath = os.path.join(OUTPUT_DIR, fname)
        fig.savefig(fpath, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        paths.append(fpath)
        print(f"  PNG: {fpath}")

    return paths


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Sheet size: {SHEET_W} x {SHEET_H} mm")
    print(f"Margin: {MARGIN} mm, Gap: {GAP} mm")
    print("=" * 60)

    for project_key, project in PROJECTS.items():
        title = project["title"]
        parts_def = project["parts"]

        print(f"\n{title}")
        print("-" * 40)

        # Expand quantities
        parts = expand_parts(parts_def)
        total_area = sum(p["w"] * p["h"] for p in parts)
        sheet_area = (SHEET_W - 2 * MARGIN) * (SHEET_H - 2 * MARGIN)
        print(f"  Parts: {len(parts)} pieces, total area: {total_area:.0f} mm2")
        print(f"  Sheet usable area: {sheet_area:.0f} mm2 ({total_area/sheet_area*100:.1f}% fill)")

        # Nest
        sheets_data = nest_parts(parts, SHEET_W, SHEET_H, MARGIN, GAP)
        print(f"  Sheets needed: {len(sheets_data)}")

        for i, sd in enumerate(sheets_data):
            print(f"    Sheet {i+1}: {len(sd)} parts")

        # Generate outputs
        create_dxf(project_key, title, sheets_data)
        create_png(project_key, title, sheets_data)

    print("\n" + "=" * 60)
    print("All sheet layouts generated successfully.")
    print(f"Files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
