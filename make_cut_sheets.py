#!/usr/bin/env python3
"""
make_cut_sheets.py
Packs all 8 project DXFs (with full detail: holes, slots, tabs) onto
the minimum number of 400×600mm MDF sheets for bulk laser cutting.

Projects are grouped to maximize sheet usage:
  Sheet 1: M6 Tower Crane (315×377) + M4 Gear-Down Motor (276×176)
  Sheet 2: M1 Catapult (348×249) + M8 Robotic Gripper (228×166)
  Sheet 3: M2 Pulley Lift (296×276) + M3 Automata Card (276×221)
  Sheet 4: M5 Hand-Crank Automata (276×264) + M7 Rover (308×203)

4 sheets instead of 8 = 50% material saving.
"""

import ezdxf
import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

SHEET_W = 400
SHEET_H = 600
MARGIN = 5

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "dxf_output")
OUTPUT_DIR = os.path.join(BASE_DIR, "sheets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sheet groupings: [(project_name, stack_position), ...]
# Projects are stacked vertically on each sheet with a gap between them
SHEETS = [
    {
        "name": "Sheet1_M6_M4",
        "label": "Sheet 1 — M6 Tower Crane + M4 Gear-Down Motor",
        "projects": ["M4_Gear_Down_Motor", "M6_Tower_Crane"],  # bottom to top
    },
    {
        "name": "Sheet2_M1_M8",
        "label": "Sheet 2 — M1 Catapult + M8 Robotic Gripper",
        "projects": ["M8_Robotic_Gripper", "M1_Catapult"],
    },
    {
        "name": "Sheet3_M2_M3",
        "label": "Sheet 3 — M2 Pulley Lift + M3 Automata Card",
        "projects": ["M3_Automata_Card", "M2_Pulley_Lift"],
    },
    {
        "name": "Sheet4_M5_M7",
        "label": "Sheet 4 — M5 Hand-Crank Automata + M7 Rover",
        "projects": ["M7_Rover_Ramp", "M5_Hand_Crank_Automata"],
    },
]

GAP = 8  # gap between projects on same sheet


def get_bounds(msp):
    """Calculate bounding box of all entities in modelspace."""
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    for e in msp:
        try:
            etype = e.dxftype()
            if etype == 'LWPOLYLINE':
                for pt in e.get_points():
                    min_x, min_y = min(min_x, pt[0]), min(min_y, pt[1])
                    max_x, max_y = max(max_x, pt[0]), max(max_y, pt[1])
            elif etype == 'CIRCLE':
                cx, cy, r = e.dxf.center.x, e.dxf.center.y, e.dxf.radius
                min_x, min_y = min(min_x, cx - r), min(min_y, cy - r)
                max_x, max_y = max(max_x, cx + r), max(max_y, cy + r)
            elif etype == 'LINE':
                for p in [e.dxf.start, e.dxf.end]:
                    min_x, min_y = min(min_x, p.x), min(min_y, p.y)
                    max_x, max_y = max(max_x, p.x), max(max_y, p.y)
            elif etype == 'TEXT':
                p = e.dxf.insert
                min_x, min_y = min(min_x, p.x), min(min_y, p.y)
                max_x, max_y = max(max_x, p.x), max(max_y, p.y)
        except Exception:
            pass

    return min_x, min_y, max_x, max_y


def copy_entities(src_msp, dst_msp, dx, dy):
    """Copy all entities from src to dst with (dx, dy) translation."""
    count = 0
    for e in src_msp:
        try:
            etype = e.dxftype()
            attribs = {}
            if e.dxf.hasattr('layer'):
                attribs['layer'] = e.dxf.layer
            if e.dxf.hasattr('color'):
                attribs['color'] = e.dxf.color

            if etype == 'LWPOLYLINE':
                pts = [(p[0] + dx, p[1] + dy) for p in e.get_points(format='xy')]
                dst_msp.add_lwpolyline(pts, close=e.close, dxfattribs=attribs)
                count += 1
            elif etype == 'CIRCLE':
                dst_msp.add_circle(
                    (e.dxf.center.x + dx, e.dxf.center.y + dy),
                    e.dxf.radius, dxfattribs=attribs)
                count += 1
            elif etype == 'LINE':
                dst_msp.add_line(
                    (e.dxf.start.x + dx, e.dxf.start.y + dy),
                    (e.dxf.end.x + dx, e.dxf.end.y + dy),
                    dxfattribs=attribs)
                count += 1
            elif etype == 'TEXT':
                if e.dxf.hasattr('height'):
                    attribs['height'] = e.dxf.height
                t = dst_msp.add_text(e.dxf.text, dxfattribs=attribs)
                t.set_placement((e.dxf.insert.x + dx, e.dxf.insert.y + dy))
                count += 1
        except Exception:
            pass
    return count


def make_combined_sheet(sheet_def):
    """Create a combined sheet DXF with multiple projects."""
    doc = ezdxf.new("R2010")

    # Add standard layers
    doc.layers.add("CUTS", color=7)
    doc.layers.add("ENGRAVE", color=1)
    doc.layers.add("GUIDE", color=3)
    doc.layers.add("SHEET", color=8)

    msp = doc.modelspace()

    # Add sheet boundary
    msp.add_lwpolyline(
        [(0, 0), (SHEET_W, 0), (SHEET_W, SHEET_H), (0, SHEET_H)],
        close=True, dxfattribs={"layer": "SHEET", "color": 8})

    cursor_y = MARGIN  # current Y position for stacking
    total_entities = 0

    for proj_name in sheet_def["projects"]:
        src_path = os.path.join(INPUT_DIR, f"{proj_name}.dxf")
        if not os.path.exists(src_path):
            print(f"  WARNING: {src_path} not found, skipping")
            continue

        src = ezdxf.readfile(src_path)
        src_msp = src.modelspace()
        min_x, min_y, max_x, max_y = get_bounds(src_msp)
        w, h = max_x - min_x, max_y - min_y

        # Translation: align left edge to MARGIN, stack at cursor_y
        dx = MARGIN - min_x
        dy = cursor_y - min_y

        # Center horizontally if narrower than sheet
        extra_x = SHEET_W - 2 * MARGIN - w
        if extra_x > 0:
            dx += extra_x / 2

        n = copy_entities(src_msp, msp, dx, dy)
        total_entities += n
        print(f"    {proj_name}: {w:.0f}×{h:.0f}mm, {n} entities, Y={cursor_y:.0f}–{cursor_y+h:.0f}")

        cursor_y += h + GAP

    # Set extents
    doc.header['$EXTMIN'] = (0, 0, 0)
    doc.header['$EXTMAX'] = (SHEET_W, SHEET_H, 0)

    # Save DXF
    dxf_path = os.path.join(OUTPUT_DIR, f"{sheet_def['name']}.dxf")
    doc.saveas(dxf_path)

    # Verify fit
    used_h = cursor_y - GAP
    fill_pct = (used_h / SHEET_H) * 100
    fits = "OK" if used_h <= SHEET_H else "OVERFLOW!"
    print(f"    Total height: {used_h:.0f}/{SHEET_H}mm ({fill_pct:.0f}%) — {fits}")
    print(f"    DXF: {dxf_path} ({total_entities} entities)")

    return dxf_path


def make_png(dxf_path, png_path, title):
    """Render a sheet DXF to PNG."""
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    fig, ax = plt.subplots(figsize=(8, 12), dpi=150)
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp)

    ax.set_xlim(-10, SHEET_W + 10)
    ax.set_ylim(-10, SHEET_H + 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, color='white', fontsize=10, fontweight='bold', pad=10)

    plt.tight_layout()
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close(fig)
    print(f"    PNG: {png_path}")
    return png_path


def main():
    print("=" * 60)
    print("Combined Laser Cut Sheets — All 8 Projects on 4 Sheets")
    print("=" * 60)
    print(f"Sheet: {SHEET_W} × {SHEET_H}mm, {MARGIN}mm margin, {GAP}mm gap")
    print(f"Output: {OUTPUT_DIR}")
    print()

    sheet_files = []
    for i, sheet_def in enumerate(SHEETS):
        print(f"\n{sheet_def['label']}")
        print("-" * 50)

        dxf_path = make_combined_sheet(sheet_def)
        png_path = dxf_path.replace('.dxf', '.png')
        make_png(dxf_path, png_path, sheet_def['label'])
        sheet_files.append((dxf_path, png_path))

    # Also generate individual project sheets (for per-project downloads)
    print("\n\nIndividual project sheets (for per-project use):")
    print("-" * 50)
    for src_name in sorted(os.listdir(INPUT_DIR)):
        if not src_name.endswith('.dxf'):
            continue
        proj = src_name.replace('.dxf', '')
        src_path = os.path.join(INPUT_DIR, src_name)

        src = ezdxf.readfile(src_path)
        src_msp = src.modelspace()
        min_x, min_y, max_x, max_y = get_bounds(src_msp)
        w, h = max_x - min_x, max_y - min_y

        # Create sheet doc
        doc = ezdxf.new("R2010")
        doc.layers.add("CUTS", color=7)
        doc.layers.add("ENGRAVE", color=1)
        doc.layers.add("GUIDE", color=3)
        doc.layers.add("SHEET", color=8)
        msp = doc.modelspace()

        # Sheet boundary
        msp.add_lwpolyline(
            [(0, 0), (SHEET_W, 0), (SHEET_W, SHEET_H), (0, SHEET_H)],
            close=True, dxfattribs={"layer": "SHEET", "color": 8})

        # Translate to center on sheet
        dx = MARGIN - min_x + max(0, (SHEET_W - 2*MARGIN - w) / 2)
        dy = MARGIN - min_y + max(0, (SHEET_H - 2*MARGIN - h) / 2)
        n = copy_entities(src_msp, msp, dx, dy)

        doc.header['$EXTMIN'] = (0, 0, 0)
        doc.header['$EXTMAX'] = (SHEET_W, SHEET_H, 0)

        dxf_out = os.path.join(OUTPUT_DIR, f"{proj}_sheet1.dxf")
        doc.saveas(dxf_out)

        png_out = os.path.join(OUTPUT_DIR, f"{proj}_sheet1.png")
        make_png(dxf_out, png_out, f"{proj.replace('_', ' ')} — Cut Sheet")

        print(f"  {proj}: {w:.0f}×{h:.0f}mm → {dxf_out}")

    print("\n" + "=" * 60)
    print("Done! 4 combined sheets + 8 individual sheets generated.")
    print(f"Files in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
