"""Section art: boot terminal, neofetch card, tech-stack orbit, divider and footer."""
import math
import os
import random

from art_common import ASSETS, C, SANS, esc, frame, frame_defs, mono_w, svg

HERE = os.path.dirname(__file__)

# ---------------------------------------------------------------------------
# Boot terminal: the original header, recoloured to the new palette.
# ---------------------------------------------------------------------------
RECOLOR = {
    "#58a6ff": C["cyan"],
    "#79c0ff": C["cyan2"],
    "#1f6feb": C["violet2"],
    "#d2a8ff": C["pink"],
    "#3fb950": C["lime"],
}


RELABEL = {
    "Applied AI · Automation · Digital Products": "GenAI · Automation · Web · Software · Data",
    'class="lbl">vision<': 'class="lbl">data<',
    'class="lbl" style="animation:k16 14s infinite;">AI<': 'class="lbl" style="animation:k16 14s infinite;">genAI<',
    'class="lbl" style="animation:k16 14s infinite;">bots<': 'class="lbl" style="animation:k16 14s infinite;">web<',
    'class="lbl" style="animation:k16 14s infinite;">apps<': 'class="lbl" style="animation:k16 14s infinite;">auto<',
    "Animated terminal that types whoami": "Animated terminal that types whoami (GenAI, automation, web, software, data)",
}


def terminal():
    with open(os.path.join(HERE, "terminal_source.svg"), encoding="utf-8") as f:
        s = f.read()
    for old, new in RECOLOR.items():
        s = s.replace(old, new)
    for old, new in RELABEL.items():
        assert old in s, old
        s = s.replace(old, new)
    return s


# ---------------------------------------------------------------------------
# neofetch card with a pixel-matrix R00T logo.
# ---------------------------------------------------------------------------
GLYPHS = {
    "R": ["1111.", "1...1", "1...1", "1111.", "1.1..", "1..1.", "1...1"],
    "0": [".111.", "1...1", "1..11", "1.1.1", "11..1", "1...1", ".111."],
    "T": ["11111", "..1..", "..1..", "..1..", "..1..", "..1..", "..1.."],
}

NEOFETCH = [
    ("OS", "Human v1.0 · Germany"),
    ("Host", "full-time job + part-time Applied AI studies"),
    ("Kernel", "Python · TypeScript · Solidity"),
    ("Shell", "claude-code · git · terraform · docker"),
    ("Uptime", "on GitHub since Jul 2024"),
    ("Focus", "GenAI · automation · web · data · software"),
    ("Projects", "edge AI · ML in prod · websites · bots · games"),
    ("Mode", "build first -> refine fast -> ship"),
]


def neofetch():
    W, H = 1200, 400
    cell, gap = 13, 3
    step = cell + gap
    lx, ly = 56, 110
    pix, shadow = [], []
    gx = lx
    word = "R00T"
    total_w = len(word) * 5 * step + (len(word) - 1) * step
    for gi, ch in enumerate(word):
        for r, row in enumerate(GLYPHS[ch]):
            for c, bit in enumerate(row):
                if bit != "1":
                    continue
                x, y = gx + c * step, ly + r * step
                t = (x - lx) / total_w
                col = C["cyan"] if t < .33 else C["violet"] if t < .66 else C["pink"]
                delay = (gi * 5 + c + r) * 0.07
                pix.append(f'<rect class="px" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                           f'fill="{col}" style="animation-delay:{delay:.2f}s"/>')
                shadow.append(f'<rect x="{x + 5}" y="{y + 5}" width="{cell}" height="{cell}" rx="2"/>')
        gx += 6 * step

    logo = (f'<g fill="#1e1b4b">{"".join(shadow)}</g><g filter="url(#glow)">{"".join(pix)}</g>'
            f'<text x="{lx}" y="{ly + 7 * step + 40}" font-size="13" fill="{C["muted"]}">'
            f'// pixel-matrix build of <tspan fill="{C["text"]}">R00t</tspan></text>'
            f'<text x="{lx}" y="{ly + 7 * step + 62}" font-size="13" fill="{C["muted"]}">'
            f'// 1 human · 0 cloud deps · 0 excuses</text>')

    ix, iy, lh, fs = 520, 70, 31, 17
    lines = [f'<text x="{ix}" y="{iy}" font-size="{fs + 2}" font-weight="700">'
             f'<tspan fill="{C["cyan"]}">r00t</tspan><tspan fill="{C["muted"]}">@</tspan>'
             f'<tspan fill="{C["pink"]}">danielkis97</tspan></text>',
             f'<rect x="{ix}" y="{iy + 12}" width="{mono_w("r00t@danielkis97", fs + 2):.0f}" height="2" fill="{C["dim"]}"/>']
    for i, (k, v) in enumerate(NEOFETCH):
        y = iy + 44 + i * lh
        lines.append(
            f'<g class="ln" style="animation-delay:{.25 + i * .14:.2f}s">'
            f'<text x="{ix}" y="{y}" font-size="{fs}" font-weight="700" fill="{C["violet"]}">{esc(k)}</text>'
            f'<text x="{ix + 120}" y="{y}" font-size="{fs}" fill="{C["text"]}">{esc(v)}</text></g>')
    by = iy + 44 + len(NEOFETCH) * lh - 8
    swatches = [C["bg"], C["red"], C["lime"], C["amber"], C["cyan"], C["violet"], C["pink"], C["text"]]
    blocks = "".join(
        f'<rect class="sw" x="{ix + i * 38}" y="{by}" width="34" height="18" rx="3" fill="{c}" '
        f'stroke="{C["dim"]}" style="animation-delay:{i * .12:.2f}s"/>' for i, c in enumerate(swatches))
    cursor = (f'<rect class="blink" x="{ix + len(swatches) * 38 + 8}" y="{by}" width="10" height="18" '
              f'fill="{C["cyan"]}"/>')

    style = f"""
.px{{animation:px 3.2s ease-in-out infinite}}
@keyframes px{{0%,100%{{opacity:.35}}25%{{opacity:1}}50%{{opacity:.6}}}}
.ln{{animation:ln .6s cubic-bezier(.2,.8,.2,1) both}}
@keyframes ln{{from{{opacity:0;transform:translateX(-14px)}}to{{opacity:1;transform:none}}}}
.sw{{animation:sw 2.4s ease-in-out infinite}}
@keyframes sw{{0%,60%,100%{{transform:translateY(0)}}30%{{transform:translateY(-6px)}}}}
.blink{{animation:blink 1.05s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
"""
    defs = frame_defs() + (f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
                           f'<circle cx="2" cy="2" r="1" fill="{C["line"]}"/></pattern>')
    body = (frame(W, H) + f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17" fill="url(#dots)" opacity=".7"/>'
            f'<line x1="470" y1="40" x2="470" y2="{H - 40}" stroke="{C["line"]}" stroke-dasharray="3 6"/>'
            + logo + "".join(lines) + blocks + cursor)
    return svg(W, H, body, "neofetch: r00t@danielkis97",
               "A neofetch-style system card: an animated pixel R00T logo next to a spec sheet - "
               + "; ".join(f"{k}: {v}" for k, v in NEOFETCH) + ".", style=style, defs=defs)


# ---------------------------------------------------------------------------
# Tech stack as three tilted orbits; pills ride the ellipses with fake depth.
# ---------------------------------------------------------------------------
RINGS = [
    (200, 64, 24, 1, "cyan", "AI · ML · Data",
     ["Python", "PyTorch", "TensorFlow", "OpenCV", "scikit-learn", "Pandas", "NumPy"]),
    (340, 112, 36, -1, "violet", "Web · Software",
     ["TypeScript", "React", "JavaScript", "Java", "Flask", "HTML/CSS", "Git", "REST APIs"]),
    (490, 166, 52, 1, "pink", "GenAI · Automation · Cloud",
     ["AWS", "Google Cloud", "Terraform", "Docker", "Solidity", "OpenAI", "Claude", "LLM Agents", "Workflows", "Bots"]),
]


def stack():
    W, H, cx, cy = 1200, 520, 600, 286
    rnd = random.Random(42)
    parts, legend = [], []
    for ri, (rx, ry, dur, direction, ckey, label, items) in enumerate(RINGS):
        col = C[ckey]
        path = (f"M{cx},{cy + ry} A{rx},{ry} 0 1 0 {cx},{cy - ry} A{rx},{ry} 0 1 0 {cx},{cy + ry}")
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{col}" '
                     f'stroke-opacity=".28" stroke-dasharray="2 7"/>')
        kp = 'keyPoints="0;1"' if direction > 0 else 'keyPoints="1;0"'
        for i, item in enumerate(items):
            phase = i / len(items)
            begin = f"-{phase * dur:.2f}s"
            fs = 13
            w = mono_w(item, fs) + 26
            depth_t = ("1;.86;.7;.86;1" if direction > 0 else "1;.86;.7;.86;1")
            parts.append(
                f'<g><animateMotion dur="{dur}s" repeatCount="indefinite" begin="{begin}" {kp} '
                f'keyTimes="0;1" calcMode="linear" path="{path}"/>'
                f'<g><animateTransform attributeName="transform" type="scale" dur="{dur}s" begin="{begin}" '
                f'repeatCount="indefinite" values="{depth_t}"/>'
                f'<animate attributeName="opacity" dur="{dur}s" begin="{begin}" repeatCount="indefinite" '
                f'values="1;.7;.35;.7;1"/>'
                f'<rect x="{-w / 2:.1f}" y="-14" width="{w:.1f}" height="28" rx="14" fill="{C["panel"]}" '
                f'stroke="{col}" stroke-opacity=".8"/>'
                f'<text x="0" y="4.6" font-size="{fs}" text-anchor="middle" fill="{col}" '
                f'textLength="{mono_w(item, fs):.1f}" lengthAdjust="spacingAndGlyphs">{esc(item)}</text></g></g>')
        lx, ly = 40, H - 86 + ri * 24
        legend.append(f'<circle cx="{lx + 6}" cy="{ly - 4}" r="5" fill="{col}"/>'
                      f'<text x="{lx + 20}" y="{ly}" font-size="13" fill="{C["muted"]}">'
                      f'<tspan fill="{col}">ring {ri + 1}</tspan>  {esc(label)}</text>')

    sparks = "".join(
        f'<circle class="sp" cx="{rnd.uniform(30, W - 30):.0f}" cy="{rnd.uniform(60, H - 30):.0f}" '
        f'r="{rnd.choice([.8, 1.1, 1.5])}" fill="{C[rnd.choice(["cyan", "violet", "pink"])]}" '
        f'style="animation-delay:-{rnd.uniform(0, 5):.2f}s"/>' for _ in range(46))

    core = (f'<circle cx="{cx}" cy="{cy}" r="70" fill="{C["violet2"]}" opacity=".35" filter="url(#softglow)" class="breathe"/>'
            f'<circle cx="{cx}" cy="{cy}" r="46" fill="url(#coreg)" stroke="{C["cyan"]}" stroke-opacity=".7"/>'
            f'<circle cx="{cx}" cy="{cy}" r="56" fill="none" stroke="{C["cyan"]}" stroke-width="1.5" '
            f'stroke-dasharray="10 8 2 8" stroke-opacity=".8">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" '
            f'dur="14s" repeatCount="indefinite"/></circle>'
            f'<text x="{cx}" y="{cy + 3}" text-anchor="middle" font-size="20" font-weight="700" fill="#fff">R00t</text>'
            f'<text x="{cx}" y="{cy + 21}" text-anchor="middle" font-size="10" fill="{C["cyan2"]}">core.v1</text>')

    header = (f'<text x="40" y="48" font-size="15" fill="{C["muted"]}"><tspan fill="{C["lime"]}">$</tspan> '
              f'ls ~/stack <tspan fill="{C["dim"]}">--orbit --live</tspan></text>'
              f'<text x="{W - 40}" y="48" font-size="13" fill="{C["muted"]}" text-anchor="end">'
              f'3 rings · {sum(len(r[6]) for r in RINGS)} tools · 0 regrets</text>')

    defs = frame_defs() + (f'<radialGradient id="coreg" cx=".35" cy=".35"><stop offset="0" stop-color="#2b1a5e"/>'
                           f'<stop offset="1" stop-color="{C["bg"]}"/></radialGradient>')
    style = """
.sp{animation:tw 5s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.1}50%{opacity:.9}}
.breathe{animation:br 4s ease-in-out infinite}
@keyframes br{0%,100%{opacity:.25}50%{opacity:.5}}
"""
    body = frame(W, H) + sparks + header + "".join(parts) + core + "".join(legend)
    return svg(W, H, body, "Tech stack orbit",
               "Three tilted orbits of tools circling a core labelled R00t: "
               + "; ".join(f"{r[5]}: " + ", ".join(r[6]) for r in RINGS) + ".", style=style, defs=defs)


# ---------------------------------------------------------------------------
# Divider and footer
# ---------------------------------------------------------------------------
def divider():
    W, H = 1200, 24
    defs = (f'<linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{C["cyan"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{C["cyan"]}"/><stop offset=".75" stop-color="{C["pink"]}"/>'
            f'<stop offset="1" stop-color="{C["pink"]}" stop-opacity="0"/></linearGradient>')
    style = (".beam{animation:beam 4.5s cubic-bezier(.6,0,.4,1) infinite}"
             "@keyframes beam{0%{transform:translateX(-320px)}100%{transform:translateX(1200px)}}"
             ".dia{transform-box:fill-box;transform-origin:center;animation:spin 6s linear infinite}"
             "@keyframes spin{to{transform:rotate(360deg)}}")
    body = (f'<line x1="0" x2="{W}" y1="12" y2="12" stroke="{C["line"]}" stroke-width="2"/>'
            f'<rect class="beam" x="0" y="10.5" width="320" height="3" rx="1.5" fill="url(#beam)"/>'
            f'<rect x="590" y="2" width="20" height="20" fill="{C["bg"]}"/>'
            f'<rect class="dia" x="594" y="6" width="12" height="12" fill="none" stroke="{C["violet"]}" stroke-width="2"/>')
    return svg(W, H, body, "divider", "An animated neon divider line.", style=style, defs=defs)


def _typing(n, cw, dur=8.0):
    """Discrete SMIL width steps: type, hold, wipe."""
    ev = [(0, 0)] + [(0.4 + k * 0.07, k * cw) for k in range(1, n + 1)] + [(dur - 0.6, 0)]
    vals = ";".join(f"{v:.1f}" for _, v in ev)
    keys = ";".join(f"{t / dur:.4f}" for t, _ in ev)
    return (f'<animate attributeName="width" dur="{dur}s" repeatCount="indefinite" calcMode="discrete" '
            f'values="{vals}" keyTimes="{keys}"/>')


def footer():
    W, H = 1200, 210

    def wave(amp, period, y0):
        pts = []
        for x in range(-period, W + period * 2, 8):
            pts.append(f"{x},{y0 + amp * math.sin(2 * math.pi * x / period):.1f}")
        return "M" + " L".join(pts)

    waves = ""
    for i, (amp, period, y0, col, dur, op) in enumerate([
        (10, 240, 160, C["cyan"], 7, .7), (14, 320, 170, C["violet"], 11, .55), (8, 180, 182, C["pink"], 5, .6)]):
        waves += (f'<path d="{wave(amp, period, y0)}" fill="none" stroke="{col}" stroke-width="2" '
                  f'stroke-opacity="{op}" filter="url(#glow)" style="animation:wv{i} {dur}s linear infinite"/>')
    style = "".join(f"@keyframes wv{i}{{to{{transform:translateX(-{p}px)}}}}" for i, p in enumerate([240, 320, 180]))
    msg = "thanks for scrolling. now go build something."
    style += f"""
.blink{{animation:blink 1.05s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
"""
    tx = (W - mono_w("$ " + msg, 22)) / 2
    defs = frame_defs() + (f'<clipPath id="typed"><rect x="{tx + mono_w("$ ", 22):.1f}" y="40" width="0" height="40">'
                           f'{_typing(len(msg), mono_w(msg, 22) / len(msg))}</rect></clipPath>')
    body = (frame(W, H)
            + f'<g clip-path="url(#clipall)">{waves}</g>'
            + f'<text x="{tx:.1f}" y="70" font-size="22" fill="{C["lime"]}">$</text>'
            + f'<text x="{tx + mono_w("$ ", 22):.1f}" y="70" font-size="22" fill="{C["text"]}" clip-path="url(#typed)" '
              f'textLength="{mono_w(msg, 22):.1f}" lengthAdjust="spacingAndGlyphs">{esc(msg)}</text>'
            + f'<text x="{W / 2}" y="104" font-size="13" fill="{C["muted"]}" text-anchor="middle">'
              f'// R00t · Danielkis97 · hand-made SVG, zero frameworks harmed · exit 0'
              f'<tspan class="blink" fill="{C["cyan"]}"> _</tspan></text>')
    defs += f'<clipPath id="clipall"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17"/></clipPath>'
    return svg(W, H, body, "exit 0", "Footer with a typed sign-off over three neon sine waves.",
               style=style, defs=defs)
