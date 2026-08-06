#!/usr/bin/env python3
"""Generate a clean SVG thumbnail for any part that does not already have a real
photo, so the catalogue never shows a blank tile.

We deliberately do NOT hotlink marketplace images - AliExpress and eBay listing
images rot within months and would leave dead tiles across the whole site.
Drop a real photo into assets/parts/<id>.png|jpg|webp and point `image:` at it
to override; this script never overwrites a non-SVG file.

Run:  python scripts/gen_thumbnails.py
"""
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, "parts")
OUT = os.path.join(ROOT, "assets", "parts")

# Per-category colour + a simple geometric motif. Muted enough to sit behind
# the part name without fighting it.
STYLE = {
    "Air quality & CO2":        ("#4f9b6f", "#232a26", "waves"),
    "Substrate sensing":        ("#9a8355", "#2a2620", "probe"),
    "Water & fertigation":      ("#4d8b9c", "#212a2d", "drop"),
    "Thermal & optical":        ("#a86a58", "#2c2320", "grid"),
    "Light measurement":        ("#a8863c", "#2b2822", "rays"),
    "Controllers & boards":     ("#77839c", "#242528", "chip"),
    "Networking & power":       ("#6a8a94", "#22272a", "chip"),
    "Actuation & relays":       ("#9c6a80", "#2a2326", "relay"),
    "Access control & presence": ("#8a7a9c", "#262428", "wave-arc"),
    "Displays & HMI":           ("#6a9c8e", "#222826", "screen"),
    "Bus infrastructure":       ("#8d8d63", "#282720", "bus"),
    "Irrigation hardware":      ("#5f9b78", "#222823", "drop"),
    "Energy monitoring":        ("#9c8d5f", "#2a2822", "bolt"),
    "Climate control":          ("#7a9cae", "#24272b", "waves"),
    "Gas & leak detection":     ("#b0895c", "#2c2822", "waves"),
}
DEFAULT = ("#8a8880", "#262624", "chip")

TIER_BADGE = {
    "field-proven": "#4f9b6f",
    "works":        "#4d8b9c",
    "experimental": "#a8863c",
    "avoid":        "#a85a54",
}


def motif(kind, accent):
    """A small, abstract glyph. Intentionally not a fake product render."""
    a = accent
    if kind == "waves":
        return (f'<path d="M40 96 q22-20 44 0 t44 0 t44 0" stroke="{a}" stroke-width="5" fill="none" opacity=".55"/>'
                f'<path d="M40 122 q22-20 44 0 t44 0 t44 0" stroke="{a}" stroke-width="5" fill="none" opacity=".3"/>')
    if kind == "probe":
        return (f'<rect x="98" y="52" width="20" height="64" rx="4" fill="{a}" opacity=".6"/>'
                f'<path d="M108 116 l14 30 h-28 z" fill="{a}" opacity=".75"/>'
                f'<path d="M60 140 h96" stroke="{a}" stroke-width="4" opacity=".35"/>')
    if kind == "drop":
        return f'<path d="M108 56 c26 34 34 46 34 60 a34 34 0 0 1-68 0 c0-14 8-26 34-60z" fill="{a}" opacity=".6"/>'
    if kind == "grid":
        cells = "".join(
            f'<rect x="{62+ (i%6)*16}" y="{62+(i//6)*16}" width="13" height="13" rx="2" '
            f'fill="{a}" opacity="{0.18 + ((i*37) % 60)/100:.2f}"/>'
            for i in range(36))
        return cells
    if kind == "rays":
        return "".join(
            f'<path d="M108 104 l{44*__import__("math").cos(i*3.14159/4):.1f} '
            f'{44*__import__("math").sin(i*3.14159/4):.1f}" stroke="{a}" stroke-width="5" '
            f'stroke-linecap="round" opacity=".5"/>' for i in range(8)
        ) + f'<circle cx="108" cy="104" r="15" fill="{a}" opacity=".7"/>'
    if kind == "relay":
        return (f'<rect x="62" y="72" width="92" height="60" rx="6" stroke="{a}" stroke-width="4" fill="none" opacity=".6"/>'
                f'<path d="M78 102 h26 l14-16 v32 l14-16 h26" stroke="{a}" stroke-width="5" fill="none" opacity=".8"/>')
    if kind == "screen":
        return (f'<rect x="60" y="64" width="96" height="72" rx="6" stroke="{a}" stroke-width="4" fill="none" opacity=".65"/>'
                f'<rect x="72" y="76" width="72" height="30" rx="3" fill="{a}" opacity=".35"/>'
                f'<rect x="72" y="114" width="44" height="8" rx="4" fill="{a}" opacity=".5"/>')
    if kind == "bus":
        return (f'<path d="M52 84 h112 M52 104 h112 M52 124 h112" stroke="{a}" stroke-width="4" opacity=".45"/>'
                + "".join(f'<circle cx="{72+i*24}" cy="{84+(i%3)*20}" r="6" fill="{a}" opacity=".8"/>' for i in range(5)))
    if kind == "bolt":
        return f'<path d="M116 56 l-30 54 h22 l-8 44 l34-58 h-22 z" fill="{a}" opacity=".7"/>'
    if kind == "wave-arc":
        return "".join(
            f'<path d="M84 104 a{18+i*14} {18+i*14} 0 0 1 {18+i*14} -{18+i*14}" '
            f'stroke="{a}" stroke-width="5" fill="none" opacity="{0.7-i*0.18:.2f}"/>' for i in range(3))
    # chip
    pins = "".join(
        f'<rect x="{56+i*18}" y="56" width="8" height="10" fill="{a}" opacity=".55"/>'
        f'<rect x="{56+i*18}" y="142" width="8" height="10" fill="{a}" opacity=".55"/>' for i in range(6))
    return (f'<rect x="66" y="66" width="84" height="76" rx="8" stroke="{a}" stroke-width="4" fill="none" opacity=".7"/>'
            f'<circle cx="80" cy="80" r="5" fill="{a}" opacity=".8"/>' + pins)


def wrap(text, width, max_lines):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and len(" ".join(lines)) < len(text):
        lines[-1] = lines[-1][: width - 1].rstrip() + "…"
    return lines


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build(part):
    accent, bg, kind = STYLE.get(part.get("category"), DEFAULT)
    tier = part.get("quality_tier", "works")
    badge = TIER_BADGE.get(tier, "#666")
    lines = wrap(part.get("name", part["id"]), 26, 3)
    label = "".join(
        f'<text x="108" y="{182 + i*19}" text-anchor="middle" font-size="14" '
        f'fill="#c9c6bd" font-family="ui-sans-serif,system-ui,sans-serif">{esc(l)}</text>'
        for i, l in enumerate(lines))
    maker = esc((part.get("manufacturer") or "")[:30])
    maker_el = (f'<text x="108" y="{182 + len(lines)*19 + 4}" text-anchor="middle" font-size="11" '
                f'fill="#908d85" font-family="ui-sans-serif,system-ui,sans-serif">{maker}</text>'
                if maker else "")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 216 260" width="216" height="260" role="img" aria-label="{esc(part.get('name', part['id']))}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{bg}"/>
      <stop offset="1" stop-color="#1a1918"/>
    </linearGradient>
  </defs>
  <rect width="216" height="260" rx="12" fill="url(#g)"/>
  <rect x="28" y="36" width="160" height="136" rx="10" fill="#000" opacity=".22"/>
  {motif(kind, accent)}
  <rect x="12" y="12" width="52" height="8" rx="4" fill="{badge}" opacity=".9"/>
  {label}{maker_el}
</svg>
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    made = skipped = 0
    for name in sorted(os.listdir(PARTS)):
        if not name.endswith((".yaml", ".yml")):
            continue
        part = yaml.safe_load(open(os.path.join(PARTS, name), encoding="utf-8"))
        img = part.get("image") or f"assets/parts/{part['id']}.svg"
        dest = os.path.join(ROOT, img)
        # Never clobber a real photo a contributor has added.
        if os.path.isfile(dest) and not dest.endswith(".svg"):
            skipped += 1
            continue
        if not dest.endswith(".svg"):
            dest = os.path.join(OUT, part["id"] + ".svg")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(build(part))
        made += 1
    print(f"thumbnails written: {made}, real photos left alone: {skipped}")


if __name__ == "__main__":
    main()
