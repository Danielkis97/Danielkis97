"""Wrap the Platane/snk output in a framed card that matches the rest of the profile.

Usage: python scripts/snake_card.py dist/snake-dark.svg  ->  assets/generated/snake.svg
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from art_common import C, frame, frame_defs, svg, write  # noqa: E402

W, PAD, TOP, BOTTOM = 1200, 40, 70, 28


def wrap(raw):
    raw = re.sub(r"<\?xml[^>]*\?>", "", raw).strip()
    m = re.match(r"<svg\b([^>]*)>", raw)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', m.group(1)).group(1).split()]
    inner_w = W - 2 * PAD
    inner_h = inner_w * vb[3] / vb[2]
    H = round(TOP + inner_h + BOTTOM)
    attrs = re.sub(r'\s(width|height|x|y)="[^"]*"', "", m.group(1))
    nested = (f'<svg x="{PAD}" y="{TOP}" width="{inner_w}" height="{inner_h:.1f}"{attrs}>'
              + raw[m.end():])
    header = (f'<text x="{PAD}" y="44" font-size="15" fill="{C["muted"]}"><tspan fill="{C["lime"]}">$</tspan> '
              f'./snake <tspan fill="{C["dim"]}">--feed contributions --daily</tspan></text>'
              f'<text x="{W - PAD}" y="44" font-size="12" fill="{C["dim"]}" text-anchor="end">'
              f'every square = a day I shipped something</text>')
    return svg(W, H, frame(W, H) + header + nested, "Contribution snake",
               "A neon snake eats the last year of contributions, regenerated daily.", defs=frame_defs())


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        write("generated/snake.svg", wrap(f.read()))
