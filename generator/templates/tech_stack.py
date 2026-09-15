"""SVG template: Currently Building + Focus Sectors."""

import math

from generator.utils import esc, svg_arc_path, resolve_arm_colors


WIDTH = 850
HEIGHT = 240


def _build_currently_building(theme):
    """Build the left side of the card."""

    cyan = theme.get("synapse_cyan", "#00d4ff")
    violet = theme.get("dendrite_violet", "#a78bfa")
    amber = theme.get("axon_amber", "#ffb020")
    text_dim = theme.get("text_dim", "#94a3b8")
    text_faint = theme.get("text_faint", "#64748b")

    return f'''
  <!-- Left: Currently Building -->

  <text x="30" y="38"
        fill="{text_faint}"
        font-size="11"
        font-family="monospace"
        letter-spacing="3">
    CURRENTLY BUILDING
  </text>

  <!-- Data Science -->
  <circle cx="35" cy="75" r="4"
          fill="{violet}">
    <animate
      attributeName="opacity"
      values="0.35;1;0.35"
      dur="2s"
      repeatCount="indefinite"/>
  </circle>

  <text x="52" y="72"
        fill="{violet}"
        font-size="11"
        font-family="monospace">
    DATA SCIENCE
  </text>

  <text x="52" y="89"
        fill="{text_dim}"
        font-size="9"
        font-family="monospace">
    Exploring data and finding insights
  </text>


  <!-- Machine Learning -->
  <circle cx="35" cy="120" r="4"
          fill="{cyan}">
    <animate
      attributeName="opacity"
      values="0.35;1;0.35"
      dur="2.5s"
      repeatCount="indefinite"/>
  </circle>

  <text x="52" y="117"
        fill="{cyan}"
        font-size="11"
        font-family="monospace">
    MACHINE LEARNING
  </text>

  <text x="52" y="134"
        fill="{text_dim}"
        font-size="9"
        font-family="monospace">
    Training and evaluating models
  </text>


  <!-- AI Projects -->
  <circle cx="35" cy="165" r="4"
          fill="{amber}">
    <animate
      attributeName="opacity"
      values="0.35;1;0.35"
      dur="3s"
      repeatCount="indefinite"/>
  </circle>

  <text x="52" y="162"
        fill="{amber}"
        font-size="11"
        font-family="monospace">
    AI PROJECTS
  </text>

  <text x="52" y="179"
        fill="{text_dim}"
        font-size="9"
        font-family="monospace">
    Learning by building
  </text>


  <!-- Status -->
  <text x="30" y="215"
        fill="{text_faint}"
        font-size="8"
        font-family="monospace"
        letter-spacing="1">
    STATUS: LEARNING • BUILDING • EXPLORING
  </text>
'''


def _build_radar_grid(rcx, rcy, grid_rings, theme):
    parts = []

    for ring_r in grid_rings:
        parts.append(
            f'    <circle cx="{rcx}" cy="{rcy}" r="{ring_r}" '
            f'fill="none" stroke="{theme["text_faint"]}" '
            f'stroke-width="0.5" stroke-dasharray="3,3" opacity="0.25"/>'
        )

    return "\n".join(parts)


def _build_radar_sectors(sector_data, rcx, rcy, radius, theme):
    parts = []

    # Sector arcs
    for sec in sector_data:
        d = svg_arc_path(
            rcx,
            rcy,
            radius,
            sec["start_deg"],
            sec["end_deg"],
        )

        parts.append(
            f'    <path d="{d}" '
            f'fill="{sec["color"]}" '
            f'fill-opacity="0.10" '
            f'stroke="{sec["color"]}" '
            f'stroke-opacity="0.3" '
            f'stroke-width="0.5"/>'
        )

    # Boundary lines
    for i in range(len(sector_data)):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg - 90)

        lx = rcx + radius * math.cos(angle_rad)
        ly = rcy + radius * math.sin(angle_rad)

        parts.append(
            f'    <line x1="{rcx}" y1="{rcy}" '
            f'x2="{lx:.1f}" y2="{ly:.1f}" '
            f'stroke="{theme["text_faint"]}" '
            f'stroke-width="0.5" opacity="0.3"/>'
        )

    return "\n".join(parts)


def _build_radar_needle(rcx, rcy, radius, theme):

    scan_color = theme.get(
        "synapse_cyan",
        "#00d4ff",
    )

    tip_x = rcx
    tip_y = rcy - radius

    sweep_d = svg_arc_path(
        rcx,
        rcy,
        radius,
        330,
        360,
    )

    outer_hw = 2.5
    inner_hw = 0.8

    return (
        f'    <g>'
        f'\n      <!-- Sweep trail -->'
        f'\n      <path d="{sweep_d}" '
        f'fill="{scan_color}" fill-opacity="0.07"/>'
        f'\n      <!-- Outer wedge -->'
        f'\n      <polygon '
        f'points="{rcx - outer_hw},{rcy} '
        f'{tip_x},{tip_y} '
        f'{rcx + outer_hw},{rcy}" '
        f'fill="{scan_color}" opacity="0.25"/>'
        f'\n      <!-- Inner bright core -->'
        f'\n      <polygon '
        f'points="{rcx - inner_hw},{rcy} '
        f'{tip_x},{tip_y} '
        f'{rcx + inner_hw},{rcy}" '
        f'fill="{scan_color}" opacity="0.5"/>'
        f'\n      <!-- Tip glow -->'
        f'\n      <circle cx="{tip_x}" cy="{tip_y}" '
        f'r="2" fill="{scan_color}" opacity="0.6">'
        f'\n        <animate '
        f'attributeName="opacity" '
        f'values="0.4;0.8;0.4" '
        f'dur="2s" '
        f'repeatCount="indefinite"/>'
        f'\n      </circle>'
        f'\n      <animateTransform '
        f'attributeName="transform" '
        f'type="rotate" '
        f'from="0 {rcx} {rcy}" '
        f'to="360 {rcx} {rcy}" '
        f'dur="8s" '
        f'repeatCount="indefinite"/>'
        f'\n    </g>'
    )


def _build_radar_labels_and_dots(
    sector_data,
    galaxy_arms,
    rcx,
    rcy,
    radius,
    theme,
):

    parts = []

    # Labels
    for sec in sector_data:

        mid_deg = (
            sec["start_deg"] +
            sec["end_deg"]
        ) / 2

        mid_rad = math.radians(
            mid_deg - 90
        )

        label_r = radius + 18

        lx = (
            rcx +
            label_r *
            math.cos(mid_rad)
        )

        ly = (
            rcy +
            label_r *
            math.sin(mid_rad)
        )

        if abs(lx - rcx) < 5:
            anchor = "middle"
        elif lx > rcx:
            anchor = "start"
        else:
            anchor = "end"

        parts.append(
            f'    <text x="{lx:.1f}" '
            f'y="{ly:.1f}" '
            f'fill="{sec["color"]}" '
            f'font-size="9" '
            f'font-family="monospace" '
            f'text-anchor="{anchor}" '
            f'dominant-baseline="middle">'
            f'{esc(sec["name"])}</text>'
        )

        count_y = ly + 12

        parts.append(
            f'    <text x="{lx:.1f}" '
            f'y="{count_y:.1f}" '
            f'fill="{theme["text_faint"]}" '
            f'font-size="8" '
            f'font-family="monospace" '
            f'text-anchor="{anchor}" '
            f'dominant-baseline="middle">'
            f'({sec["items"]})</text>'
        )

    # Animated dots
    radii_cycle = [24, 40, 56]

    for sec_i, sec in enumerate(sector_data):

        arm = galaxy_arms[sec_i]
        items = arm.get("items", [])
        item_count = len(items)

        edge_pad = 10

        for j, item in enumerate(items):

            usable_start = (
                sec["start_deg"] +
                edge_pad
            )

            usable_end = (
                sec["end_deg"] -
                edge_pad
            )

            if item_count == 1:
                item_angle = (
                    usable_start +
                    usable_end
                ) / 2
            else:
                item_angle = (
                    usable_start +
                    (
                        usable_end -
                        usable_start
                    ) *
                    j /
                    (item_count - 1)
                )

            item_rad = math.radians(
                item_angle - 90
            )

            dot_r = radii_cycle[
                j % 3
            ]

            dx = (
                rcx +
                dot_r *
                math.cos(item_rad)
            )

            dy = (
                rcy +
                dot_r *
                math.sin(item_rad)
            )

            pulse_begin = (
                item_angle / 360
            ) * 8 - 0.3

            if pulse_begin < 0:
                pulse_begin += 8

            parts.append(
                f'    <circle '
                f'cx="{dx:.1f}" '
                f'cy="{dy:.1f}" '
                f'r="3" '
                f'fill="{sec["color"]}" '
                f'opacity="0.35">'
                f'\n      <animate '
                f'attributeName="opacity" '
                f'values="0.35;0.35;1.0;0.35;0.35" '
                f'keyTimes="0;0.04;0.06;0.10;1" '
                f'dur="8s" '
                f'begin="{pulse_begin:.2f}s" '
                f'repeatCount="indefinite"/>'
                f'\n    </circle>'
            )

    return "\n".join(parts)


def render(
    languages: dict,
    galaxy_arms: list,
    theme: dict,
    exclude: list,
    max_display: int,
) -> str:

    # Language telemetry has been intentionally removed.
    # The left side now shows static profile information.

    all_arm_colors = resolve_arm_colors(
        galaxy_arms,
        theme,
    )

    sector_data = []

    for i, arm in enumerate(galaxy_arms):

        color = all_arm_colors[i]

        items = arm.get(
            "items",
            [],
        )

        sector_data.append(
            {
                "name": arm["name"],
                "color": color,
                "items": len(items),
                "start_deg": i * 120 + 1,
                "end_deg": (i + 1) * 120 - 1,
            }
        )

    # Radar geometry
    radius = 65
    rcx = 637
    rcy = 140

    grid_rings = [
        22,
        44,
        65,
    ]

    radar_parts = []

    radar_parts.append(
        _build_radar_grid(
            rcx,
            rcy,
            grid_rings,
            theme,
        )
    )

    radar_parts.append(
        _build_radar_sectors(
            sector_data,
            rcx,
            rcy,
            radius,
            theme,
        )
    )

    radar_parts.append(
        _build_radar_needle(
            rcx,
            rcy,
            radius,
            theme,
        )
    )

    radar_parts.append(
        _build_radar_labels_and_dots(
            sector_data,
            galaxy_arms,
            rcx,
            rcy,
            radius,
            theme,
        )
    )

    radar_str = "\n".join(
        radar_parts
    )

    return f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}">

  <defs/>

  <!-- Card background -->
  <rect
    x="0.5"
    y="0.5"
    width="{WIDTH - 1}"
    height="{HEIGHT - 1}"
    rx="12"
    ry="12"
    fill="{theme["nebula"]}"
    stroke="{theme["star_dust"]}"
    stroke-width="1"/>

  <!-- Left: Currently Building -->
  {_build_currently_building(theme)}

  <!-- Vertical divider -->
  <line
    x1="425"
    y1="25"
    x2="425"
    y2="215"
    stroke="{theme["star_dust"]}"
    stroke-width="1"
    opacity="0.4"/>

  <!-- Right: Focus Sectors -->
  <text
    x="460"
    y="38"
    fill="{theme["text_faint"]}"
    font-size="11"
    font-family="monospace"
    letter-spacing="3">
    FOCUS SECTORS
  </text>

{radar_str}

</svg>'''
