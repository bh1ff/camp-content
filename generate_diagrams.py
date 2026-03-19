#!/usr/bin/env python3
"""
Generate educational mechanism diagrams for 8 mechanical engineering projects.
Kids workshop style: clean, minimal, 2D, with clear labels and annotations.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Arc, Polygon, Circle, Rectangle, Wedge
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

# ── Style constants ──────────────────────────────────────────────────────────
BG_COLOR = '#FFFFFF'
ACCENT = '#00dcde'       # turquoise
DARK = '#003439'         # dark teal
ARROW_COLOR = '#ff9752'  # orange
LIGHT_BG = '#EDFFFE'     # light annotation bg
GREY = '#9CA3AF'         # structural grey
LIGHT_GREY = '#D1D5DB'

DPI = 200
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diagrams')
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Nunito', 'Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.facecolor': BG_COLOR,
    'figure.facecolor': BG_COLOR,
    'text.color': DARK,
})


def save_fig(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor=BG_COLOR,
                edgecolor='none', transparent=False)
    plt.close(fig)
    print(f"  Saved: {path}")


def draw_arrow(ax, start, end, color=ARROW_COLOR, lw=2, style='->', head_width=0.15,
               mutation_scale=18, zorder=10):
    """Draw a clean arrow between two points."""
    arrow = FancyArrowPatch(start, end, arrowstyle=style,
                            color=color, lw=lw,
                            mutation_scale=mutation_scale, zorder=zorder)
    ax.add_patch(arrow)
    return arrow


def label_box(ax, x, y, text, fontsize=9, color=DARK, bg=LIGHT_BG, zorder=12):
    """Add a label with a subtle background box."""
    ax.text(x, y, text, fontsize=fontsize, color=color, ha='center', va='center',
            zorder=zorder, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=bg, edgecolor=ACCENT,
                      linewidth=0.8, alpha=0.95))


# ═══════════════════════════════════════════════════════════════════════════════
# M1 — CATAPULT / LEVER PRINCIPLE
# ═══════════════════════════════════════════════════════════════════════════════
def draw_m1_catapult():
    print("M1 Catapult — Lever Principle")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(-1, 12)
    ax.set_ylim(-1.5, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.suptitle('M1 Catapult — Class 1 Lever Principle', fontsize=14,
                 fontweight='bold', color=DARK, y=0.97)

    # Base plate
    base = mpatches.FancyBboxPatch((0.5, -0.3), 10, 0.4, boxstyle='round,pad=0.05',
                                    facecolor=GREY, edgecolor=DARK, linewidth=1.2)
    ax.add_patch(base)
    ax.text(5.5, -0.1, 'Base Plate', fontsize=7, ha='center', va='center', color='white', fontweight='bold')

    # Fulcrum — triangle
    fulcrum_x = 3.3  # 80mm short side : 200mm long side ≈ ratio 2.86:7.14 on 10-unit arm
    tri = Polygon([[fulcrum_x - 0.5, 0.1], [fulcrum_x + 0.5, 0.1], [fulcrum_x, 0.9]],
                  closed=True, facecolor=ACCENT, edgecolor=DARK, linewidth=1.5, zorder=5)
    ax.add_patch(tri)
    label_box(ax, fulcrum_x, -0.9, 'Fulcrum')

    # Lever arm — angled slightly showing loaded position
    arm_left = 1.0
    arm_right = 10.0
    pivot_y = 0.9
    # Short arm from left to fulcrum, long arm from fulcrum to right
    # Slight tilt: short end down, long end up (resting)
    tilt = 0.07  # radians
    lx = fulcrum_x - (fulcrum_x - arm_left)
    rx = fulcrum_x + (arm_right - fulcrum_x)
    ly = pivot_y - (fulcrum_x - arm_left) * np.sin(tilt)
    ry = pivot_y + (arm_right - fulcrum_x) * np.sin(tilt)

    ax.plot([lx, rx], [ly, ry], color=DARK, linewidth=5, solid_capstyle='round', zorder=4)
    # Pivot dot
    ax.plot(fulcrum_x, pivot_y, 'o', color=ACCENT, markersize=8, zorder=6, markeredgecolor=DARK, markeredgewidth=1.5)

    # Cup at long end
    cup_x = rx - 0.1
    cup_y = ry + 0.05
    cup = mpatches.FancyBboxPatch((cup_x - 0.4, cup_y), 0.8, 0.5,
                                   boxstyle='round,pad=0.05',
                                   facecolor=ACCENT, edgecolor=DARK, linewidth=1.2, zorder=5)
    ax.add_patch(cup)
    # Ball in cup
    ball = Circle((cup_x, cup_y + 0.65), 0.2, facecolor=ARROW_COLOR, edgecolor=DARK,
                  linewidth=1, zorder=6)
    ax.add_patch(ball)

    # Effort arrow — pushing down on short end
    draw_arrow(ax, (lx + 0.3, ly + 1.8), (lx + 0.3, ly + 0.3), color=ARROW_COLOR, lw=2.5,
               mutation_scale=22)
    ax.text(lx + 0.3, ly + 2.1, 'EFFORT', fontsize=10, ha='center', va='bottom',
            color=ARROW_COLOR, fontweight='bold')

    # Load arrow — going up from cup
    draw_arrow(ax, (cup_x, cup_y + 1.0), (cup_x, cup_y + 2.5), color=ARROW_COLOR, lw=2.5,
               mutation_scale=22)
    ax.text(cup_x, cup_y + 2.7, 'LOAD', fontsize=10, ha='center', va='bottom',
            color=ARROW_COLOR, fontweight='bold')

    # Launch trajectory arc
    theta = np.linspace(0.3, 1.5, 40)
    traj_x = cup_x + 2.0 * np.cos(theta) * (theta - 0.3)
    traj_y = cup_y + 1.5 + 3.0 * np.sin(theta) * (theta - 0.3) - 0.3 * (theta - 0.3)**2
    ax.plot(traj_x, traj_y, '--', color=ARROW_COLOR, linewidth=1.5, alpha=0.5, zorder=3)
    # Arrowhead at end of trajectory
    draw_arrow(ax, (traj_x[-2], traj_y[-2]), (traj_x[-1], traj_y[-1]),
               color=ARROW_COLOR, lw=1.5, mutation_scale=14)

    # Dimension labels for arm lengths
    # Short arm
    ax.annotate('', xy=(lx, -0.6), xytext=(fulcrum_x, -0.6),
                arrowprops=dict(arrowstyle='<->', color=DARK, lw=1.2))
    ax.text((lx + fulcrum_x) / 2, -0.85, 'Short arm\n(80 mm)', fontsize=8,
            ha='center', va='top', color=DARK)

    # Long arm
    ax.annotate('', xy=(fulcrum_x, -0.6), xytext=(rx, -0.6),
                arrowprops=dict(arrowstyle='<->', color=DARK, lw=1.2))
    ax.text((fulcrum_x + rx) / 2, -0.85, 'Long arm (200 mm)', fontsize=8,
            ha='center', va='top', color=DARK)

    # Annotation box
    ann_text = 'Mechanical advantage:\ndistance traded for height'
    ax.text(6.5, 5.8, ann_text, fontsize=9, ha='center', va='center', color=DARK,
            style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=LIGHT_BG, edgecolor=ACCENT,
                      linewidth=1.2))

    save_fig(fig, 'm1_catapult_lever.png')


# ═══════════════════════════════════════════════════════════════════════════════
# M2 — PULLEY LIFT
# ═══════════════════════════════════════════════════════════════════════════════
def draw_m2_pulley():
    print("M2 Pulley Lift — Pulley Mechanics")
    fig, ax = plt.subplots(figsize=(8, 9))
    ax.set_xlim(-1, 9)
    ax.set_ylim(-1.5, 11)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.suptitle('M2 Pulley Lift — Pulley Mechanics', fontsize=14,
                 fontweight='bold', color=DARK, y=0.97)

    # Two vertical uprights
    for x in [1.5, 6.5]:
        ax.plot([x, x], [0, 9], color=DARK, linewidth=4, solid_capstyle='round', zorder=3)
    # Top beam
    ax.plot([1.5, 6.5], [9, 9], color=DARK, linewidth=4, solid_capstyle='round', zorder=3)
    # Base
    ax.plot([0.5, 7.5], [0, 0], color=GREY, linewidth=5, solid_capstyle='round', zorder=2)

    # Pulley wheel at top center
    pulley_cx, pulley_cy = 4.0, 8.5
    pulley_r = 0.55
    # Outer ring
    pulley_outer = Circle((pulley_cx, pulley_cy), pulley_r, facecolor=LIGHT_BG,
                          edgecolor=ACCENT, linewidth=2.5, zorder=5)
    ax.add_patch(pulley_outer)
    # Groove (inner circle)
    pulley_inner = Circle((pulley_cx, pulley_cy), pulley_r * 0.3, facecolor=ACCENT,
                          edgecolor=DARK, linewidth=1.5, zorder=6)
    ax.add_patch(pulley_inner)
    # Axle mount
    ax.plot([pulley_cx, pulley_cx], [pulley_cy + pulley_r, 9], color=DARK, linewidth=2, zorder=4)
    label_box(ax, pulley_cx + 2.2, pulley_cy, 'Pulley\nredirects force')

    # Winch drum at base (right upright)
    winch_cx, winch_cy = 6.5, 1.5
    winch_r = 0.5
    winch = Circle((winch_cx, winch_cy), winch_r, facecolor=ACCENT, edgecolor=DARK,
                   linewidth=2, zorder=5)
    ax.add_patch(winch)
    # Winch axle dot
    ax.plot(winch_cx, winch_cy, 'o', color=DARK, markersize=5, zorder=7)
    label_box(ax, winch_cx + 1.5, winch_cy, 'Winch\ndrum')

    # Crank handle
    crank_angle = np.pi * 0.25
    crank_len = 0.9
    crank_ex = winch_cx + crank_len * np.cos(crank_angle)
    crank_ey = winch_cy + crank_len * np.sin(crank_angle)
    ax.plot([winch_cx, crank_ex], [winch_cy, crank_ey], color=DARK, linewidth=2.5, zorder=6)
    ax.plot(crank_ex, crank_ey, 'o', color=DARK, markersize=7, zorder=7)

    # Crank rotation arrow
    arc_angles = np.linspace(20, 300, 60)
    arc_r = 1.1
    arc_x = winch_cx + arc_r * np.cos(np.radians(arc_angles))
    arc_y = winch_cy + arc_r * np.sin(np.radians(arc_angles))
    ax.plot(arc_x, arc_y, color=ARROW_COLOR, linewidth=1.8, zorder=4)
    draw_arrow(ax, (arc_x[-2], arc_y[-2]), (arc_x[-1], arc_y[-1]),
               color=ARROW_COLOR, lw=1.8, mutation_scale=16)
    ax.text(winch_cx + 1.5, winch_cy + 1.2, 'Turn\ncrank', fontsize=8,
            color=ARROW_COLOR, fontweight='bold', ha='center')

    # String path: from winch top, up right upright, across top, over pulley, down to hook
    string_color = DARK
    # From winch drum top to top of right upright area, over to pulley, down
    string_pts_x = [winch_cx, winch_cx, pulley_cx + pulley_r * 0.05]
    string_pts_y = [winch_cy + winch_r, 8.5, pulley_cy]

    # String up from winch
    ax.plot([winch_cx - 0.05, pulley_cx + pulley_r], [winch_cy + winch_r, pulley_cy],
            color=string_color, linewidth=1.5, linestyle='-', zorder=4)

    # String over pulley (small arc)
    arc_theta = np.linspace(0, np.pi, 30)
    arc_sx = pulley_cx + pulley_r * np.cos(arc_theta)
    arc_sy = pulley_cy + pulley_r * np.sin(arc_theta)
    # Just show straight over the top
    # String going down from pulley left side
    hook_x = pulley_cx - 0.05
    hook_y = 3.0
    ax.plot([pulley_cx - pulley_r, hook_x], [pulley_cy, hook_y],
            color=string_color, linewidth=1.5, zorder=4)

    # Hook
    hook_t = np.linspace(0, np.pi * 1.3, 30)
    hook_r_size = 0.3
    hx = hook_x + hook_r_size * np.sin(hook_t)
    hy = hook_y - 0.3 - hook_r_size * (1 - np.cos(hook_t))
    ax.plot(hx, hy, color=DARK, linewidth=2.5, zorder=5)

    # Load box
    load_w, load_h = 1.4, 1.0
    load_x = hook_x - load_w / 2
    load_y = hook_y - 0.3 - hook_r_size * 2 - load_h
    load_box = mpatches.FancyBboxPatch((load_x, load_y), load_w, load_h,
                                        boxstyle='round,pad=0.08',
                                        facecolor=ACCENT, edgecolor=DARK,
                                        linewidth=1.5, zorder=5, alpha=0.7)
    ax.add_patch(load_box)
    ax.text(hook_x, load_y + load_h / 2, 'LOAD', fontsize=10, ha='center',
            va='center', fontweight='bold', color=DARK, zorder=6)

    # Load going up arrow
    draw_arrow(ax, (hook_x - 1.2, load_y + 0.2), (hook_x - 1.2, load_y + 2.0),
               color=ARROW_COLOR, lw=2.5, mutation_scale=20)
    ax.text(hook_x - 1.2, load_y + 2.3, 'Load\ngoes UP', fontsize=9,
            ha='center', color=ARROW_COLOR, fontweight='bold')

    # Pull direction arrow on string
    mid_string_y = (winch_cy + winch_r + pulley_cy) / 2
    draw_arrow(ax, (winch_cx + 0.6, mid_string_y - 0.5), (winch_cx + 0.6, mid_string_y + 0.8),
               color=ARROW_COLOR, lw=2, mutation_scale=16)
    ax.text(winch_cx + 1.3, mid_string_y, 'Pull', fontsize=9,
            color=ARROW_COLOR, fontweight='bold', ha='left')

    save_fig(fig, 'm2_pulley_lift.png')


# ═══════════════════════════════════════════════════════════════════════════════
# M3 — AUTOMATA CARD / CAM MECHANISM
# ═══════════════════════════════════════════════════════════════════════════════
def draw_m3_cam():
    print("M3 Automata Card — Cam Mechanism")
    fig = plt.figure(figsize=(11, 6.5))
    # Main diagram on left, inset on right
    ax = fig.add_axes([0.05, 0.05, 0.62, 0.85])
    ax_inset = fig.add_axes([0.70, 0.08, 0.28, 0.82])

    ax.set_xlim(-2, 8)
    ax.set_ylim(-2, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.suptitle('M3 Automata Card — Cam Mechanism', fontsize=14,
                 fontweight='bold', color=DARK, y=0.97)

    # Housing / frame
    frame = mpatches.FancyBboxPatch((-0.5, -1.5), 7, 7.5, boxstyle='round,pad=0.15',
                                     facecolor=LIGHT_BG, edgecolor=ACCENT,
                                     linewidth=1, alpha=0.3, zorder=0)
    ax.add_patch(frame)

    # Cam (egg shape) — use an ellipse rotated
    cam_cx, cam_cy = 3, 1.5
    cam_angle = 30
    cam_w, cam_h = 2.8, 2.0
    # Draw cam as ellipse
    cam = mpatches.Ellipse((cam_cx, cam_cy), cam_w, cam_h, angle=cam_angle,
                            facecolor=ACCENT, edgecolor=DARK, linewidth=2, zorder=4, alpha=0.8)
    ax.add_patch(cam)

    # Cam axle
    axle = Circle((cam_cx, cam_cy), 0.15, facecolor=DARK, edgecolor=DARK, zorder=6)
    ax.add_patch(axle)
    label_box(ax, cam_cx - 2.0, cam_cy, 'Cam', fontsize=10)

    # Axle line extending left
    ax.plot([cam_cx - 2.5, cam_cx - 0.15], [cam_cy, cam_cy], color=DARK, linewidth=3, zorder=3)
    ax.plot(cam_cx - 2.5, cam_cy, 'o', color=GREY, markersize=8, zorder=4)

    # Rotary input arrow (circular)
    arc_angles = np.linspace(200, 510, 60)
    arc_r = 1.8
    arc_x = cam_cx + arc_r * np.cos(np.radians(arc_angles))
    arc_y = cam_cy + arc_r * np.sin(np.radians(arc_angles)) * 0.4 - 0.5
    ax.plot(arc_x[:55], arc_y[:55], color=ARROW_COLOR, linewidth=2, zorder=3)
    draw_arrow(ax, (arc_x[53], arc_y[53]), (arc_x[55], arc_y[55]),
               color=ARROW_COLOR, lw=2, mutation_scale=18)
    ax.text(cam_cx, cam_cy - 1.8, 'Rotary input', fontsize=10, ha='center',
            color=ARROW_COLOR, fontweight='bold')

    # Follower — vertical rod sitting on top of cam
    # Compute top of cam at current angle
    follower_x = cam_cx + 0.3
    cam_top = cam_cy + cam_h / 2 * np.cos(np.radians(cam_angle)) + cam_w / 2 * np.sin(np.radians(cam_angle)) * 0.3
    follower_bottom = cam_top + 0.3
    follower_top = follower_bottom + 2.5

    # Follower rod
    ax.plot([follower_x, follower_x], [follower_bottom, follower_top],
            color=DARK, linewidth=4, solid_capstyle='round', zorder=5)
    # Flat foot on follower
    ax.plot([follower_x - 0.4, follower_x + 0.4], [follower_bottom, follower_bottom],
            color=DARK, linewidth=4, solid_capstyle='round', zorder=5)

    # Character/figure on top of follower
    fig_cx = follower_x
    fig_cy = follower_top + 0.4
    head = Circle((fig_cx, fig_cy + 0.3), 0.25, facecolor=ARROW_COLOR, edgecolor=DARK,
                  linewidth=1.5, zorder=6)
    ax.add_patch(head)
    body = mpatches.FancyBboxPatch((fig_cx - 0.2, fig_cy - 0.2), 0.4, 0.4,
                                    boxstyle='round,pad=0.05',
                                    facecolor=ARROW_COLOR, edgecolor=DARK,
                                    linewidth=1, zorder=6, alpha=0.7)
    ax.add_patch(body)

    label_box(ax, follower_x + 2.0, (follower_bottom + follower_top) / 2, 'Follower', fontsize=10)

    # Dashed lines showing travel range
    travel_low = follower_bottom - 0.6
    travel_high = follower_bottom + 0.6
    ax.plot([follower_x - 0.8, follower_x + 0.8], [travel_low, travel_low],
            '--', color=GREY, linewidth=1.2, zorder=2)
    ax.plot([follower_x - 0.8, follower_x + 0.8], [travel_high, travel_high],
            '--', color=GREY, linewidth=1.2, zorder=2)
    # Travel range bracket
    ax.annotate('', xy=(follower_x + 1.0, travel_low), xytext=(follower_x + 1.0, travel_high),
                arrowprops=dict(arrowstyle='<->', color=DARK, lw=1.2))
    ax.text(follower_x + 1.3, (travel_low + travel_high) / 2, 'Travel\nrange',
            fontsize=7, ha='left', va='center', color=DARK)

    # Linear output arrow
    draw_arrow(ax, (follower_x - 1.2, follower_top - 0.5), (follower_x - 1.2, follower_top + 0.8),
               color=ARROW_COLOR, lw=2.5, mutation_scale=20)
    draw_arrow(ax, (follower_x - 1.2, follower_top + 0.3), (follower_x - 1.2, follower_top - 1.0),
               color=ARROW_COLOR, lw=2.5, mutation_scale=20)
    ax.text(follower_x - 1.2, follower_top + 1.1, 'Linear\noutput', fontsize=10,
            ha='center', color=ARROW_COLOR, fontweight='bold')

    # ── Inset: 3 cam shapes ──
    ax_inset.set_xlim(-1.5, 1.5)
    ax_inset.set_ylim(-0.5, 9)
    ax_inset.set_aspect('equal')
    ax_inset.axis('off')
    ax_inset.set_title('Cam Shapes', fontsize=11, fontweight='bold', color=DARK, pad=8)

    cam_shapes = [
        ('Egg cam\n(smooth rise & fall)', 'egg'),
        ('Eccentric\n(sinusoidal)', 'round'),
        ('Snail cam\n(gradual rise,\nsudden drop)', 'snail'),
    ]

    for i, (desc, shape) in enumerate(cam_shapes):
        cy = 7.5 - i * 3.2
        if shape == 'egg':
            cam_s = mpatches.Ellipse((0, cy), 1.6, 1.1, angle=0,
                                      facecolor=ACCENT, edgecolor=DARK, linewidth=1.5, alpha=0.7)
        elif shape == 'round':
            cam_s = mpatches.Ellipse((0.2, cy), 1.4, 1.4, angle=0,
                                      facecolor=ACCENT, edgecolor=DARK, linewidth=1.5, alpha=0.7)
            # Offset axle
            ax_inset.plot(-0.1, cy, 'o', color=DARK, markersize=4, zorder=6)
        else:  # snail
            theta_s = np.linspace(0, 2 * np.pi, 100)
            r_s = 0.4 + 0.35 * theta_s / (2 * np.pi)
            sx = r_s * np.cos(theta_s)
            sy = cy + r_s * np.sin(theta_s)
            ax_inset.fill(sx, sy, facecolor=ACCENT, edgecolor=DARK, linewidth=1.5, alpha=0.7, zorder=4)
            ax_inset.plot(0, cy, 'o', color=DARK, markersize=4, zorder=6)

        if shape != 'snail':
            ax_inset.add_patch(cam_s)
            ax_inset.plot(0, cy, 'o', color=DARK, markersize=4, zorder=6)

        ax_inset.text(0, cy - 1.1, desc, fontsize=7, ha='center', va='top', color=DARK,
                      style='italic')

    save_fig(fig, 'm3_cam_mechanism.png')


# ═══════════════════════════════════════════════════════════════════════════════
# M4 — GEAR-DOWN MOTOR / GEAR RATIO
# ═══════════════════════════════════════════════════════════════════════════════
def draw_m4_gears():
    print("M4 Gear-Down Motor — Gear Ratio")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.set_xlim(-3, 11)
    ax.set_ylim(-3, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.suptitle('M4 Gear-Down Motor — Gear Ratio', fontsize=14,
                 fontweight='bold', color=DARK, y=0.97)

    # Small gear (12 teeth) — left
    sg_cx, sg_cy = 2, 2
    sg_r = 1.2  # radius
    sg_teeth = 12

    # Large gear (36 teeth) — right
    lg_cx = sg_cx + sg_r + 3.0 - 0.08  # meshing
    lg_cy = 2
    lg_r = 3.0
    lg_teeth = 36

    # Draw gears
    for cx, cy, r, teeth, label_text in [
        (sg_cx, sg_cy, sg_r, sg_teeth, '12 teeth'),
        (lg_cx, lg_cy, lg_r, lg_teeth, '36 teeth'),
    ]:
        # Gear body
        gear_body = Circle((cx, cy), r * 0.88, facecolor=LIGHT_BG if r < 2 else ACCENT,
                           edgecolor=DARK, linewidth=1.5, zorder=3, alpha=0.7)
        ax.add_patch(gear_body)

        # Teeth
        for t_i in range(teeth):
            angle = 2 * np.pi * t_i / teeth
            tooth_inner = r * 0.85
            tooth_outer = r
            tx1 = cx + tooth_inner * np.cos(angle - 0.5 * np.pi / teeth)
            ty1 = cy + tooth_inner * np.sin(angle - 0.5 * np.pi / teeth)
            tx2 = cx + tooth_outer * np.cos(angle - 0.3 * np.pi / teeth)
            ty2 = cy + tooth_outer * np.sin(angle - 0.3 * np.pi / teeth)
            tx3 = cx + tooth_outer * np.cos(angle + 0.3 * np.pi / teeth)
            ty3 = cy + tooth_outer * np.sin(angle + 0.3 * np.pi / teeth)
            tx4 = cx + tooth_inner * np.cos(angle + 0.5 * np.pi / teeth)
            ty4 = cy + tooth_inner * np.sin(angle + 0.5 * np.pi / teeth)
            tooth_poly = Polygon([[tx1, ty1], [tx2, ty2], [tx3, ty3], [tx4, ty4]],
                                 closed=True, facecolor=ACCENT if r < 2 else '#00b5b7',
                                 edgecolor=DARK, linewidth=0.6, zorder=4)
            ax.add_patch(tooth_poly)

        # Center hole
        center = Circle((cx, cy), r * 0.12, facecolor=DARK, edgecolor=DARK, zorder=5)
        ax.add_patch(center)

        # Tooth count label
        ax.text(cx, cy - r * 0.35, label_text, fontsize=8, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=6)

    # Rotation arrows
    # Small gear — clockwise
    arc_angles = np.linspace(60, 320, 50)
    arc_r_s = sg_r + 0.4
    ax.plot(sg_cx + arc_r_s * np.cos(np.radians(arc_angles)),
            sg_cy + arc_r_s * np.sin(np.radians(arc_angles)),
            color=ARROW_COLOR, linewidth=2, zorder=6)
    draw_arrow(ax,
               (sg_cx + arc_r_s * np.cos(np.radians(318)),
                sg_cy + arc_r_s * np.sin(np.radians(318))),
               (sg_cx + arc_r_s * np.cos(np.radians(320)),
                sg_cy + arc_r_s * np.sin(np.radians(320))),
               color=ARROW_COLOR, lw=2, mutation_scale=18)

    # Large gear — counter-clockwise
    arc_angles2 = np.linspace(120, 400, 50)
    arc_r_l = lg_r + 0.4
    ax.plot(lg_cx + arc_r_l * np.cos(np.radians(arc_angles2)),
            lg_cy + arc_r_l * np.sin(np.radians(arc_angles2)),
            color=ARROW_COLOR, linewidth=2, zorder=6)
    draw_arrow(ax,
               (lg_cx + arc_r_l * np.cos(np.radians(122)),
                lg_cy + arc_r_l * np.sin(np.radians(122))),
               (lg_cx + arc_r_l * np.cos(np.radians(120)),
                lg_cy + arc_r_l * np.sin(np.radians(120))),
               color=ARROW_COLOR, lw=2, mutation_scale=18)

    # Motor label (left)
    label_box(ax, sg_cx, sg_cy + sg_r + 1.2, 'Motor\n(fast, low torque)', fontsize=9)
    # Speed arrow — fast
    draw_arrow(ax, (sg_cx - 1.8, sg_cy + sg_r + 0.5), (sg_cx - 0.8, sg_cy + sg_r + 0.5),
               color=ARROW_COLOR, lw=2, mutation_scale=14)
    draw_arrow(ax, (sg_cx - 1.6, sg_cy + sg_r + 0.5), (sg_cx - 0.6, sg_cy + sg_r + 0.5),
               color=ARROW_COLOR, lw=1.5, mutation_scale=12)
    ax.text(sg_cx - 1.2, sg_cy + sg_r + 0.85, 'FAST', fontsize=8, ha='center',
            color=ARROW_COLOR, fontweight='bold')

    # Output label (right)
    label_box(ax, lg_cx, lg_cy - lg_r - 0.8, 'Output\n(slow, high torque)', fontsize=9)
    # Speed arrow — slow
    draw_arrow(ax, (lg_cx + 2.0, lg_cy - lg_r - 0.3), (lg_cx + 2.5, lg_cy - lg_r - 0.3),
               color=ARROW_COLOR, lw=1.5, mutation_scale=10)
    ax.text(lg_cx + 2.25, lg_cy - lg_r - 0.6, 'SLOW', fontsize=8, ha='center',
            color=ARROW_COLOR, fontweight='bold')

    # Annotation box
    ax.text(4.0, -2.3, 'Ratio 1:3 \u2014 3\u00d7 slower, 3\u00d7 stronger', fontsize=11,
            ha='center', va='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=LIGHT_BG, edgecolor=ACCENT,
                      linewidth=1.5))

    save_fig(fig, 'm4_gear_ratio.png')


# ═══════════════════════════════════════════════════════════════════════════════
# M5 — HAND-CRANK AUTOMATA / CRANK + CAM
# ═══════════════════════════════════════════════════════════════════════════════
def draw_m5_crank_cam():
    print("M5 Hand-Crank Automata — Crank + Cam")
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.set_xlim(-2, 12)
    ax.set_ylim(-2, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.suptitle('M5 Hand-Crank Automata \u2014 Crank + Cam Combined', fontsize=14,
                 fontweight='bold', color=DARK, y=0.97)

    # Scene panel (back panel)
    panel = mpatches.FancyBboxPatch((4, 3.5), 6, 4, boxstyle='round,pad=0.1',
                                     facecolor=LIGHT_BG, edgecolor=ACCENT,
                                     linewidth=1.5, zorder=1, alpha=0.5)
    ax.add_patch(panel)
    ax.text(7, 7.1, 'Scene Panel', fontsize=9, ha='center', color=GREY, style='italic')

    # Platform / box
    box = mpatches.FancyBboxPatch((-0.5, -0.5), 11, 3.5, boxstyle='round,pad=0.1',
                                   facecolor='#F3F4F6', edgecolor=DARK,
                                   linewidth=1.5, zorder=2)
    ax.add_patch(box)
    ax.text(5, -0.1, 'Mechanism Box', fontsize=8, ha='center', color=GREY, style='italic')

    # Crank disc (left side)
    crank_cx, crank_cy = 1.5, 1.5
    crank_r = 0.8
    crank_disc = Circle((crank_cx, crank_cy), crank_r, facecolor=ACCENT,
                        edgecolor=DARK, linewidth=2, zorder=5, alpha=0.8)
    ax.add_patch(crank_disc)
    ax.plot(crank_cx, crank_cy, 'o', color=DARK, markersize=6, zorder=7)
    label_box(ax, crank_cx, crank_cy - 1.4, 'Crank Disc', fontsize=8)

    # Handle extending left
    handle_x = crank_cx - 1.5
    ax.plot([crank_cx, handle_x], [crank_cy, crank_cy], color=DARK, linewidth=3, zorder=4)
    ax.plot(handle_x, crank_cy, 'o', color=ARROW_COLOR, markersize=8, zorder=6)
    ax.text(handle_x - 0.3, crank_cy + 0.4, 'Handle', fontsize=8, ha='center', color=DARK,
            fontweight='bold')

    # Rotation arrow on crank
    arc_a = np.linspace(30, 330, 50)
    arc_rr = crank_r + 0.35
    ax.plot(crank_cx + arc_rr * np.cos(np.radians(arc_a)),
            crank_cy + arc_rr * np.sin(np.radians(arc_a)),
            color=ARROW_COLOR, linewidth=1.5, zorder=4)
    draw_arrow(ax,
               (crank_cx + arc_rr * np.cos(np.radians(328)),
                crank_cy + arc_rr * np.sin(np.radians(328))),
               (crank_cx + arc_rr * np.cos(np.radians(330)),
                crank_cy + arc_rr * np.sin(np.radians(330))),
               color=ARROW_COLOR, lw=1.5, mutation_scale=14)

    # Offset pin on crank disc
    pin_angle = np.radians(40)
    pin_x = crank_cx + crank_r * 0.6 * np.cos(pin_angle)
    pin_y = crank_cy + crank_r * 0.6 * np.sin(pin_angle)
    ax.plot(pin_x, pin_y, 'o', color=DARK, markersize=6, zorder=7)

    # Connecting rod to cam axle
    cam_cx, cam_cy = 5.5, 1.5
    ax.plot([pin_x, cam_cx], [pin_y, cam_cy], color=DARK, linewidth=2.5, zorder=4)
    label_box(ax, (pin_x + cam_cx) / 2, (pin_y + cam_cy) / 2 + 0.6,
              'Connecting Rod', fontsize=8)

    # Shared axle
    ax.plot([cam_cx - 0.3, cam_cx + 0.3], [cam_cy, cam_cy], color=DARK, linewidth=4, zorder=5)

    # Cam (egg-shaped) on shared axle
    cam = mpatches.Ellipse((cam_cx, cam_cy + 0.5), 1.6, 2.2, angle=15,
                            facecolor=ACCENT, edgecolor=DARK, linewidth=2, zorder=4, alpha=0.7)
    ax.add_patch(cam)
    ax.plot(cam_cx, cam_cy, 'o', color=DARK, markersize=5, zorder=7)
    label_box(ax, cam_cx + 1.5, cam_cy, 'Cam', fontsize=9)

    # Follower on top of cam
    follower_x = cam_cx + 0.1
    follower_bottom = cam_cy + 1.7
    follower_top = 3.0 + 2.5

    # Guide slot
    ax.plot([follower_x - 0.15, follower_x - 0.15], [follower_bottom - 0.3, follower_top + 0.3],
            color=GREY, linewidth=1, linestyle='--', zorder=3)
    ax.plot([follower_x + 0.15, follower_x + 0.15], [follower_bottom - 0.3, follower_top + 0.3],
            color=GREY, linewidth=1, linestyle='--', zorder=3)

    # Follower rod
    ax.plot([follower_x, follower_x], [follower_bottom, follower_top],
            color=DARK, linewidth=3.5, solid_capstyle='round', zorder=5)
    # Flat foot
    ax.plot([follower_x - 0.3, follower_x + 0.3], [follower_bottom, follower_bottom],
            color=DARK, linewidth=3, zorder=5)
    label_box(ax, follower_x + 1.8, (follower_bottom + follower_top) / 2, 'Follower', fontsize=8)

    # Figure on top
    fig_head = Circle((follower_x, follower_top + 0.5), 0.3, facecolor=ARROW_COLOR,
                      edgecolor=DARK, linewidth=1.5, zorder=6)
    ax.add_patch(fig_head)

    # Up-down arrow
    draw_arrow(ax, (follower_x - 0.8, follower_top - 0.3), (follower_x - 0.8, follower_top + 0.7),
               color=ARROW_COLOR, lw=2, mutation_scale=16)
    draw_arrow(ax, (follower_x - 0.8, follower_top + 0.4), (follower_x - 0.8, follower_top - 0.6),
               color=ARROW_COLOR, lw=2, mutation_scale=16)

    # Motion path labels
    ax.annotate('Rotary\nmotion', xy=(crank_cx, crank_cy + 1.6), fontsize=8,
                ha='center', color=ARROW_COLOR, fontweight='bold')
    ax.annotate('', xy=(3.5, 2.5), xytext=(2.5, 2.5),
                arrowprops=dict(arrowstyle='->', color=ARROW_COLOR, lw=1.5))
    ax.annotate('', xy=(cam_cx - 0.5, 3.5), xytext=(cam_cx - 0.5, 2.8),
                arrowprops=dict(arrowstyle='->', color=ARROW_COLOR, lw=1.5))
    ax.text(cam_cx - 0.5, 3.7, 'Up & down\nmotion', fontsize=8, ha='center',
            color=ARROW_COLOR, fontweight='bold')

    save_fig(fig, 'm5_crank_cam.png')


# ═══════════════════════════════════════════════════════════════════════════════
# M6 — TOWER CRANE / COMBINED SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_m6_crane():
    print("M6 Tower Crane — Combined Systems")
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-3, 13)
    ax.set_ylim(-1.5, 14)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.suptitle('M6 Tower Crane \u2014 Combined Systems', fontsize=14,
                 fontweight='bold', color=DARK, y=0.97)

    # Ground
    ax.plot([-2, 12], [0, 0], color=GREY, linewidth=3, zorder=2)
    ax.fill_between([-2, 12], [-0.5, -0.5], [0, 0], color='#F3F4F6', zorder=1)

    # Tower (vertical lattice)
    tower_x = 5
    tower_h = 10
    tower_w = 0.8
    # Main uprights
    ax.plot([tower_x - tower_w / 2, tower_x - tower_w / 2], [0, tower_h],
            color=DARK, linewidth=3, zorder=4)
    ax.plot([tower_x + tower_w / 2, tower_x + tower_w / 2], [0, tower_h],
            color=DARK, linewidth=3, zorder=4)
    # Cross bracing
    for i in range(0, int(tower_h), 1):
        if i % 2 == 0:
            ax.plot([tower_x - tower_w / 2, tower_x + tower_w / 2], [i, i + 1],
                    color=DARK, linewidth=1, zorder=3)
        else:
            ax.plot([tower_x + tower_w / 2, tower_x - tower_w / 2], [i, i + 1],
                    color=DARK, linewidth=1, zorder=3)
    # Horizontal ties
    for i in range(0, int(tower_h) + 1, 2):
        ax.plot([tower_x - tower_w / 2, tower_x + tower_w / 2], [i, i],
                color=DARK, linewidth=1.5, zorder=3)

    # Jib arm (horizontal beam at top)
    jib_left = 0
    jib_right = 11
    jib_y = tower_h + 0.3
    ax.plot([jib_left, jib_right], [jib_y, jib_y], color=DARK, linewidth=3, zorder=4)
    ax.plot([jib_left, jib_right], [jib_y + 0.3, jib_y + 0.3], color=DARK, linewidth=1.5, zorder=4)
    # Connection diagonal braces
    ax.plot([tower_x, jib_right - 0.5], [jib_y + 1.5, jib_y + 0.3], color=DARK, linewidth=1.5, zorder=3)
    ax.plot([tower_x, jib_left + 0.5], [jib_y + 1.5, jib_y + 0.3], color=DARK, linewidth=1.5, zorder=3)
    # Top mast
    ax.plot([tower_x, tower_x], [jib_y, jib_y + 1.8], color=DARK, linewidth=2, zorder=4)

    # Pulley at jib tip
    pulley_cx, pulley_cy = jib_right - 0.3, jib_y - 0.5
    pulley_r = 0.35
    pulley = Circle((pulley_cx, pulley_cy), pulley_r, facecolor=LIGHT_BG,
                    edgecolor=ACCENT, linewidth=2, zorder=6)
    ax.add_patch(pulley)
    ax.plot(pulley_cx, pulley_cy, 'o', color=DARK, markersize=4, zorder=7)
    ax.plot([pulley_cx, pulley_cx], [pulley_cy + pulley_r, jib_y], color=DARK, linewidth=2, zorder=5)

    # String from winch at base, up tower, along jib, over pulley, down to hook
    winch_x, winch_y = tower_x + 0.8, 0.8
    # Winch drum
    winch = Circle((winch_x, winch_y), 0.3, facecolor=ACCENT, edgecolor=DARK,
                   linewidth=1.5, zorder=6)
    ax.add_patch(winch)

    # String path
    string_path_x = [winch_x, winch_x + 0.5, pulley_cx + pulley_r, pulley_cx + pulley_r]
    string_path_y = [winch_y + 0.3, jib_y - 0.3, jib_y - 0.3, pulley_cy]
    ax.plot([winch_x, pulley_cx + pulley_r * 0.7], [winch_y + 0.3, pulley_cy + pulley_r * 0.5],
            color=DARK, linewidth=1.2, zorder=4, linestyle='-')
    # String down from pulley
    hook_y = 5
    ax.plot([pulley_cx - pulley_r * 0.3, pulley_cx - 0.2], [pulley_cy - pulley_r * 0.8, hook_y],
            color=DARK, linewidth=1.2, zorder=4)

    # Hook
    hook_t = np.linspace(0, np.pi * 1.3, 30)
    hook_r_s = 0.25
    hx = pulley_cx - 0.2 + hook_r_s * np.sin(hook_t)
    hy = hook_y - hook_r_s * (1 - np.cos(hook_t))
    ax.plot(hx, hy, color=DARK, linewidth=2, zorder=5)

    # Load
    load_w, load_h = 1.2, 0.8
    load_box = mpatches.FancyBboxPatch((pulley_cx - 0.2 - load_w / 2, hook_y - load_h - 0.7),
                                        load_w, load_h, boxstyle='round,pad=0.05',
                                        facecolor=ACCENT, edgecolor=DARK,
                                        linewidth=1.5, zorder=5, alpha=0.7)
    ax.add_patch(load_box)
    ax.text(pulley_cx - 0.2, hook_y - load_h / 2 - 0.7, 'Load', fontsize=8,
            ha='center', va='center', fontweight='bold', color=DARK, zorder=6)

    # Gear pair on winch
    sg_r, lg_r_g = 0.25, 0.5
    sg = Circle((winch_x - 0.8, winch_y), sg_r, facecolor=LIGHT_BG, edgecolor=DARK,
                linewidth=1.5, zorder=6)
    lg = Circle((winch_x, winch_y), lg_r_g, facecolor=ACCENT, edgecolor=DARK,
                linewidth=1.5, zorder=5, alpha=0.6)
    ax.add_patch(lg)
    ax.add_patch(sg)
    label_box(ax, winch_x - 1.8, winch_y, 'Gears reduce\neffort', fontsize=8)

    # Counterweight on opposite side of jib
    cw_x = jib_left + 0.8
    cw_y = jib_y - 1.5
    cw = mpatches.FancyBboxPatch((cw_x - 0.6, cw_y - 0.5), 1.2, 1.0,
                                  boxstyle='round,pad=0.05',
                                  facecolor=GREY, edgecolor=DARK,
                                  linewidth=1.5, zorder=5)
    ax.add_patch(cw)
    ax.plot([cw_x, cw_x], [jib_y, cw_y + 0.5], color=DARK, linewidth=2, zorder=4)
    ax.text(cw_x, cw_y - 0.8, 'Counter-\nweight', fontsize=8, ha='center',
            fontweight='bold', color=DARK)

    # Labels with arrows
    label_box(ax, pulley_cx + 1.8, pulley_cy + 0.3, 'Pulley redirects\nforce', fontsize=8)
    label_box(ax, cw_x - 1.5, cw_y + 1.5, 'Counterweight\n= stability', fontsize=8)

    # Force arrows
    draw_arrow(ax, (pulley_cx - 0.2, hook_y - 0.3), (pulley_cx - 0.2, hook_y - 1.5),
               color=ARROW_COLOR, lw=2, mutation_scale=16)
    ax.text(pulley_cx + 0.6, hook_y - 1.0, 'Gravity', fontsize=8, color=ARROW_COLOR, fontweight='bold')

    draw_arrow(ax, (pulley_cx - 0.8, hook_y + 0.5), (pulley_cx - 0.8, hook_y + 2.0),
               color=ARROW_COLOR, lw=2, mutation_scale=16)
    ax.text(pulley_cx - 1.8, hook_y + 1.5, 'Lift', fontsize=8, color=ARROW_COLOR, fontweight='bold')

    save_fig(fig, 'm6_tower_crane.png')


# ═══════════════════════════════════════════════════════════════════════════════
# M7 — ROVER / GEAR REDUCTION FOR CLIMBING
# ═══════════════════════════════════════════════════════════════════════════════
def draw_m7_rover():
    print("M7 Rover — Gear Reduction for Climbing")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.set_xlim(-1, 13)
    ax.set_ylim(-2, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.suptitle('M7 Rover \u2014 Gear Reduction for Climbing', fontsize=14,
                 fontweight='bold', color=DARK, y=0.97)

    # Ramp
    ramp_angle = 25  # degrees
    ramp_rad = np.radians(ramp_angle)
    ramp_len = 11
    ramp_x = [0, ramp_len * np.cos(ramp_rad)]
    ramp_y = [0, ramp_len * np.sin(ramp_rad)]
    ax.fill([0, ramp_x[1], ramp_x[1], 0], [0, ramp_y[1], 0, 0],
            color='#F3F4F6', zorder=1)
    ax.plot(ramp_x, ramp_y, color=DARK, linewidth=2.5, zorder=2)
    ax.plot([0, ramp_x[1]], [0, 0], color=GREY, linewidth=1.5, zorder=2)

    # Angle arc
    arc_a = np.linspace(0, ramp_rad, 30)
    arc_rr = 2.0
    ax.plot(arc_rr * np.cos(arc_a), arc_rr * np.sin(arc_a), color=DARK, linewidth=1.2, zorder=3)
    ax.text(2.3, 0.5, f'{ramp_angle}\u00b0', fontsize=10, color=DARK, fontweight='bold')

    # Rover position on ramp (roughly middle)
    rover_pos = 4.5  # distance along ramp
    rover_cx = rover_pos * np.cos(ramp_rad)
    rover_cy = rover_pos * np.sin(ramp_rad)

    # Chassis — rotated rectangle
    chassis_w, chassis_h = 3.5, 0.8
    # Compute chassis corners (rotated)
    cos_a, sin_a = np.cos(ramp_rad), np.sin(ramp_rad)
    # Center of chassis
    ccx = rover_cx
    ccy = rover_cy + 0.7

    def rot_point(dx, dy):
        return ccx + dx * cos_a - dy * sin_a, ccy + dx * sin_a + dy * cos_a

    p1 = rot_point(-chassis_w / 2, -chassis_h / 2)
    p2 = rot_point(chassis_w / 2, -chassis_h / 2)
    p3 = rot_point(chassis_w / 2, chassis_h / 2)
    p4 = rot_point(-chassis_w / 2, chassis_h / 2)

    chassis = Polygon([p1, p2, p3, p4], closed=True, facecolor=ACCENT,
                      edgecolor=DARK, linewidth=2, zorder=5, alpha=0.8)
    ax.add_patch(chassis)

    # Wheels
    wheel_r = 0.45
    for wheel_offset in [-1.2, 1.2]:
        wx, wy = rot_point(wheel_offset, -chassis_h / 2 - 0.1)
        wheel = Circle((wx, wy), wheel_r, facecolor=DARK, edgecolor=DARK,
                       linewidth=1.5, zorder=6)
        ax.add_patch(wheel)
        # Hub
        hub = Circle((wx, wy), wheel_r * 0.3, facecolor=GREY, edgecolor=DARK,
                     linewidth=1, zorder=7)
        ax.add_patch(hub)

    # Gear train diagram (offset, shown as inset-like near the rover)
    # Motor small gear
    gear_label_x = ccx + 2.5 * cos_a + 1.0
    gear_label_y = ccy + 2.5 * sin_a + 1.5

    # Small gear
    sg_cx_g, sg_cy_g = gear_label_x - 0.8, gear_label_y
    sg_r_g = 0.35
    sg = Circle((sg_cx_g, sg_cy_g), sg_r_g, facecolor=LIGHT_BG, edgecolor=DARK,
                linewidth=1.5, zorder=8)
    ax.add_patch(sg)
    ax.plot(sg_cx_g, sg_cy_g, 'o', color=DARK, markersize=3, zorder=9)

    # Large gear
    lg_cx_g = sg_cx_g + sg_r_g + 0.6
    lg_r_g = 0.65
    lg = Circle((lg_cx_g, sg_cy_g), lg_r_g, facecolor=ACCENT, edgecolor=DARK,
                linewidth=1.5, zorder=8, alpha=0.7)
    ax.add_patch(lg)
    ax.plot(lg_cx_g, sg_cy_g, 'o', color=DARK, markersize=3, zorder=9)

    # Arrow from motor to small gear
    ax.text(sg_cx_g, sg_cy_g + 0.7, 'TT Motor', fontsize=8, ha='center', color=DARK,
            fontweight='bold')
    ax.annotate('', xy=(lg_cx_g + 0.8, sg_cy_g), xytext=(lg_cx_g + 0.2, sg_cy_g),
                arrowprops=dict(arrowstyle='->', color=ARROW_COLOR, lw=1.5))
    # Arrow to wheel
    rear_wx, rear_wy = rot_point(1.2, -chassis_h / 2 - 0.1)
    ax.annotate('', xy=(rear_wx, rear_wy + 0.6), xytext=(lg_cx_g + 0.7, sg_cy_g - 0.2),
                arrowprops=dict(arrowstyle='->', color=ARROW_COLOR, lw=1.5,
                                connectionstyle='arc3,rad=-0.2'))
    ax.text(lg_cx_g + 1.2, sg_cy_g, 'Axle', fontsize=7, color=DARK)

    label_box(ax, (sg_cx_g + lg_cx_g) / 2, sg_cy_g - 1.0, 'Gear reduction', fontsize=9)

    # Drive force arrow (along ramp surface)
    drive_start = rot_point(2.5, 0.3)
    drive_end = rot_point(4.0, 0.3)
    draw_arrow(ax, drive_start, drive_end, color=ARROW_COLOR, lw=2.5, mutation_scale=20)
    ax.text(drive_end[0] + 0.3, drive_end[1] + 0.3, 'Drive\nforce', fontsize=9,
            color=ARROW_COLOR, fontweight='bold')

    # Gravity arrow (straight down)
    grav_start = (ccx, ccy + 0.5)
    grav_end = (ccx, ccy - 1.5)
    draw_arrow(ax, grav_start, grav_end, color='#cc4444', lw=2.5, mutation_scale=20)
    ax.text(ccx - 0.8, ccy - 1.5, 'Gravity', fontsize=9, color='#cc4444', fontweight='bold')

    # Annotation
    ax.text(6.5, 7.2, 'Torque > Speed for climbing',
            fontsize=11, ha='center', va='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=LIGHT_BG, edgecolor=ACCENT,
                      linewidth=1.5))

    save_fig(fig, 'm7_rover_gear_reduction.png')


# ═══════════════════════════════════════════════════════════════════════════════
# M8 — ROBOTIC GRIPPER / SCISSOR LINKAGE
# ═══════════════════════════════════════════════════════════════════════════════
def draw_m8_gripper():
    print("M8 Robotic Gripper — Scissor Linkage")
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_xlim(-1, 13)
    ax.set_ylim(-2, 4)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.suptitle('M8 Robotic Gripper \u2014 Scissor Linkage (Top View)', fontsize=14,
                 fontweight='bold', color=DARK, y=0.97)

    # Overall layout: handles (left) -> scissor X (middle) -> jaws (right)

    # ── Handle bars (back / left side) ──
    handle_top_y = 2.0
    handle_bot_y = 0.0
    handle_x_left = 0.5
    handle_x_right = 3.0

    # Top handle
    ax.plot([handle_x_left, handle_x_right], [handle_top_y, handle_top_y],
            color=DARK, linewidth=6, solid_capstyle='round', zorder=5)
    # Bottom handle
    ax.plot([handle_x_left, handle_x_right], [handle_bot_y, handle_bot_y],
            color=DARK, linewidth=6, solid_capstyle='round', zorder=5)

    # Squeeze arrows on handles
    draw_arrow(ax, (handle_x_left - 0.3, handle_top_y + 0.8),
               (handle_x_left - 0.3, handle_top_y + 0.1),
               color=ARROW_COLOR, lw=2.5, mutation_scale=18)
    draw_arrow(ax, (handle_x_left - 0.3, handle_bot_y - 0.8),
               (handle_x_left - 0.3, handle_bot_y - 0.1),
               color=ARROW_COLOR, lw=2.5, mutation_scale=18)
    ax.text(handle_x_left - 0.3, 1.0, 'Squeeze', fontsize=9, ha='center', va='center',
            color=ARROW_COLOR, fontweight='bold', rotation=90)

    label_box(ax, handle_x_left, handle_top_y + 1.3, 'Input\n(squeeze)', fontsize=9)

    # Handle grip ends (rounded)
    for y in [handle_top_y, handle_bot_y]:
        grip = Circle((handle_x_left, y), 0.15, facecolor=ARROW_COLOR, edgecolor=DARK,
                      linewidth=1.5, zorder=6)
        ax.add_patch(grip)

    # ── Scissor linkage (X-shaped) ──
    # Two crossing arms
    scissor_left = handle_x_right
    scissor_right = 7.5
    pivot_x = (scissor_left + scissor_right) / 2
    pivot_y = 1.0  # center

    spread = 1.0  # how far arms spread at ends

    # Arm 1: top-left to bottom-right
    ax.plot([scissor_left, scissor_right],
            [handle_top_y, handle_bot_y],
            color=ACCENT, linewidth=5, solid_capstyle='round', zorder=4)
    # Arm 2: bottom-left to top-right
    ax.plot([scissor_left, scissor_right],
            [handle_bot_y, handle_top_y],
            color=ACCENT, linewidth=5, solid_capstyle='round', zorder=4)

    # Second X stage for more amplification
    scissor_left2 = scissor_right
    scissor_right2 = scissor_right + 3.0
    # Same crossing pattern reversed
    ax.plot([scissor_left2, scissor_right2],
            [handle_top_y, handle_bot_y + 0.3],
            color=ACCENT, linewidth=5, solid_capstyle='round', zorder=4, alpha=0.8)
    ax.plot([scissor_left2, scissor_right2],
            [handle_bot_y, handle_top_y - 0.3],
            color=ACCENT, linewidth=5, solid_capstyle='round', zorder=4, alpha=0.8)

    # Pivot points (circles at crossings and joints)
    pivot_points = [
        (scissor_left, handle_top_y), (scissor_left, handle_bot_y),
        (pivot_x, pivot_y),
        (scissor_right, handle_top_y), (scissor_right, handle_bot_y),
        ((scissor_left2 + scissor_right2) / 2, pivot_y),
        (scissor_right2, handle_bot_y + 0.3), (scissor_right2, handle_top_y - 0.3),
    ]
    for px, py in pivot_points:
        piv = Circle((px, py), 0.12, facecolor='white', edgecolor=DARK,
                     linewidth=1.5, zorder=7)
        ax.add_patch(piv)

    label_box(ax, pivot_x, pivot_y - 1.5, 'Linkage transfers\nmotion', fontsize=9)

    # ── Jaw pieces (right / front) ──
    jaw_x_start = scissor_right2
    jaw_x_end = jaw_x_start + 1.5
    jaw_top_y = handle_top_y - 0.3
    jaw_bot_y = handle_bot_y + 0.3

    # Top jaw
    jaw_top = Polygon([
        [jaw_x_start, jaw_top_y + 0.25],
        [jaw_x_end, jaw_top_y - 0.15],
        [jaw_x_end, jaw_top_y - 0.45],
        [jaw_x_start, jaw_top_y - 0.25],
    ], closed=True, facecolor=DARK, edgecolor=DARK, linewidth=1.5, zorder=5)
    ax.add_patch(jaw_top)

    # Bottom jaw
    jaw_bot = Polygon([
        [jaw_x_start, jaw_bot_y - 0.25],
        [jaw_x_end, jaw_bot_y + 0.15],
        [jaw_x_end, jaw_bot_y + 0.45],
        [jaw_x_start, jaw_bot_y + 0.25],
    ], closed=True, facecolor=DARK, edgecolor=DARK, linewidth=1.5, zorder=5)
    ax.add_patch(jaw_bot)

    # Jaw close arrows
    draw_arrow(ax, (jaw_x_end + 0.5, jaw_top_y + 0.2),
               (jaw_x_end + 0.5, jaw_top_y - 0.6),
               color=ARROW_COLOR, lw=2.5, mutation_scale=18)
    draw_arrow(ax, (jaw_x_end + 0.5, jaw_bot_y - 0.2),
               (jaw_x_end + 0.5, jaw_bot_y + 0.6),
               color=ARROW_COLOR, lw=2.5, mutation_scale=18)
    ax.text(jaw_x_end + 0.5, 1.0, 'Close', fontsize=9, ha='center', va='center',
            color=ARROW_COLOR, fontweight='bold', rotation=90)

    label_box(ax, jaw_x_end + 0.5, jaw_top_y + 1.0, 'Output\n(grip)', fontsize=9)

    # Object being gripped (dashed circle between jaws)
    obj = Circle((jaw_x_end - 0.2, 1.0), 0.35, facecolor='none', edgecolor=ARROW_COLOR,
                 linewidth=1.5, linestyle='--', zorder=6)
    ax.add_patch(obj)
    ax.text(jaw_x_end - 0.2, 1.0, '?', fontsize=10, ha='center', va='center',
            color=ARROW_COLOR, fontweight='bold')

    # Flow arrows along bottom
    ax.annotate('', xy=(4.5, -1.3), xytext=(1.5, -1.3),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=1.5))
    ax.annotate('', xy=(9.0, -1.3), xytext=(5.5, -1.3),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=1.5))
    ax.text(3.0, -1.6, 'Input force', fontsize=8, ha='center', color=DARK)
    ax.text(7.25, -1.6, 'Amplified & redirected', fontsize=8, ha='center', color=DARK)

    save_fig(fig, 'm8_robotic_gripper.png')


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print(f"\nGenerating mechanism diagrams to: {OUT_DIR}\n")
    draw_m1_catapult()
    draw_m2_pulley()
    draw_m3_cam()
    draw_m4_gears()
    draw_m5_crank_cam()
    draw_m6_crane()
    draw_m7_rover()
    draw_m8_gripper()
    print(f"\nAll 8 diagrams generated successfully in: {OUT_DIR}\n")
