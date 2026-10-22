"""Project cards: text on the left, a tiny looping scene about the project on the right."""
import math
import random

from art_common import C, SANS, chip, esc, frame, frame_defs, mono_w, svg

W, H = 580, 260
VX, VY, VS = 344, 22, 216  # vignette box (x, y, size)


def _segments(x, y, segs, size, fill):
    """Render a line made of (text, redacted) pieces; redacted pieces become flickering bars."""
    out = ""
    for text, redacted in segs:
        w = mono_w(text, size)
        if redacted:
            out += (f'<rect class="redact" x="{x:.1f}" y="{y - size * .82:.1f}" width="{w:.1f}" '
                    f'height="{size * 1.05:.1f}" rx="1.5" fill="{C["text"]}" '
                    f'style="animation-delay:-{(x * 7) % 3:.2f}s"/>')
        elif text:
            out += (f'<text x="{x:.1f}" y="{y}" font-size="{size}" fill="{fill}" textLength="{w:.1f}" '
                    f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{esc(text)}</text>')
        x += w
    return out


def card(num, kind, title, desc, tags, accent, scene, style="", defs="", aria=""):
    a = C[accent]
    body = frame(W, H, rx=16)
    body += (f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="15" fill="url(#corner)"/>'
             f'<text x="26" y="40" font-size="11" letter-spacing="1.5" fill="{a}">PROJECT {num:02d}'
             f'<tspan fill="{C["dim"]}">  //  </tspan><tspan fill="{C["muted"]}">{esc(kind)}</tspan></text>')
    for i, line in enumerate(title):
        if isinstance(line, list):
            body += _segments(26, 74 + i * 29, line, 22, "#fff")
        else:
            body += (f'<text x="26" y="{74 + i * 29}" class="sans" font-size="24" font-weight="800" '
                     f'fill="#fff">{esc(line)}</text>')
    dy = 74 + len(title) * 29 + 12
    for i, line in enumerate(desc):
        segs = line if isinstance(line, list) else [(line, False)]
        body += _segments(26, dy + i * 19, segs, 12, C["muted"])
    tx = 26
    for t in tags:
        g, w = chip(tx, 208, t, a, size=11, pad=9, h=22)
        body += g
        tx += w + 7
    body += (f'<g transform="translate({VX},{VY})">'
             f'<rect width="{VS}" height="{VS}" rx="12" fill="{C["bg"]}" stroke="{C["line"]}"/>'
             f'<g clip-path="url(#vclip)">{scene}</g>'
             f'<rect width="{VS}" height="{VS}" rx="12" fill="url(#vscan)"/></g>')
    d = frame_defs() + defs + (
        f'<radialGradient id="corner" cx="0" cy="0" r="1"><stop offset="0" stop-color="{a}" stop-opacity=".16"/>'
        f'<stop offset=".6" stop-color="{a}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="vclip"><rect width="{VS}" height="{VS}" rx="12"/></clipPath>'
        f'<pattern id="vscan" width="3" height="3" patternUnits="userSpaceOnUse">'
        f'<rect width="3" height="1" fill="#000" fill-opacity=".22"/></pattern>')
    style += (".redact{animation:redact 3s steps(1) infinite}"
              "@keyframes redact{0%,100%{opacity:1}46%{opacity:.25}48%{opacity:1}83%{opacity:.6}85%{opacity:1}}"
              ".blink{animation:blink 1.05s steps(1) infinite}@keyframes blink{50%{opacity:0}}")
    plain_title = " ".join(t if isinstance(t, str) else "".join("█" * len(s) if r else s for s, r in t) for t in title)
    return svg(W, H, body, plain_title, aria, style=style, defs=d)


def _label(x, y, text, fill, size=9.5, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>'
            f'{esc(text)}</text>')


# --- 01  IoT anomaly detection ------------------------------------------------
def iot():
    rnd = random.Random(3)

    def series(y0, amp, spike_at=None):
        pts = []
        base = [rnd.uniform(-amp, amp) for _ in range(28)]
        for k in range(55):  # two identical periods of 216px so the scroll loops seamlessly
            x = k * 8
            v = base[k % 27]
            if spike_at is not None and (k % 27) == spike_at:
                v = -amp * 3.4
            pts.append(f"{x},{y0 + v:.1f}")
        return "M" + " L".join(pts)

    lines = ""
    for (y0, col, amp, spike, name) in [(122, C["cyan"], 5, None, "temp"), (152, C["violet"], 5, None, "humid"),
                                        (186, C["pink"], 4, 19, "sound")]:
        lines += f'<path d="{series(y0, amp, spike)}" fill="none" stroke="{col}" stroke-width="1.6"/>'
        lines += _label(6, y0 - 9, name, col, 8)
    marks = "".join(
        f'<circle cx="{19 * 8 + o}" cy="{186 - 4 * 3.4:.1f}" r="8" fill="none" stroke="{C["red"]}" stroke-width="2" class="ring"/>'
        f'<text x="{19 * 8 + o}" y="{186 - 4 * 3.4 - 13:.1f}" font-size="8.5" fill="{C["red"]}" text-anchor="middle" '
        f'font-weight="700">ANOMALY</text>' for o in (0, 216))
    turbine = (f'<g transform="translate(46,58)"><path d="M-2,0 L-4,46 L4,46 L2,0Z" fill="{C["dim"]}"/>'
               f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="2.6s" repeatCount="indefinite"/>'
               + "".join(f'<path d="M0,0 L-3,-4 L0,-30 L3,-4Z" fill="{C["text"]}" transform="rotate({a})"/>' for a in (0, 120, 240))
               + f'</g><circle r="3.5" fill="{C["amber"]}"/></g>')
    api = (_label(206, 30, "POST /predict", C["text"], 9.5, "end")
           + _label(206, 44, "200 OK · 12ms", C["lime"], 9.5, "end")
           + _label(206, 58, "IsolationForest", C["muted"], 9, "end")
           + f'<circle cx="122" cy="26" r="3.5" fill="{C["lime"]}" class="blink"/>')
    scene = (turbine + api + f'<line x1="0" x2="{VS}" y1="96" y2="96" stroke="{C["line"]}"/>'
             f'<g class="scroll">{lines}{marks}</g>')
    style = (".scroll{animation:scroll 6s linear infinite}@keyframes scroll{to{transform:translateX(-216px)}}"
             ".ring{animation:ring 1s ease-in-out infinite}@keyframes ring{50%{stroke-opacity:.2}}")
    return card(1, "ML IN PRODUCTION", ["IoT Anomaly", "Detection"],
                ["Wind-turbine factory sensors stream",
                 "into an IsolationForest behind a",
                 "Flask API. Dockerized, 29/29 checks."],
                ["Python", "Flask", "Docker", "sklearn"], "cyan", scene, style,
                aria="Card: a spinning wind turbine, three scrolling sensor lines and a flagged anomaly spike.")


# --- 02  Age / gender / emotion ------------------------------------------------
def emotion():
    cx, cy = 108, 96
    mouths = ["M88,128 C98,142 118,142 128,128 C118,135 98,135 88,128",
              "M91,131 C100,132 116,132 125,131 C116,133 100,133 91,131",
              "M100,131 C100,119 116,119 116,131 C116,143 100,143 100,131"]
    vals = ";".join([mouths[0], mouths[0], mouths[1], mouths[1], mouths[2], mouths[2], mouths[0]])
    face = (f'<ellipse cx="{cx}" cy="{cy}" rx="44" ry="56" fill="none" stroke="{C["violet"]}" stroke-width="1.6"/>'
            f'<path d="M84,80 q8,-6 16,0 M116,80 q8,-6 16,0" fill="none" stroke="{C["violet"]}" stroke-width="1.6"/>'
            f'<circle cx="92" cy="92" r="3" fill="{C["text"]}"/><circle cx="124" cy="92" r="3" fill="{C["text"]}"/>'
            f'<path d="M108,96 L104,114 L111,114" fill="none" stroke="{C["violet"]}" stroke-width="1.4"/>'
            f'<path fill="{C["pink"]}" fill-opacity=".85"><animate attributeName="d" dur="9s" repeatCount="indefinite" '
            f'values="{vals}" keyTimes="0;.28;.33;.61;.66;.94;1"/></path>')
    rnd = random.Random(5)
    dots = "".join(f'<circle cx="{cx + 40 * math.cos(a):.1f}" cy="{cy + 52 * math.sin(a):.1f}" r="1.6" '
                   f'fill="{C["cyan"]}" class="lm" style="animation-delay:-{rnd.uniform(0, 2):.2f}s"/>'
                   for a in [i * math.pi / 9 for i in range(18)])
    x0, y0, x1, y1 = 52, 30, 164, 162
    br = "".join(f'<path d="{d}" fill="none" stroke="{C["lime"]}" stroke-width="2.4"/>' for d in [
        f"M{x0},{y0 + 16} V{y0} H{x0 + 16}", f"M{x1 - 16},{y0} H{x1} V{y0 + 16}",
        f"M{x0},{y1 - 16} V{y1} H{x0 + 16}", f"M{x1 - 16},{y1} H{x1} V{y1 - 16}"])
    scan = (f'<rect x="{x0 + 3}" y="{y0}" width="{x1 - x0 - 6}" height="2" fill="{C["lime"]}" opacity=".7" class="scan"/>')
    labels = ""
    for i, (emo, p) in enumerate([("happy", "0.94"), ("neutral", "0.81"), ("surprise", "0.77")]):
        labels += (f'<g class="lab" style="animation-delay:{i * 3}s">'
                   f'<rect x="{x0}" y="{y1 + 6}" width="{x1 - x0}" height="18" rx="3" fill="{C["lime"]}"/>'
                   f'<text x="{x0 + 6}" y="{y1 + 18.5}" font-size="10" font-weight="700" fill="{C["bg"]}">'
                   f'age 26 · {emo} {p}</text></g>')
    scene = (face + dots + br + scan + labels
             + _label(108, 206, "TFLite · on-device · 0 cloud calls", C["muted"], 8.5, "middle")
             + f'<circle cx="14" cy="14" r="4" fill="{C["red"]}" class="blink"/>'
             + _label(23, 17.5, "LIVE", C["red"], 9, extra='font-weight="700"'))
    style = (f".scan{{animation:scan 2.2s ease-in-out infinite alternate}}@keyframes scan{{to{{transform:translateY({y1 - y0 - 2}px)}}}}"
             ".lab{opacity:0;animation:lab 9s steps(1) infinite}@keyframes lab{0%{opacity:1}33.3%,100%{opacity:0}}"
             ".lm{animation:lm 2s ease-in-out infinite}@keyframes lm{50%{opacity:.2}}")
    return card(2, "EDGE AI · COMPUTER VISION", ["Age · Gender ·", "Emotion Recognition"],
                ["Webcam + image face analysis that",
                 "runs 100% local. Benchmarked CPU/GPU/",
                 "edge, exported to TFLite for mobile."],
                ["TensorFlow", "OpenCV", "DeepFace"], "violet", scene, style,
                aria="Card: a wireframe face inside a detection box whose expression and label cycle happy, neutral, surprise.")


# --- 03  Video object detection ---------------------------------------------------
def video():
    def walker(x_from, x_to, y, dur, delay, conf, col):
        legs = (f'<g><animateTransform attributeName="transform" type="rotate" values="-22 0 0;22 0 0;-22 0 0" '
                f'dur=".7s" repeatCount="indefinite"/><line x1="0" y1="0" x2="0" y2="18" stroke="{C["text"]}" stroke-width="2.4"/></g>'
                f'<g><animateTransform attributeName="transform" type="rotate" values="22 0 0;-22 0 0;22 0 0" '
                f'dur=".7s" repeatCount="indefinite"/><line x1="0" y1="0" x2="0" y2="18" stroke="{C["text"]}" stroke-width="2.4"/></g>')
        fig = (f'<circle cx="0" cy="-30" r="6" fill="{C["text"]}"/>'
               f'<line x1="0" y1="-24" x2="0" y2="0" stroke="{C["text"]}" stroke-width="2.4"/>'
               f'<line x1="-8" y1="-14" x2="8" y2="-18" stroke="{C["text"]}" stroke-width="2"/>' + legs)
        box = (f'<rect x="-14" y="-41" width="28" height="62" fill="none" stroke="{col}" stroke-width="1.6"/>'
               f'<rect x="-14" y="-53" width="{mono_w(f"person {conf}", 8) + 6:.0f}" height="12" fill="{col}"/>'
               f'<text x="-11" y="-44" font-size="8" font-weight="700" fill="{C["bg"]}">person {conf}</text>')
        return (f'<g><animateTransform attributeName="transform" type="translate" from="{x_from} {y}" to="{x_to} {y}" '
                f'dur="{dur}s" begin="-{delay}s" repeatCount="indefinite"/>{fig}{box}</g>')

    ground = "".join(f'<line x1="{x}" y1="178" x2="{x - 30}" y2="216" stroke="{C["line"]}"/>' for x in range(0, 280, 26))
    scene = (f'<rect y="160" width="{VS}" height="56" fill="#0b1020"/>{ground}'
             f'<line x1="0" x2="{VS}" y1="160" y2="160" stroke="{C["dim"]}"/>'
             + walker(-30, 250, 150, 7, 1, "0.97", C["violet"])
             + walker(250, -30, 172, 9, 4, "0.91", C["cyan"])
             + walker(-30, 250, 196, 5.5, 3.2, "0.88", C["pink"])
             + f'<circle cx="14" cy="16" r="4" fill="{C["red"]}" class="blink"/>'
             + _label(23, 19.5, "REC  MOT17-04", C["muted"], 9))
    for i, m in enumerate(["YOLOv8", "Faster R-CNN", "SSD"]):
        scene += (f'<g class="mdl" style="animation-delay:{i * 2}s">'
                  + _label(204, 19.5, f"model: {m}", C["lime"], 9, "end") + "</g>")
    scene += _label(204, 34, "persons tracked: 3", C["muted"], 9, "end")
    style = ".mdl{opacity:0;animation:mdl 6s steps(1) infinite}@keyframes mdl{0%{opacity:1}33.3%,100%{opacity:0}}"
    return card(3, "COMPUTER VISION", ["Video Object", "Detection"],
                ["Person detection & tracking across",
                 "video frames: YOLOv8 vs Faster R-CNN",
                 "vs SSD, with GUI and eval metrics."],
                ["PyTorch", "YOLOv8", "OpenCV"], "pink", scene, style,
                aria="Card: stick figures walk across a street, each followed by a labelled person bounding box.")


# --- 04  Sentiment analysis --------------------------------------------------------
def sentiment():
    words = [("\"a masterpiece\"", True), ("\"painfully boring\"", False),
             ("\"loved every minute\"", True), ("\"waste of time\"", False)]
    dur = 10
    scene = ""
    for i, (w, pos) in enumerate(words):
        col = C["lime"] if pos else C["red"]
        scene += (f'<g class="wd" style="animation-delay:{i * dur / 4}s">'
                  f'<text x="108" y="34" font-size="12" text-anchor="middle" fill="{col}">{esc(w)}</text>'
                  f'<text x="108" y="52" font-size="9" text-anchor="middle" fill="{C["muted"]}">'
                  f'tokenize -> lemmatize -> NB</text></g>')
    # gauge
    gx, gy, r = 108, 168, 66
    arc = f"M{gx - r},{gy} A{r},{r} 0 0 1 {gx + r},{gy}"
    ticks = "".join(
        f'<line x1="{gx + (r - 8) * math.cos(math.pi * (1 - k / 10)):.1f}" y1="{gy - (r - 8) * math.sin(math.pi * (1 - k / 10)):.1f}" '
        f'x2="{gx + r * math.cos(math.pi * (1 - k / 10)):.1f}" y2="{gy - r * math.sin(math.pi * (1 - k / 10)):.1f}" '
        f'stroke="{C["dim"]}" stroke-width="1.5"/>' for k in range(11))
    angles = []
    for _, pos in words:
        angles += [55 if pos else -55] * 2
    seq, keys = [], []
    for i, a in enumerate([55, -55, 55, -55]):
        t0 = i / 4
        seq += [a, a]
        keys += [t0 + .06, t0 + .25]
    seq = [-55] + seq + [-55]
    keys = [0] + keys + [1]
    needle = (f'<g><animateTransform attributeName="transform" type="rotate" dur="{dur}s" repeatCount="indefinite" '
              f'values="{";".join(f"{a} {gx} {gy}" for a in seq)}" keyTimes="{";".join(f"{k:.3f}" for k in keys)}" '
              f'calcMode="spline" keySplines="{";".join([".4 0 .2 1"] * (len(keys) - 1))}"/>'
              f'<line x1="{gx}" y1="{gy}" x2="{gx}" y2="{gy - r + 14}" stroke="#fff" stroke-width="3" stroke-linecap="round"/></g>')
    scene += (f'<path d="{arc}" fill="none" stroke="url(#sentg)" stroke-width="10" stroke-linecap="round"/>{ticks}{needle}'
              f'<circle cx="{gx}" cy="{gy}" r="6" fill="{C["text"]}"/>'
              + _label(gx - r, gy + 22, "NEG", C["red"], 9, "middle", 'font-weight="700"')
              + _label(gx + r, gy + 22, "POS", C["lime"], 9, "middle", 'font-weight="700"')
              + _label(gx, gy + 34, "IMDB · acc 84%+", C["muted"], 9, "middle"))
    defs = (f'<linearGradient id="sentg" x1="0" x2="1"><stop offset="0" stop-color="{C["red"]}"/>'
            f'<stop offset=".5" stop-color="{C["amber"]}"/><stop offset="1" stop-color="{C["lime"]}"/></linearGradient>')
    style = (".wd{opacity:0;animation:wd 10s linear infinite}"
             "@keyframes wd{0%{opacity:0;transform:translateY(-10px)}4%{opacity:1;transform:none}21%{opacity:1;transform:none}"
             "25%,100%{opacity:0;transform:translateY(14px)}}")
    return card(4, "NLP", ["Sentiment Analysis", "of Movie Reviews"],
                ["IMDB reviews -> tokenize, lemmatize,",
                 "classify. A tuned Naive Bayes pipeline",
                 "with 84%+ accuracy."],
                ["NLTK", "scikit-learn", "Python"], "amber", scene, style, defs,
                aria="Card: movie review quotes drop in and a sentiment gauge needle swings to negative or positive.")


# --- 05  Terraform on AWS -----------------------------------------------------------
def terraform():
    els = [
        ('<rect x="14" y="44" width="188" height="140" rx="8" fill="none" stroke="{v}" stroke-dasharray="4 3"/>'
         '<text x="22" y="58" font-size="9" fill="{v}">vpc</text>'),
        ('<rect x="24" y="66" width="80" height="70" rx="5" fill="{p}" stroke="{d}"/>'
         '<text x="30" y="78" font-size="8" fill="{m}">subnet-a</text>'),
        ('<rect x="112" y="66" width="80" height="70" rx="5" fill="{p}" stroke="{d}"/>'
         '<text x="118" y="78" font-size="8" fill="{m}">subnet-b</text>'),
        ('<rect x="44" y="88" width="40" height="34" rx="4" fill="none" stroke="{a}" stroke-width="1.6"/>'
         '<text x="64" y="109" font-size="9" fill="{a}" text-anchor="middle">EC2</text>'),
        ('<rect x="132" y="88" width="40" height="34" rx="4" fill="none" stroke="{a}" stroke-width="1.6"/>'
         '<text x="152" y="109" font-size="9" fill="{a}" text-anchor="middle">EC2</text>'),
        ('<rect x="78" y="146" width="60" height="26" rx="13" fill="none" stroke="{c}" stroke-width="1.6"/>'
         '<text x="108" y="163" font-size="9" fill="{c}" text-anchor="middle">ELB</text>'
         '<path d="M92,146 L64,122 M124,146 L152,122" stroke="{c}" stroke-dasharray="3 3"/>'),
        ('<text x="196" y="182" font-size="8" fill="{l}" text-anchor="end">ASG 2..4</text>'),
    ]
    fmt = dict(v=C["violet"], p=C["panel"], d=C["line"], m=C["muted"], a=C["amber"], c=C["cyan"], l=C["lime"])
    n = len(els)
    style = ""
    scene = (_label(12, 22, "$ terraform apply -auto-approve", C["text"], 9.5)
             + f'<text x="12" y="36" font-size="9" fill="{C["muted"]}">creating resources'
             f'<tspan class="blink">...</tspan></text>')
    for i, e in enumerate(els):
        p = 8 + i * 8
        style += (f"@keyframes tf{i}{{0%,{p}%{{opacity:0;transform:translateY(6px)}}{p + 4}%,92%{{opacity:1;transform:none}}"
                  f"100%{{opacity:0}}}}.tf{i}{{animation:tf{i} 9s ease-out infinite}}")
        scene += f'<g class="tf{i}">{e.format(**fmt)}</g>'
    pd = 8 + n * 8 + 4
    style += (f"@keyframes done{{0%,{pd}%{{opacity:0}}{pd + 3}%,92%{{opacity:1}}100%{{opacity:0}}}}"
              ".done{animation:done 9s steps(1) infinite}")
    scene += (f'<g class="done">' + _label(12, 205, f"Apply complete! Resources: {n} added.", C["lime"], 9.5,
                                           extra='font-weight="700"') + "</g>")
    return card(5, "CLOUD · IaC", ["Terraform", "AWS Infrastructure"],
                ["VPC, multi-AZ subnets, an ELB and an",
                 "Auto Scaling Group of EC2 web servers,",
                 "all from a single terraform apply."],
                ["Terraform", "AWS", "HCL"], "amber", scene, style,
                aria="Card: terraform apply draws a VPC, two subnets, two EC2 instances, a load balancer and an auto scaling group.")


# --- 06  Superspeed Seeds -----------------------------------------------------------
def seeds():
    rnd = random.Random(9)
    stars = "".join(f'<circle cx="{rnd.uniform(0, 432):.0f}" cy="{rnd.uniform(30, 120):.0f}" r="1" fill="#fff" opacity=".5"/>'
                    for _ in range(26))
    stars += "".join(s.replace('cx="', 'cx="2', 0) for s in [])
    rain = "".join(f'<line x1="{x}" y1="{y}" x2="{x - 6}" y2="{y + 12}" stroke="{C["cyan2"]}" stroke-opacity=".35"/>'
                   for x, y in [(rnd.uniform(0, 240), rnd.uniform(-20, 216)) for _ in range(30)])
    road = "".join(f'<rect x="{x}" y="184" width="22" height="4" rx="2" fill="{C["dim"]}"/>' for x in range(0, 440, 44))
    pod = (f'<g class="bob"><g transform="translate(62,150)">'
           f'<ellipse cx="0" cy="0" rx="20" ry="13" fill="{C["amber"]}"/>'
           f'<ellipse cx="-4" cy="-3" rx="12" ry="6" fill="#fde68a" opacity=".6"/>'
           f'<path d="M6,-12 q10,-14 18,-6 q-8,2 -18,6Z" fill="{C["lime"]}"/>'
           f'<path d="M-22,2 L-40,-2 M-22,6 L-46,6 M-22,10 L-38,13" stroke="{C["cyan"]}" stroke-width="2" class="trail"/>'
           f'</g></g>')

    def fudder(y, dur, delay, laser=False):
        eye = f'<circle cx="-4" cy="-2" r="2.4" fill="#fff"/><circle cx="4" cy="-2" r="2.4" fill="#fff"/>'
        beam = (f'<line x1="-12" y1="0" x2="-60" y2="0" stroke="{C["red"]}" stroke-width="2" class="blink"/>' if laser else "")
        return (f'<g><animateTransform attributeName="transform" type="translate" from="250 {y}" to="-40 {y}" '
                f'dur="{dur}s" begin="-{delay}s" repeatCount="indefinite"/>{beam}'
                f'<path d="M-10,6 Q-12,-10 0,-11 Q12,-10 10,6 L6,2 L3,7 L0,2 L-3,7 L-6,2Z" fill="{C["pink"]}"/>{eye}</g>')

    scene = (f'<g class="par1">{stars}</g>{rain.replace("<line", "<line class=\"rain\"")}'
             f'<rect y="176" width="{VS}" height="40" fill="#0b1020"/><g class="par2">{road}</g>'
             + fudder(110, 3.6, 0.4, laser=True) + fudder(160, 2.8, 1.9) + pod
             + _label(10, 20, "LVL 37/100", C["lime"], 10, extra='font-weight="700"')
             + _label(206, 20, "SEEDS 128", C["amber"], 10, "end", 'font-weight="700"')
             + _label(10, 34, "world: CYBER  weather: rain", C["muted"], 8.5))
    style = (".par1{animation:p1 14s linear infinite}@keyframes p1{to{transform:translateX(-216px)}}"
             ".par2{animation:p2 .9s linear infinite}@keyframes p2{to{transform:translateX(-44px)}}"
             ".bob{animation:bob 1.4s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-16px)}}"
             ".trail{animation:blink .2s steps(1) infinite}"
             ".rain{animation:rain .8s linear infinite}@keyframes rain{to{transform:translate(-12px,24px)}}")
    return card(6, "GAME DEV", ["Superspeed Seeds:", "Racing Royale"],
                ["A 100-level seed-powered racer with",
                 "Fudders, wild weather & 4 SeedDrivers.",
                 "Built for the SuperSeed Tesla Contest."],
                ["Python", "Game Dev", "100 levels"], "lime", scene, style,
                aria="Card: a seed pod racer bobs through the rain while laser-shooting Fudders fly past.")


# --- 07  Habit tracker -----------------------------------------------------------------
def habits():
    rnd = random.Random(11)
    cols, rows, s, g = 10, 7, 15, 4
    x0, y0 = 14, 34
    cells = ""
    for c in range(cols):
        for r in range(rows):
            lvl = rnd.choice([1, 2, 3, 3, 4, 4, 4]) if (c * rows + r) % 9 != 4 else 0
            col = [C["line"], "#365314", "#4d7c0f", "#65a30d", C["lime"]][lvl]
            idx = c * rows + r
            p = 2 + idx * 1.0
            cells += f'<rect x="{x0 + c * (s + g)}" y="{y0 + r * (s + g)}" width="{s}" height="{s}" rx="3" fill="{C["line"]}"/>'
            if lvl:
                cells += (f'<rect class="hc" x="{x0 + c * (s + g)}" y="{y0 + r * (s + g)}" width="{s}" height="{s}" rx="3" '
                          f'fill="{col}" style="animation-delay:{p * 0.08:.2f}s"/>')
    scene = (_label(14, 22, "$ habit analyze --all", C["text"], 9.5) + cells
             + _label(14, 186, "current streak", C["muted"], 9) + _label(202, 186, "21 days", C["lime"], 9, "end", 'font-weight="700"')
             + _label(14, 202, "longest streak", C["muted"], 9) + _label(202, 202, "42 days", C["cyan"], 9, "end", 'font-weight="700"'))
    style = (".hc{opacity:0;animation:hc 8s steps(1) infinite}"
             "@keyframes hc{0%{opacity:0}1%,88%{opacity:1}100%{opacity:0}}")
    # stagger: each cell's own delay places its 1% switch-on point later in the loop
    return card(7, "PYTHON APP", ["Habit Tracker"],
                ["Create habits, log completions and",
                 "analyze current & longest streaks,",
                 "daily or weekly. Clean OOP Python."],
                ["Python", "OOP", "Analytics"], "lime", scene, style,
                aria="Card: a streak calendar fills up day by day next to current and longest streak counters.")


# --- 08  Classified -----------------------------------------------------------------------
def classified():
    cx, cy = 108, 100
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["red"]}" stroke-opacity=".3"/>'
                    for r in (22, 46, 70))
    cross = (f'<line x1="{cx - 78}" x2="{cx + 78}" y1="{cy}" y2="{cy}" stroke="{C["red"]}" stroke-opacity=".2"/>'
             f'<line x1="{cx}" x2="{cx}" y1="{cy - 78}" y2="{cy + 78}" stroke="{C["red"]}" stroke-opacity=".2"/>')
    sweep = (f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" '
             f'dur="4s" repeatCount="indefinite"/>'
             f'<path d="M{cx},{cy} L{cx + 72},{cy} A72,72 0 0 0 {cx + 72 * math.cos(math.radians(-40)):.1f},'
             f'{cy + 72 * math.sin(math.radians(-40)):.1f} Z" fill="url(#sweepg)"/></g>')
    blips = ""
    for i, (a, d) in enumerate([(30, 50), (140, 34), (250, 60), (320, 26)]):
        bx, by = cx + d * math.cos(math.radians(a)), cy + d * math.sin(math.radians(a))
        blips += (f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="3.5" fill="{C["red"]}" class="blip" '
                  f'style="animation-delay:{(a / 360) * 4:.2f}s"/>')
    scene = (rings + cross + sweep + blips
             + f'<rect x="38" y="184" width="140" height="20" rx="3" fill="none" stroke="{C["red"]}" class="redact"/>'
             + _label(108, 198, "CLEARANCE REQUIRED", C["red"], 9.5, "middle", 'font-weight="700"'))
    defs = (f'<linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["red"]}" stop-opacity=".05"/>'
            f'<stop offset="1" stop-color="{C["red"]}" stop-opacity=".55"/></linearGradient>')
    style = (".blip{opacity:0;animation:blip 4s ease-out infinite}"
             "@keyframes blip{0%{opacity:1}60%,100%{opacity:0}}")
    return card(8, "STEALTH MODE", [[("Project ", False), ("████████", True)], "in progress"],
                [[("A browser ", False), ("████████", True), (" with on-chain", False)],
                 [("████████", True), (". Contracts, game loop,", False)],
                 [("the whole stack. Reveal: soon", False), ("™", False)]],
                ["TypeScript", "Solidity", "????"], "red", scene, style, defs,
                aria="Card: a redacted stealth project with a radar sweep and the note clearance required.")


def build_all():
    return [("01-iot", iot()), ("02-emotion", emotion()), ("03-video", video()), ("04-sentiment", sentiment()),
            ("05-terraform", terraform()), ("06-seeds", seeds()), ("07-habits", habits()),
            ("08-classified", classified())]
