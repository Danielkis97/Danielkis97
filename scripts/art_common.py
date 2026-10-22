"""Shared palette and helpers for the hand-made profile SVGs.

Everything here is plain stdlib so the GitHub Action (and anyone cloning
the repo) can rebuild the art with `python scripts/build_art.py`.
"""
import os
from xml.sax.saxutils import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS = os.path.join(ROOT, "assets")

C = {
    "bg": "#05070d",
    "panel": "#0b1020",
    "panel2": "#0f1629",
    "line": "#1e293b",
    "text": "#e2e8f0",
    "muted": "#64748b",
    "dim": "#334155",
    "cyan": "#22d3ee",
    "cyan2": "#67e8f9",
    "violet": "#a78bfa",
    "violet2": "#8b5cf6",
    "pink": "#f472b6",
    "lime": "#a3e635",
    "amber": "#fbbf24",
    "red": "#f87171",
}

MONO = "ui-monospace,SFMono-Regular,'JetBrains Mono','Cascadia Code',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "'Segoe UI',Inter,system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif"

# Stops CSS animations for people who asked their OS for less motion.
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

# Approximate advance of one monospace glyph, as a fraction of font-size.
# Text that must line up gets textLength so the fallback font cannot break it.
MONO_ADV = 0.6


def esc(s):
    return escape(str(s))


def mono_w(text, size):
    return len(text) * size * MONO_ADV


def svg(w, h, body, title, desc="", style="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d">\n'
        f'<title id="t">{esc(title)}</title>\n<desc id="d">{esc(desc)}</desc>\n'
        f"<defs>{defs}</defs>\n"
        f"<style>text{{font-family:{MONO}}} .sans{{font-family:{SANS}}} {style} {REDUCED}</style>\n"
        f"{body}\n</svg>\n"
    )


def frame(w, h, rx=18, stroke_id="frameStroke"):
    """Rounded dark card with a gradient hairline border (looks right in light and dark mode)."""
    return (
        f'<rect width="{w}" height="{h}" rx="{rx}" fill="{C["bg"]}"/>'
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{rx - .75}" fill="none" '
        f'stroke="url(#{stroke_id})" stroke-width="1.5"/>'
    )


def frame_defs(stroke_id="frameStroke"):
    return (
        f'<linearGradient id="{stroke_id}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{C["cyan"]}" stop-opacity=".55"/>'
        f'<stop offset=".5" stop-color="{C["line"]}"/>'
        f'<stop offset="1" stop-color="{C["pink"]}" stop-opacity=".55"/></linearGradient>'
        '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="3" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="7"/></filter>'
    )


def chip(x, y, label, color, size=12, pad=10, h=24, cls=""):
    w = mono_w(label, size) + pad * 2
    return (
        f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" '
        f'fill="{color}" fill-opacity=".1" stroke="{color}" stroke-opacity=".55"/>'
        f'<text x="{x + pad}" y="{y + h / 2 + size * .36:.1f}" font-size="{size}" fill="{color}" '
        f'textLength="{mono_w(label, size):.1f}" lengthAdjust="spacingAndGlyphs">{esc(label)}</text></g>'
    ), w


def write(name, content):
    path = os.path.join(ASSETS, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  wrote assets/{name}  ({len(content) / 1024:.1f} KB)")
