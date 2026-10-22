"""Embed the Platane/snk animation into our own cards (used by stats.py)."""
import re

from art_common import C


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


def nest(raw, x, y, width):
    """Return (svg_markup, height) placing the snk drawing at (x, y) scaled to `width`."""
    raw = re.sub(r"<\?xml[^>]*\?>", "", raw).strip()
    m = re.match(r"<svg\b([^>]*)>", raw)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', m.group(1)).group(1).split()]
    height = width * vb[3] / vb[2]
    attrs = re.sub(r'\s(width|height|x|y)="[^"]*"', "", m.group(1))
    return (f'<svg x="{x}" y="{y}" width="{width}" height="{height:.1f}"{attrs}>'
            + _arena(raw[m.end():])), height
