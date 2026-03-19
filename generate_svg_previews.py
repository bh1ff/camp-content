#!/usr/bin/env python3
"""
Generate SVG previews of all DXF files for easy browser viewing.
Also generates a combined index.html with all projects side by side.
"""

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import glob

DXF_DIR = os.path.join(os.path.dirname(__file__), "dxf_output")
SVG_DIR = os.path.join(os.path.dirname(__file__), "svg_preview")
os.makedirs(SVG_DIR, exist_ok=True)

dxf_files = sorted(glob.glob(os.path.join(DXF_DIR, "*.dxf")))

svg_entries = []

for dxf_path in dxf_files:
    name = os.path.splitext(os.path.basename(dxf_path))[0]
    svg_path = os.path.join(SVG_DIR, f"{name}.svg")
    png_path = os.path.join(SVG_DIR, f"{name}.png")

    print(f"Rendering {name}...")

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    fig = plt.figure(dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp)

    ax.set_aspect("equal")
    ax.set_facecolor("#1a1a2e")

    # Save SVG
    fig.savefig(svg_path, format="svg", bbox_inches="tight",
                facecolor="#1a1a2e", edgecolor="none", dpi=150)
    # Save PNG too
    fig.savefig(png_path, format="png", bbox_inches="tight",
                facecolor="#1a1a2e", edgecolor="none", dpi=150)
    plt.close(fig)
    print(f"  ✓ {svg_path}")
    svg_entries.append((name, f"{name}.svg", f"{name}.png"))

# Generate index.html
html_path = os.path.join(SVG_DIR, "index.html")
with open(html_path, "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
<title>Robocode Spring Camp 2026 — Laser Cut Kit Preview</title>
<style>
  body { font-family: -apple-system, sans-serif; background: #0d1117; color: #e6edf3; margin: 0; padding: 20px; }
  h1 { text-align: center; color: #58a6ff; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; max-width: 1400px; margin: 0 auto; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; overflow: hidden; }
  .card h2 { margin: 0; padding: 12px 16px; background: #21262d; color: #58a6ff; font-size: 16px; }
  .card img { width: 100%; display: block; }
  .info { padding: 8px 16px; font-size: 13px; color: #8b949e; }
</style>
</head>
<body>
<h1>Robocode Spring Camp 2026 — Laser Cut Parts</h1>
<p style="text-align:center;color:#8b949e">3mm MDF | 400×600mm sheets | Kerf: 0.1mm | Tab: 10mm | Dowel: Ø4mm</p>
<div class="grid">
""")
    project_names = {
        "M1_Catapult": "M1 Catapult — Levers",
        "M2_Pulley_Lift": "M2 Pulley Lift — Pulleys",
        "M3_Automata_Card": "M3 Automata Card — Cams",
        "M4_Gear_Down_Motor": "M4 Gear-Down Motor — Gears",
        "M5_Hand_Crank_Automata": "M5 Hand-Crank Automata — Crank+Cam",
        "M6_Tower_Crane": "M6 Tower Crane — Pulleys+Gears",
        "M7_Rover_Ramp": "M7 Rover Ramp — Wheels+Gears+Motor",
        "M8_Robotic_Gripper": "M8 Robotic Gripper — Linkages",
    }
    for name, svg_file, png_file in svg_entries:
        title = project_names.get(name, name)
        f.write(f"""  <div class="card">
    <h2>{title}</h2>
    <img src="{png_file}" alt="{name}">
    <div class="info">Click to open: <a href="{svg_file}" style="color:#58a6ff">{svg_file}</a></div>
  </div>
""")
    f.write("</div>\n</body>\n</html>\n")

print(f"\n✓ Index page: {html_path}")
print("  Open in browser to see all projects!")
