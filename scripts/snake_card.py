"""Wrap the Platane/snk output in a framed card that matches the rest of the profile.

Usage: python scripts/snake_card.py dist/snake-dark.svg  ->  assets/generated/snake.svg
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from art_common import C, frame, frame_defs, svg, write  # noqa: E402

W, PAD, TOP, BOTTOM = 1200, 40, 70, 28


def _arena(inner):
    """snk turns the snake one row above/below the grid; draw that track so it never looks off-board."""
    xs = sorted({int(x) for x in re.findall(r'<rect class="c[^"]*" x="(-?\d+)"', inner)})
    ys = sorted({int(y) for y in re.findall(r'<rect class="c[^"]*" x="-?\d+" y="(-?\d+)"', inner)})
    if not xs or not ys:
        return inner
    step = ys[1] - ys[0] if len(ys) > 1 else 16
    top, bottom = ys[0] - step, ys[-1] + step
    arena = (f'<rect x="{xs[0] - 6}" y="{top - 6}" width="{xs[-1] - xs[0] + 24}" height="{bottom - top + 24}" '
             f'rx="8" fill="{C["panel"]}" stroke="{C["line"]}"/>')
    ghosts = "".join(f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="{C["panel2"]}" '
                     f'stroke="{C["line"]}" stroke-dasharray="2 2"/>' for y in (top, bottom) for x in xs)
    i = inner.index("</style>") + len("</style>")
    return inner[:i] + arena + ghosts + inner[i:]


def wrap(raw):
    raw = re.sub(r"<\?xml[^>]*\?>", "", raw).strip()
    m = re.match(r"<svg\b([^>]*)>", raw)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', m.group(1)).group(1).split()]
    inner_w = W - 2 * PAD
    inner_h = inner_w * vb[3] / vb[2]
    H = round(TOP + inner_h + BOTTOM)
    attrs = re.sub(r'\s(width|height|x|y)="[^"]*"', "", m.group(1))
    nested = (f'<svg x="{PAD}" y="{TOP}" width="{inner_w}" height="{inner_h:.1f}"{attrs}>'
              + _arena(raw[m.end():]))
    header = (f'<text x="{PAD}" y="44" font-size="15" fill="{C["muted"]}"><tspan fill="{C["lime"]}">$</tspan> '
              f'./snake <tspan fill="{C["dim"]}">--feed contributions --daily</tspan></text>'
              f'<text x="{W - PAD}" y="44" font-size="12" fill="{C["dim"]}" text-anchor="end">'
              f'every square = a day I shipped something</text>')
    return svg(W, H, frame(W, H) + header + nested, "Contribution snake",
               "A neon snake eats the last year of contributions, regenerated daily.", defs=frame_defs())


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        write("generated/snake.svg", wrap(f.read()))
