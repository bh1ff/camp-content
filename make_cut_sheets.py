#!/usr/bin/env python3
"""
make_cut_sheets.py — Mass Production Sheets
Packs maximum duplicate copies of each project onto 400×600mm MDF sheets.
Tries both orientations (normal + 90° rotated) to maximize kits per sheet.
All internal features (holes, slots, tabs, gear teeth) are preserved.
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
GAP = 5  # gap between copies

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "dxf_output")
OUTPUT_DIR = os.path.join(BASE_DIR, "sheets")
os.makedirs(OUTPUT_DIR, exist_ok=True)


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


def calc_grid(w, h):
    """How many copies fit in a grid on the usable sheet area."""
    uw = SHEET_W - 2 * MARGIN
    uh = SHEET_H - 2 * MARGIN
    cols = 1
    while (cols + 1) * w + cols * GAP <= uw:
        cols += 1
    rows = 1
    while (rows + 1) * h + rows * GAP <= uh:
        rows += 1
    return cols, rows, cols * rows


def copy_entities(src_msp, dst_msp, dx, dy, rotate=False, rot_cx=0, rot_cy=0):
    """Copy entities with translation. If rotate=True, rotate 90° CCW first."""
    count = 0
    for e in src_msp:
        try:
            etype = e.dxftype()
            attribs = {}
            if e.dxf.hasattr('layer'):
                attribs['layer'] = e.dxf.layer
            if e.dxf.hasattr('color'):
                attribs['color'] = e.dxf.color

            def tx(x, y):
                if rotate:
                    # Rotate 90° CCW around (rot_cx, rot_cy), then translate
                    rx, ry = -(y - rot_cy), (x - rot_cx)
                    return (rx + dx, ry + dy)
                return (x + dx, y + dy)

            if etype == 'LWPOLYLINE':
                pts = [tx(p[0], p[1]) for p in e.get_points(format='xy')]
                dst_msp.add_lwpolyline(pts, close=e.close, dxfattribs=attribs)
                count += 1
            elif etype == 'CIRCLE':
                nc = tx(e.dxf.center.x, e.dxf.center.y)
                dst_msp.add_circle(nc, e.dxf.radius, dxfattribs=attribs)
                count += 1
            elif etype == 'LINE':
                ns = tx(e.dxf.start.x, e.dxf.start.y)
                ne = tx(e.dxf.end.x, e.dxf.end.y)
                dst_msp.add_line(ns, ne, dxfattribs=attribs)
                count += 1
            elif etype == 'TEXT':
                if e.dxf.hasattr('height'):
                    attribs['height'] = e.dxf.height
                np = tx(e.dxf.insert.x, e.dxf.insert.y)
                t = dst_msp.add_text(e.dxf.text, dxfattribs=attribs)
                t.set_placement(np)
                count += 1
        except Exception:
            pass
    return count


def make_mass_sheet(src_path, proj_name):
    """Create a mass production sheet with maximum copies of one project."""
    src = ezdxf.readfile(src_path)
    src_msp = src.modelspace()
    min_x, min_y, max_x, max_y = get_bounds(src_msp)
    w = max_x - min_x
    h = max_y - min_y

    # Try normal orientation
    cols_n, rows_n, count_n = calc_grid(w, h)
    # Try rotated 90° (swap w and h)
    cols_r, rows_r, count_r = calc_grid(h, w)

    use_rotate = count_r > count_n
    if use_rotate:
        cols, rows, count = cols_r, rows_r, count_r
        cell_w, cell_h = h, w  # after rotation, width=old_height, height=old_width
    else:
        cols, rows, count = cols_n, rows_n, count_n
        cell_w, cell_h = w, h

    print(f"  {proj_name}: {w:.0f}×{h:.0f}mm → {cols}×{rows} grid = {count} copies/sheet"
          f"{'  (rotated 90°)' if use_rotate else ''}")

    # Create target document
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

    # Calculate starting offset to center the grid
    grid_w = cols * cell_w + (cols - 1) * GAP
    grid_h = rows * cell_h + (rows - 1) * GAP
    start_x = MARGIN + (SHEET_W - 2 * MARGIN - grid_w) / 2
    start_y = MARGIN + (SHEET_H - 2 * MARGIN - grid_h) / 2

    total_entities = 0
    for row in range(rows):
        for col in range(cols):
            # Position for this copy
            cx = start_x + col * (cell_w + GAP)
            cy = start_y + row * (cell_h + GAP)

            if use_rotate:
                # Rotate 90° CCW: the source min corner maps to a new position
                # After rotation around (min_x + w/2, min_y + h/2) then translate
                # Simpler: normalize source to origin, rotate, then place
                # Rotation 90° CCW of point (x-min_x, y-min_y) → (-(y-min_y), (x-min_x))
                # This maps (0,0)→(0,0), (w,0)→(0,w), (0,h)→(-h,0), (w,h)→(-h,w)
                # Bounding box after: (-h,0) to (0,w) → shift by +h: (0,0) to (h,w)
                # So cell_w = h, cell_h = w (confirmed)
                dx = cx + h  # shift to put left edge at cx (after rotation, min_x = -h + origin)
                dy = cy
                n = copy_entities(src_msp, msp, dx, dy,
                                  rotate=True, rot_cx=min_x, rot_cy=min_y)
            else:
                dx = cx - min_x
                dy = cy - min_y
                n = copy_entities(src_msp, msp, dx, dy)

            total_entities += n

    doc.header['$EXTMIN'] = (0, 0, 0)
    doc.header['$EXTMAX'] = (SHEET_W, SHEET_H, 0)

    dxf_path = os.path.join(OUTPUT_DIR, f"{proj_name}_x{count}.dxf")
    doc.saveas(dxf_path)
    print(f"    DXF: {dxf_path} ({total_entities} entities)")

    return dxf_path, count, cols, rows, use_rotate


def make_png(dxf_path, png_path, title):
    """Render sheet DXF to PNG."""
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    fig, ax = plt.subplots(figsize=(8, 12), dpi=150)
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp)

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
    print("Mass Production Cut Sheets")
    print("Maximum duplicate kits per 400×600mm MDF sheet")
    print("=" * 60)
    print(f"Sheet: {SHEET_W}×{SHEET_H}mm, {MARGIN}mm margin, {GAP}mm gap")
    print()

    results = []
    for src_name in sorted(os.listdir(INPUT_DIR)):
        if not src_name.endswith('.dxf'):
            continue
        proj = src_name.replace('.dxf', '')
        src_path = os.path.join(INPUT_DIR, src_name)

        dxf_path, count, cols, rows, rotated = make_mass_sheet(src_path, proj)
        png_path = dxf_path.replace('.dxf', '.png')
        title = f"{proj.replace('_', ' ')} — {count} kits per sheet ({cols}×{rows})"
        make_png(dxf_path, png_path, title)
        results.append((proj, count, cols, rows, rotated))

    # Also keep individual single-copy sheets for per-project use
    print("\nSingle-copy project sheets:")
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

        doc = ezdxf.new("R2010")
        doc.layers.add("CUTS", color=7)
        doc.layers.add("ENGRAVE", color=1)
        doc.layers.add("GUIDE", color=3)
        doc.layers.add("SHEET", color=8)
        msp = doc.modelspace()
        msp.add_lwpolyline(
            [(0, 0), (SHEET_W, 0), (SHEET_W, SHEET_H), (0, SHEET_H)],
            close=True, dxfattribs={"layer": "SHEET", "color": 8})
        dx = MARGIN - min_x + max(0, (SHEET_W - 2 * MARGIN - w) / 2)
        dy = MARGIN - min_y + max(0, (SHEET_H - 2 * MARGIN - h) / 2)
        copy_entities(src_msp, msp, dx, dy)
        doc.header['$EXTMIN'] = (0, 0, 0)
        doc.header['$EXTMAX'] = (SHEET_W, SHEET_H, 0)
        dxf_out = os.path.join(OUTPUT_DIR, f"{proj}_sheet1.dxf")
        doc.saveas(dxf_out)
        png_out = dxf_out.replace('.dxf', '.png')
        make_png(dxf_out, png_out, f"{proj.replace('_', ' ')}")
        print(f"  {proj} → {dxf_out}")

    print("\n" + "=" * 60)
    print("SUMMARY — Kits per sheet:")
    print("-" * 40)
    for proj, count, cols, rows, rotated in results:
        r = " (rotated)" if rotated else ""
        print(f"  {proj:35s}  {count} kits  ({cols}×{rows}){r}")
    print("=" * 60)


if __name__ == "__main__":
    main()
