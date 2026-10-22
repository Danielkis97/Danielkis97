"""Hero banner: glitching name, typed role ticker, synthwave sun and an endless perspective grid."""
import random

from art_common import C, MONO, SANS, chip, esc, frame, frame_defs, mono_w, svg

W, H, HZ = 1200, 460, 322  # HZ = horizon line

ROLES = [
    "Applied & Generative AI",
    "Automation Engineer",
    "Web Developer",
    "Software Developer",
    "Data Analyst",
    "Bot Builder",
    "Idea -> Product Shipper",
]
ROLE_SIZE = 26
ROLE_X = 100
ROLE_Y = 254
SLOT = 4.6  # seconds each role owns
TYPE_STEP, ERASE_STEP = 0.065, 0.025


def _role_timelines():
    total = SLOT * len(ROLES)
    cw = ROLE_SIZE * 0.6
    per_role, cursor = [], [(0.0, 0.0)]
    for i, role in enumerate(ROLES):
        t0, n = i * SLOT, len(role)
        ev = [(0.0, 0.0)] if i else []
        ev += [(t0 + k * TYPE_STEP + 0.15, k * cw) for k in range(1, n + 1)]
        erase0 = t0 + SLOT - 0.35 - n * ERASE_STEP
        ev += [(erase0 + k * ERASE_STEP, (n - k) * cw) for k in range(1, n + 1)]
        if i == 0:
            ev = [(0.0, 0.0)] + ev
        per_role.append(ev)
        cursor += [e for e in ev if e[0] > 0]
    return total, per_role, cursor


def _discrete(attr, events, total, offset=0.0):
    vals = ";".join(f"{offset + v:.1f}" for _, v in events)
    keys = ";".join(f"{t / total:.4f}" for t, _ in events)
    return (f'<animate attributeName="{attr}" dur="{total:.1f}s" repeatCount="indefinite" '
            f'calcMode="discrete" values="{vals}" keyTimes="{keys}"/>')


def _floor_keyframes(n=12):
    # Screen-space y of a ground line sliding from depth z=10 to z=1.
    steps = []
    for k in range(n + 1):
        t = k / n
        z = 10 - 9 * t
        y = (H - HZ) * (1 / z - 0.1) / 0.9
        op = 0.08 + 0.92 * t
        steps.append(f"{t * 100:.1f}%{{transform:translateY({y:.1f}px);opacity:{op:.2f}}}")
    return "@keyframes floor{" + "".join(steps) + "}"


def build():
    rnd = random.Random(1997)
    total, role_ev, cursor_ev = _role_timelines()

    defs = frame_defs() + f"""
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{C['bg']}"/><stop offset=".62" stop-color="#0d0a24"/><stop offset=".7" stop-color="#1c0f3a"/>
  <stop offset=".7" stop-color="#0a0718"/><stop offset="1" stop-color="{C['bg']}"/></linearGradient>
<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{C['amber']}"/><stop offset=".5" stop-color="{C['pink']}"/><stop offset="1" stop-color="{C['violet2']}"/></linearGradient>
<linearGradient id="nameFill" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#e0f7ff"/><stop offset="1" stop-color="{C['cyan2']}"/></linearGradient>
<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="floorg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c0f3a"/><stop offset="1" stop-color="{C['bg']}"/></linearGradient>
<pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity=".28"/></pattern>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<clipPath id="sky-clip"><rect width="{W}" height="{HZ}"/></clipPath>
<clipPath id="floor-clip"><rect y="{HZ}" width="{W}" height="{H - HZ}"/></clipPath>
<mask id="sunMask"><rect width="{W}" height="{H}" fill="#fff"/>
  <g class="stripes">{''.join(f'<rect x="700" y="{236 + i * 11}" width="460" height="{1.2 + i * 0.95:.2f}" fill="#000"/>' for i in range(9))}</g></mask>
<clipPath id="slice"><rect x="0" y="0" width="{W}" height="0">
  <animate attributeName="y" dur="5s" repeatCount="indefinite" calcMode="discrete" values="150;150;118;176;140;150" keyTimes="0;.86;.885;.91;.94;.97"/>
  <animate attributeName="height" dur="5s" repeatCount="indefinite" calcMode="discrete" values="0;16;9;22;12;0" keyTimes="0;.86;.885;.91;.94;.97"/></rect></clipPath>
""" + "".join(
        f'<clipPath id="role{i}"><rect x="{ROLE_X}" y="{ROLE_Y - 28}" width="0" height="38">'
        f'{_discrete("width", ev, total)}</rect></clipPath>' for i, ev in enumerate(role_ev))

    style = _floor_keyframes() + f"""
.st{{animation:tw 4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:1}}}}
.fl{{animation:floor 2.4s linear infinite}}
.stripes{{animation:sunstripe 1.6s linear infinite}}
@keyframes sunstripe{{to{{transform:translateY(11px)}}}}
.sweep{{animation:sweep 7s linear infinite}}
@keyframes sweep{{0%{{transform:translateY(-120px)}}100%{{transform:translateY({H + 40}px)}}}}
.nm{{font-family:{SANS};font-weight:900;font-size:132px;letter-spacing:6px}}
.g1{{animation:g1 5s steps(1) infinite}} .g2{{animation:g2 5s steps(1) infinite}} .gs{{transform:translateX(16px)}}
@keyframes g1{{0%,85%{{transform:translate(-3px,0)}}87%{{transform:translate(-11px,2px)}}89%{{transform:translate(8px,-2px)}}92%{{transform:translate(-5px,1px)}}95%{{transform:translate(12px,0)}}97%,100%{{transform:translate(-3px,0)}}}}
@keyframes g2{{0%,85%{{transform:translate(3px,0)}}87%{{transform:translate(10px,-2px)}}89%{{transform:translate(-9px,2px)}}92%{{transform:translate(6px,0)}}95%{{transform:translate(-12px,1px)}}97%,100%{{transform:translate(3px,0)}}}}
.blink{{animation:blink 1.05s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.pulse{{animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
.sunglow{{animation:breathe 5s ease-in-out infinite}}
@keyframes breathe{{0%,100%{{opacity:.55}}50%{{opacity:.85}}}}
.chipin{{animation:chipin .8s cubic-bezier(.2,.8,.2,1) both}}
@keyframes chipin{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
"""

    stars = "".join(
        f'<circle class="st" cx="{rnd.uniform(10, W - 10):.0f}" cy="{rnd.uniform(10, HZ - 30):.0f}" '
        f'r="{rnd.choice([.6, .8, 1, 1.3, 1.7])}" fill="#fff" '
        f'style="animation-delay:-{rnd.uniform(0, 4):.2f}s;animation-duration:{rnd.uniform(2.4, 5.5):.2f}s"/>'
        for _ in range(110))

    sun_c = (930, HZ, 150)
    sun = (f'<circle class="sunglow" cx="{sun_c[0]}" cy="{sun_c[1]}" r="{sun_c[2] + 18}" fill="{C["pink"]}" filter="url(#softglow)"/>'
           f'<circle cx="{sun_c[0]}" cy="{sun_c[1]}" r="{sun_c[2]}" fill="url(#sun)" mask="url(#sunMask)"/>')

    pts, x = [(640, HZ)], 640
    while x < W:
        x += rnd.uniform(18, 46)
        near_sun = abs(x - 930) < 220
        pts.append((min(x, W), HZ - rnd.uniform(14, 62 if near_sun else 36)))
    pts.append((W, HZ))
    mpath = " ".join(f"{a:.0f},{b:.0f}" for a, b in pts)
    mountains = (f'<polygon points="{mpath}" fill="#070a16"/>'
                 f'<polyline points="{mpath}" fill="none" stroke="{C["cyan"]}" stroke-opacity=".45" stroke-width="1.2"/>')

    vlines = "".join(
        f'<line x1="{600 + k * 16}" y1="{HZ}" x2="{600 + k * 120}" y2="{H}"/>' for k in range(-16, 17))
    hlines = "".join(
        f'<line class="fl" x1="0" x2="{W}" y1="{HZ}" y2="{HZ}" style="animation-delay:-{i * 2.4 / 9:.3f}s"/>'
        for i in range(9))
    floor = (f'<g clip-path="url(#floor-clip)"><rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#floorg)"/>'
             f'<g stroke="{C["pink"]}" stroke-opacity=".55" stroke-width="1.3" filter="url(#glow)">{vlines}{hlines}</g></g>'
             f'<line x1="0" x2="{W}" y1="{HZ}" y2="{HZ}" stroke="{C["pink"]}" stroke-width="2" filter="url(#glow)"/>')

    # --- left text block -------------------------------------------------
    boot = (f'<text x="64" y="84" font-size="15" fill="{C["muted"]}">'
            f'<tspan class="pulse" fill="{C["lime"]}">&#9679;</tspan>'
            f'<tspan fill="{C["lime"]}"> SYSTEM ONLINE</tspan>'
            f'<tspan>  //  github.com/Danielkis97</tspan></text>')

    name_attrs = 'x="60" y="212" textLength="486" lengthAdjust="spacingAndGlyphs"'
    name = (f'<text {name_attrs} fill="{C["cyan"]}" fill-opacity=".85" class="nm g1">DANIEL</text>'
            f'<text {name_attrs} fill="{C["pink"]}" fill-opacity=".85" class="nm g2">DANIEL</text>'
            f'<text {name_attrs} fill="url(#nameFill)" class="nm">DANIEL</text>'
            f'<g clip-path="url(#slice)"><rect x="40" y="90" width="540" height="140" fill="{C["bg"]}" class="gs"/>'
            f'<text {name_attrs} fill="{C["cyan2"]}" class="nm gs">DANIEL</text></g>')

    aka = (f'<text x="574" y="146" font-size="14" fill="{C["muted"]}">aka</text>'
           f'<text x="572" y="190" font-size="38" font-weight="700" fill="{C["lime"]}" filter="url(#glow)">R00t'
           f'<tspan class="blink">_</tspan></text>')

    roles = f'<text x="64" y="{ROLE_Y}" font-size="{ROLE_SIZE}" fill="{C["lime"]}">&gt;</text>'
    for i, role in enumerate(ROLES):
        roles += (f'<text x="{ROLE_X}" y="{ROLE_Y}" font-size="{ROLE_SIZE}" fill="{C["cyan"]}" '
                  f'clip-path="url(#role{i})" textLength="{mono_w(role, ROLE_SIZE):.1f}" '
                  f'lengthAdjust="spacingAndGlyphs">{esc(role)}</text>')
    roles += (f'<rect x="{ROLE_X}" y="{ROLE_Y - 22}" width="13" height="27" fill="{C["cyan"]}" class="blink">'
              f'{_discrete("x", cursor_ev, total, offset=ROLE_X + 3)}</rect>')

    chips, cx = "", 64
    for i, (label, col) in enumerate([("Germany", C["cyan"]), ("full-time job", C["violet"]),
                                      ("part-time Applied AI studies", C["pink"]),
                                      ("build > refine > ship", C["lime"])]):
        g, w = chip(cx, 278, label, col, cls="chipin")
        chips += g.replace('class="chipin"', f'class="chipin" style="animation-delay:{.3 + i * .15:.2f}s"')
        cx += w + 10

    hud = (f'<g font-size="12" fill="{C["muted"]}" text-anchor="end">'
           f'<text x="1168" y="40">uptime <tspan fill="{C["text"]}">since 2024</tspan></text>'
           f'<text x="1168" y="58">status <tspan fill="{C["lime"]}">shipping</tspan></text>'
           f'<text x="1168" y="76">mode <tspan fill="{C["pink"]}">build_first</tspan></text></g>')

    body = (f'<g clip-path="url(#card)">'
            f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
            f'<g clip-path="url(#sky-clip)">{stars}{sun}{mountains}</g>'
            f'{floor}{hud}{boot}{name}{aka}{roles}{chips}'
            f'<rect width="{W}" height="{H}" fill="url(#scanlines)"/>'
            f'<rect class="sweep" width="{W}" height="120" fill="url(#scan)"/>'
            f'</g>' + frame(W, H).split("/>", 1)[1])
    return svg(W, H, body, "Daniel aka R00t",
               "Synthwave hero banner: a glitching DANIEL headline, a typed ticker cycling through "
               + ", ".join(ROLES) + ", a striped neon sun and an endless perspective grid.",
               style=style, defs=defs)
