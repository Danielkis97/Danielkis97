"""Project cards: text on the left, a tiny looping scene about the project on the right."""
import math
import random

from art_common import C, chip, esc, frame, frame_defs, mono_w, svg

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


def _brackets(x0, y0, x1, y1, col, L=12, sw=2):
    return "".join(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"/>' for d in [
        f"M{x0},{y0 + L} V{y0} H{x0 + L}", f"M{x1 - L},{y0} H{x1} V{y0 + L}",
        f"M{x0},{y1 - L} V{y1} H{x0 + L}", f"M{x1 - L},{y1} H{x1} V{y1 - L}"])


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
             f'<rect width="{VS}" height="{VS}" rx="12" fill="{C["bg"]}"/>'
             f'<g clip-path="url(#vclip)"><rect width="{VS}" height="{VS}" fill="url(#vgrid)"/>'
             f'<rect width="{VS}" height="{VS}" fill="url(#vglow)"/>{scene}</g>'
             f'<rect width="{VS}" height="{VS}" rx="12" fill="url(#vscan)"/>'
             f'<rect x=".5" y=".5" width="{VS - 1}" height="{VS - 1}" rx="12" fill="none" stroke="{C["line"]}"/>'
             f'<g opacity=".7">{_brackets(4, 4, VS - 4, VS - 4, a, 9, 1.5)}</g></g>')
    d = frame_defs() + defs + (
        f'<radialGradient id="corner" cx="0" cy="0" r="1"><stop offset="0" stop-color="{a}" stop-opacity=".16"/>'
        f'<stop offset=".6" stop-color="{a}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="vglow" cx=".5" cy="1" r=".9"><stop offset="0" stop-color="{a}" stop-opacity=".18"/>'
        f'<stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>'
        f'<pattern id="vgrid" width="18" height="18" patternUnits="userSpaceOnUse">'
        f'<path d="M18,0 H0 V18" fill="none" stroke="#0f172a" stroke-width="1"/></pattern>'
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


def _live(text, col=None):
    col = col or C["red"]
    return (f'<circle cx="14" cy="15" r="3.5" fill="{col}" class="blink"/>'
            + _label(22, 18.5, text, C["muted"], 8.5))


# --- 01  IoT anomaly detection ------------------------------------------------
def iot():
    rnd = random.Random(3)
    lanes = [(122, C["cyan"], "temperature", None), (156, C["violet"], "humidity", None),
             (190, C["pink"], "sound_volume", 19)]
    charts, defs = "", ""
    for li, (y0, col, name, spike) in enumerate(lanes):
        base = [rnd.uniform(-5, 5) for _ in range(27)]
        pts = []
        for k in range(55):  # two identical 216px periods so the scroll loops seamlessly
            v = base[k % 27]
            if spike is not None and k % 27 == spike:
                v = -17
            pts.append((k * 8, y0 + v))
        line = "M" + " L".join(f"{x},{y:.1f}" for x, y in pts)
        area = line + f" L{pts[-1][0]},{y0 + 12} L0,{y0 + 12} Z"
        defs += (f'<linearGradient id="ar{li}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" '
                 f'stop-opacity=".35"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient>')
        charts += (f'<path d="{area}" fill="url(#ar{li})"/>'
                   f'<path d="{line}" fill="none" stroke="{col}" stroke-width="1.6" filter="url(#glow)"/>')
    marks = "".join(
        f'<circle cx="{152 + o}" cy="173" r="6" fill="none" stroke="{C["red"]}" stroke-width="2">'
        f'<animate attributeName="r" values="5;11;5" dur="1.2s" repeatCount="indefinite"/>'
        f'<animate attributeName="stroke-opacity" values="1;.1;1" dur="1.2s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{152 + o}" cy="173" r="2.5" fill="{C["red"]}"/>' for o in (0, 216))
    lane_labels = "".join(_label(8, y0 - 12, name, col, 7.5) for y0, col, name, _ in lanes)
    turbine = (f'<g transform="translate(36,58)"><path d="M-1.5,0 L-4,44 L4,44 L1.5,0Z" fill="{C["dim"]}"/>'
               f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="2.4s" repeatCount="indefinite"/>'
               + "".join(f'<path d="M0,0 L-3,-4 L0,-30 L3,-4Z" fill="url(#blade)" transform="rotate({a})"/>' for a in (0, 120, 240))
               + f'</g><circle r="4" fill="{C["amber"]}" filter="url(#glow)"/></g>')
    panel = (f'<rect x="72" y="30" width="134" height="58" rx="7" fill="{C["panel"]}" stroke="{C["line"]}"/>'
             + _label(82, 45, "anomaly score", C["muted"], 8)
             + f'<g class="ok">{_label(82, 74, "0.12", C["lime"], 20, extra=chr(32) + "font-weight=\"700\"")}'
             + _label(198, 74, "normal", C["lime"], 8.5, "end") + '</g>'
             + f'<g class="alert">{_label(82, 74, "-0.41", C["red"], 20, extra=chr(32) + "font-weight=\"700\"")}'
             + f'<rect x="146" y="63" width="54" height="15" rx="3" fill="{C["red"]}"/>'
             + _label(173, 74, "ANOMALY", C["bg"], 8, "middle", 'font-weight="700"') + '</g>')
    detector = (f'<line x1="120" y1="100" x2="120" y2="204" stroke="{C["text"]}" stroke-opacity=".45" stroke-dasharray="3 3"/>'
                + _label(124, 106, "t = now", C["muted"], 7))
    scene = (_live("LIVE · 3 sensors", C["lime"]) + _label(206, 18.5, "IsolationForest", C["dim"], 8, "end")
             + turbine + panel + lane_labels + f'<g class="scroll">{charts}{marks}</g>' + detector)
    style = (".scroll{animation:scroll 6s linear infinite}@keyframes scroll{to{transform:translateX(-216px)}}"
             ".ok{animation:ok 6s steps(1) infinite}@keyframes ok{0%{opacity:1}13%{opacity:0}32%,100%{opacity:1}}"
             ".alert{animation:al 6s steps(1) infinite}@keyframes al{0%{opacity:0}13%{opacity:1}32%,100%{opacity:0}}")
    defs += (f'<linearGradient id="blade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/>'
             f'<stop offset="1" stop-color="{C["cyan2"]}"/></linearGradient>')
    return card(1, "ML IN PRODUCTION", ["IoT Anomaly", "Detection"],
                ["Wind-turbine factory sensors stream",
                 "into an IsolationForest behind a",
                 "Flask API. Dockerized, 29/29 checks."],
                ["Python", "Flask", "Docker", "sklearn"], "cyan", scene, style, defs,
                aria="Card: a spinning wind turbine, three live sensor charts and an anomaly that trips the detector.")


# --- 02  Age / gender / emotion ------------------------------------------------
def emotion():
    cx, cy, rx, ry = 108, 90, 40, 50
    outer = [(cx + rx * math.cos(2 * math.pi * i / 18), cy + ry * math.sin(2 * math.pi * i / 18)) for i in range(18)]
    inner = [(cx + rx * .6 * math.cos(2 * math.pi * i / 12), cy + 4 + ry * .58 * math.sin(2 * math.pi * i / 12))
             for i in range(12)]
    feats = [(94, 82), (122, 82), (108, 100), (96, 116), (120, 116)]
    edges = [(outer[i], outer[(i + 1) % 18]) for i in range(18)]
    edges += [(inner[i], inner[(i + 1) % 12]) for i in range(12)]
    edges += [(outer[i], inner[round(i * 12 / 18) % 12]) for i in range(18)]
    edges += [(p, min(inner, key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)) for p in feats]
    edges += [(feats[0], feats[2]), (feats[1], feats[2]), (feats[2], feats[3]), (feats[2], feats[4])]
    mesh = "".join(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>' for a, b in edges)
    rnd = random.Random(5)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" class="lm" '
                   f'style="animation-delay:-{rnd.uniform(0, 2):.2f}s"/>' for x, y in outer + inner + feats)
    mouths = ["M94,116 C102,128 114,128 122,116 C114,122 102,122 94,116",
              "M96,119 C104,120 112,120 120,119 C112,121 104,121 96,119",
              "M102,119 C102,108 114,108 114,119 C114,130 102,130 102,119"]
    keys = "0;.28;.33;.61;.66;.94;1"
    mvals = ";".join([mouths[0], mouths[0], mouths[1], mouths[1], mouths[2], mouths[2], mouths[0]])
    eyes = "".join(f'<g class="eye"><ellipse cx="{x}" cy="82" rx="6.5" ry="3.6" fill="none" stroke="{C["cyan2"]}" '
                   f'stroke-width="1.3"/><circle cx="{x}" cy="82" r="1.8" fill="#fff"/></g>' for x in (94, 122))
    face = (f'<g stroke="{C["violet"]}" stroke-opacity=".35" stroke-width=".8">{mesh}</g>'
            f'<g fill="{C["cyan"]}" filter="url(#glow)">{dots}</g>{eyes}'
            f'<path d="M86,72 q8,-6 16,0 M114,72 q8,-6 16,0" fill="none" stroke="{C["violet"]}" stroke-width="1.6"/>'
            f'<path fill="{C["pink"]}" fill-opacity=".9" filter="url(#glow)"><animate attributeName="d" dur="9s" '
            f'repeatCount="indefinite" values="{mvals}" keyTimes="{keys}"/></path>')
    box = _brackets(58, 30, 158, 150, C["lime"], 14, 2.2)
    laser = (f'<g class="scan"><rect x="60" y="20" width="96" height="14" fill="url(#trail)"/>'
             f'<rect x="60" y="33" width="96" height="1.6" fill="{C["lime"]}" filter="url(#glow)"/></g>')
    bars = ""
    vals = [(.94, .10, .08), (.04, .81, .15), (.02, .09, .77)]
    for i, (name, col) in enumerate([("happy", C["lime"]), ("neutral", C["cyan"]), ("surprise", C["pink"])]):
        y = 166 + i * 15
        seq = [vals[i][0], vals[i][0], vals[i][1], vals[i][1], vals[i][2], vals[i][2], vals[i][0]]
        bars += (_label(14, y + 6, name, C["muted"], 8)
                 + f'<rect x="64" y="{y}" width="132" height="7" rx="3.5" fill="{C["line"]}"/>'
                 f'<rect x="64" y="{y}" height="7" rx="3.5" fill="{col}" width="0">'
                 f'<animate attributeName="width" dur="9s" repeatCount="indefinite" keyTimes="{keys}" '
                 f'values="{";".join(f"{132 * v:.1f}" for v in seq)}"/></rect>')
    scene = (_live("LIVE · webcam") + _label(206, 18.5, "TFLite · on-device", C["dim"], 8, "end")
             + face + box + laser + _label(62, 146, "age ~26", C["lime"], 8, extra='font-weight="700"') + bars)
    defs = (f'<linearGradient id="trail" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["lime"]}" '
            f'stop-opacity="0"/><stop offset="1" stop-color="{C["lime"]}" stop-opacity=".3"/></linearGradient>')
    style = (".scan{animation:scan 2.4s ease-in-out infinite alternate}@keyframes scan{from{transform:translateY(8px)}to{transform:translateY(112px)}}"
             ".lm{animation:lm 2s ease-in-out infinite}@keyframes lm{50%{opacity:.25}}"
             ".eye{transform-box:fill-box;transform-origin:center;animation:eye 4s infinite}"
             "@keyframes eye{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}")
    return card(2, "EDGE AI · COMPUTER VISION", ["Age · Gender ·", "Emotion Recognition"],
                ["Webcam + image face analysis that",
                 "runs 100% local. Benchmarked CPU/GPU/",
                 "edge, exported to TFLite for mobile."],
                ["TensorFlow", "OpenCV", "DeepFace"], "violet", scene, style, defs,
                aria="Card: a glowing face mesh under a laser scan; expression and emotion bars cycle happy, neutral, surprise.")


# --- 03  Video object detection ---------------------------------------------------
def video():
    rnd = random.Random(21)
    hz = 96
    sky = ""
    x = 0
    while x < VS:
        w, h = rnd.randint(14, 30), rnd.randint(16, 52)
        sky += f'<rect x="{x}" y="{hz - h}" width="{w}" height="{h}" fill="#0b1020" stroke="{C["line"]}"/>'
        for _ in range(rnd.randint(1, 4)):
            wx, wy = x + rnd.randint(3, w - 5), hz - rnd.randint(5, h - 4)
            sky += (f'<rect x="{wx}" y="{wy}" width="2.5" height="3" fill="{C["amber"]}" class="win" '
                    f'style="animation-delay:-{rnd.uniform(0, 6):.1f}s"/>')
        x += w + rnd.randint(1, 4)
    ground = (f'<rect y="{hz}" width="{VS}" height="{VS - hz}" fill="#070a14"/>'
              + "".join(f'<line x1="108" y1="{hz}" x2="{x2}" y2="{VS}" stroke="{C["line"]}"/>'
                        for x2 in range(-216, 433, 54))
              + f'<line x1="0" x2="{VS}" y1="{hz}" y2="{hz}" stroke="{C["violet"]}" stroke-opacity=".5"/>')

    def walker(x_from, x_to, y, s, dur, delay, tid, conf, col):
        def leg(phase):
            return (f'<g><animateTransform attributeName="transform" type="rotate" '
                    f'values="{phase} 0 {-8 * s:.1f};{-phase} 0 {-8 * s:.1f};{phase} 0 {-8 * s:.1f}" dur=".75s" repeatCount="indefinite"/>'
                    f'<path d="M0,{-8 * s:.1f} L0,{9 * s:.1f}" stroke="#cbd5e1" stroke-width="{3.4 * s:.1f}" stroke-linecap="round"/></g>')
        body = (leg(24) + leg(-24)
                + f'<rect x="{-5 * s:.1f}" y="{-29 * s:.1f}" width="{10 * s:.1f}" height="{22 * s:.1f}" rx="{4 * s:.1f}" fill="#cbd5e1"/>'
                + f'<circle cy="{-35 * s:.1f}" r="{5.5 * s:.1f}" fill="#cbd5e1"/>')
        bx0, by0, bx1, by1 = -13 * s, -44 * s, 13 * s, 12 * s
        lbl = f"#{tid} person {conf}"
        box = (f'<rect x="{bx0:.1f}" y="{by0:.1f}" width="{bx1 - bx0:.1f}" height="{by1 - by0:.1f}" fill="{col}" fill-opacity=".1"/>'
               + _brackets(bx0, by0, bx1, by1, col, 6 * s, 1.6)
               + f'<rect x="{bx0:.1f}" y="{by0 - 12:.1f}" width="{mono_w(lbl, 7.5) + 6:.1f}" height="11" rx="2" fill="{col}"/>'
               + f'<text x="{bx0 + 3:.1f}" y="{by0 - 4:.1f}" font-size="7.5" font-weight="700" fill="{C["bg"]}">{lbl}</text>')
        return (f'<g><animateTransform attributeName="transform" type="translate" from="{x_from} {y}" to="{x_to} {y}" '
                f'dur="{dur}s" begin="-{delay}s" repeatCount="indefinite"/>{body}{box}</g>')

    scene = (f'<rect width="{VS}" height="{hz}" fill="url(#vsky)"/>{sky}{ground}'
             + walker(-30, 250, 132, .75, 9, 2, "03", ".88", C["cyan"])
             + walker(250, -30, 162, .95, 7.5, 5, "02", ".91", C["violet"])
             + walker(-30, 250, 200, 1.2, 5.5, 1.2, "01", ".97", C["pink"])
             + _live("REC  MOT17-04") + _label(206, 30, "FPS 30 · tracked 3", C["dim"], 7.5, "end"))
    for i, m in enumerate(["YOLOv8", "Faster R-CNN", "SSD"]):
        scene += f'<g class="mdl" style="animation-delay:{i * 2}s">' + _label(206, 18.5, m, C["lime"], 8.5, "end", 'font-weight="700"') + "</g>"
    defs = (f'<linearGradient id="vsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["bg"]}"/>'
            f'<stop offset="1" stop-color="#1c0f3a"/></linearGradient>')
    style = (".mdl{opacity:0;animation:mdl 6s steps(1) infinite}@keyframes mdl{0%{opacity:1}33.3%,100%{opacity:0}}"
             ".win{animation:win 6s steps(1) infinite}@keyframes win{0%,70%{opacity:.8}71%,100%{opacity:.15}}")
    return card(3, "COMPUTER VISION", ["Video Object", "Detection"],
                ["Person detection & tracking across",
                 "video frames: YOLOv8 vs Faster R-CNN",
                 "vs SSD, with GUI and eval metrics."],
                ["PyTorch", "YOLOv8", "OpenCV"], "pink", scene, style, defs,
                aria="Card: silhouettes walk down a night street, each tracked by a numbered person bounding box.")


# --- 04  Sentiment analysis --------------------------------------------------------
def sentiment():
    words = [("\"a masterpiece\"", True), ("\"painfully boring\"", False),
             ("\"loved every minute\"", True), ("\"waste of time\"", False)]
    dur = 10
    scene = ""
    for i, (w, pos) in enumerate(words):
        col = C["lime"] if pos else C["red"]
        toks = w.strip('"').split()
        chips, tx = "", 108 - sum(mono_w(t, 8) + 12 for t in toks) / 2
        for t in toks:
            tw = mono_w(t, 8) + 8
            chips += (f'<rect x="{tx:.1f}" y="46" width="{tw:.1f}" height="13" rx="3" fill="{C["panel"]}" stroke="{C["line"]}"/>'
                      f'<text x="{tx + 4:.1f}" y="55.5" font-size="8" fill="{C["text"]}">{esc(t)}</text>')
            tx += tw + 4
        scene += (f'<g class="wd" style="animation-delay:{i * dur / 4}s">'
                  f'<text x="108" y="36" font-size="12" text-anchor="middle" fill="{col}" font-weight="700">{esc(w)}</text>'
                  f'{chips}</g>')
    scene += _label(108, 74, "tokenize -> lemmatize -> Naive Bayes", C["dim"], 7.5, "middle")
    gx, gy, r = 108, 168, 64
    arc = f"M{gx - r},{gy} A{r},{r} 0 0 1 {gx + r},{gy}"
    ticks = "".join(
        f'<line x1="{gx + (r - 9) * math.cos(math.pi * (1 - k / 10)):.1f}" y1="{gy - (r - 9) * math.sin(math.pi * (1 - k / 10)):.1f}" '
        f'x2="{gx + (r - 4) * math.cos(math.pi * (1 - k / 10)):.1f}" y2="{gy - (r - 4) * math.sin(math.pi * (1 - k / 10)):.1f}" '
        f'stroke="{C["dim"]}" stroke-width="1.5"/>' for k in range(11))
    seq, keys = [-55], [0]
    for i, a in enumerate([55, -55, 55, -55]):
        seq += [a, a]
        keys += [i / 4 + .06, i / 4 + .25]
    seq.append(-55)
    keys.append(1)
    needle = (f'<g filter="url(#glow)"><animateTransform attributeName="transform" type="rotate" dur="{dur}s" repeatCount="indefinite" '
              f'values="{";".join(f"{a} {gx} {gy}" for a in seq)}" keyTimes="{";".join(f"{k:.3f}" for k in keys)}" '
              f'calcMode="spline" keySplines="{";".join([".4 0 .2 1"] * (len(keys) - 1))}"/>'
              f'<line x1="{gx}" y1="{gy}" x2="{gx}" y2="{gy - r + 16}" stroke="#fff" stroke-width="3" stroke-linecap="round"/></g>')
    scene += (f'<path d="{arc}" fill="none" stroke="url(#sentg)" stroke-width="16" stroke-opacity=".18" filter="url(#softglow)"/>'
              f'<path d="{arc}" fill="none" stroke="url(#sentg)" stroke-width="9" stroke-linecap="round"/>{ticks}{needle}'
              f'<circle cx="{gx}" cy="{gy}" r="6" fill="{C["text"]}"/>'
              + _label(gx - r, gy + 20, "NEG", C["red"], 9, "middle", 'font-weight="700"')
              + _label(gx + r, gy + 20, "POS", C["lime"], 9, "middle", 'font-weight="700"')
              + _label(gx, gy + 32, "IMDB · acc 84%+", C["muted"], 8.5, "middle"))
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
                aria="Card: review quotes split into tokens and a glowing sentiment gauge swings to negative or positive.")


# --- 05  Terraform on AWS -----------------------------------------------------------
def terraform():
    packets = "".join(
        f'<circle r="2.6" fill="{C["cyan2"]}" filter="url(#glow)"><animateMotion dur="1.6s" begin="{b}s" '
        f'repeatCount="indefinite" path="{p}"/></circle>'
        for p, b in [("M108,146 L64,122", 0), ("M108,146 L152,122", .8), ("M108,196 L108,172", .4)])
    els = [
        ('<rect x="14" y="44" width="188" height="140" rx="8" fill="{v}" fill-opacity=".05" stroke="{v}" stroke-dasharray="4 3"/>'
         '<text x="22" y="58" font-size="9" fill="{v}">vpc 10.0.0.0/16</text>'),
        ('<rect x="24" y="66" width="80" height="70" rx="5" fill="{p}" stroke="{d}"/>'
         '<text x="30" y="78" font-size="8" fill="{m}">subnet-a · az1</text>'),
        ('<rect x="112" y="66" width="80" height="70" rx="5" fill="{p}" stroke="{d}"/>'
         '<text x="118" y="78" font-size="8" fill="{m}">subnet-b · az2</text>'),
        ('<rect x="44" y="88" width="40" height="34" rx="4" fill="{a}" fill-opacity=".12" stroke="{a}" stroke-width="1.6"/>'
         '<text x="64" y="109" font-size="9" fill="{a}" text-anchor="middle" font-weight="700">EC2</text>'),
        ('<rect x="132" y="88" width="40" height="34" rx="4" fill="{a}" fill-opacity=".12" stroke="{a}" stroke-width="1.6"/>'
         '<text x="152" y="109" font-size="9" fill="{a}" text-anchor="middle" font-weight="700">EC2</text>'),
        ('<path d="M92,146 L64,122 M124,146 L152,122 M108,196 L108,172" stroke="{c}" stroke-dasharray="3 3"/>'
         '<rect x="78" y="146" width="60" height="26" rx="13" fill="{bg}" stroke="{c}" stroke-width="1.6"/>'
         '<text x="108" y="163" font-size="9" fill="{c}" text-anchor="middle" font-weight="700">ELB</text>' + packets),
        ('<text x="196" y="182" font-size="8" fill="{l}" text-anchor="end">ASG 2..4</text>'),
    ]
    fmt = dict(v=C["violet"], p=C["panel"], d=C["line"], m=C["muted"], a=C["amber"], c=C["cyan"], l=C["lime"],
               bg=C["bg"])
    n = len(els)
    style = ""
    scene = (_label(12, 20, "$ terraform apply -auto-approve", C["text"], 9.5)
             + f'<text x="12" y="34" font-size="8.5" fill="{C["muted"]}">+ creating resources'
             f'<tspan class="blink">_</tspan></text>')
    for i, e in enumerate(els):
        p = 8 + i * 8
        style += (f"@keyframes tf{i}{{0%,{p}%{{opacity:0;transform:translateY(6px)}}{p + 4}%,92%{{opacity:1;transform:none}}"
                  f"100%{{opacity:0}}}}.tf{i}{{animation:tf{i} 9s ease-out infinite}}")
        scene += f'<g class="tf{i}">{e.replace("{packets}", "").format(**fmt) if "{" in e else e}</g>'
    pd = 8 + n * 8 + 4
    style += (f"@keyframes done{{0%,{pd}%{{opacity:0}}{pd + 3}%,92%{{opacity:1}}100%{{opacity:0}}}}"
              ".done{animation:done 9s steps(1) infinite}")
    scene += (f'<g class="done">' + _label(12, 207, f"Apply complete! Resources: {n} added.", C["lime"], 9,
                                           extra='font-weight="700"') + "</g>")
    return card(5, "CLOUD · IaC", ["Terraform", "AWS Infrastructure"],
                ["VPC, multi-AZ subnets, an ELB and an",
                 "Auto Scaling Group of EC2 web servers,",
                 "all from a single terraform apply."],
                ["Terraform", "AWS", "HCL"], "amber", scene, style,
                aria="Card: terraform apply draws a VPC, subnets, EC2 instances and a load balancer, then traffic flows through it.")


# --- 06  Superspeed Seeds -----------------------------------------------------------
def seeds():
    rnd = random.Random(9)

    def skyline(seed, hmin, hmax, fill, stroke, neon):
        r, out, x = random.Random(seed), "", 0
        while x < 432:
            w, h = r.randint(14, 30), r.randint(hmin, hmax)
            out += f'<rect x="{x}" y="{168 - h}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>'
            if neon and r.random() < .5:
                out += f'<rect x="{x + 3}" y="{168 - h + 4}" width="{w - 6}" height="2" fill="{r.choice([C["pink"], C["cyan"]])}" opacity=".7"/>'
            x += w
        return out

    far = skyline(1, 30, 80, "#0d0b22", "#1a1640", False)
    near = skyline(2, 18, 50, "#090b18", C["line"], True)
    rain = "".join(f'<line class="rain" x1="{x:.0f}" y1="{y:.0f}" x2="{x - 6:.0f}" y2="{y + 12:.0f}" '
                   f'stroke="{C["cyan2"]}" stroke-opacity=".3"/>'
                   for x, y in [(rnd.uniform(0, 240), rnd.uniform(-20, 170)) for _ in range(26)])
    road = (f'<rect y="168" width="{VS}" height="48" fill="#070912"/>'
            f'<line x1="0" x2="{VS}" y1="168" y2="168" stroke="{C["pink"]}" stroke-width="2" filter="url(#glow)"/>'
            f'<g class="dash">' + "".join(f'<rect x="{x}" y="190" width="24" height="3" rx="1.5" fill="{C["dim"]}"/>'
                                          for x in range(0, 460, 46)) + '</g>')
    pod = (f'<g class="bob"><g transform="translate(64,138)">'
           f'<path class="flame" d="M-22,-4 Q-46,0 -22,4 Z" fill="{C["cyan"]}" filter="url(#glow)"/>'
           f'<ellipse rx="26" ry="16" fill="{C["amber"]}" opacity=".35" filter="url(#softglow)"/>'
           f'<ellipse rx="22" ry="14" fill="url(#podg)"/>'
           f'<ellipse cx="-5" cy="-4" rx="12" ry="5" fill="#fff" opacity=".35"/>'
           f'<path d="M8,-13 q12,-16 22,-7 q-9,3 -22,7Z" fill="{C["lime"]}"/></g></g>')
    collect = "".join(
        f'<circle cy="138" r="3.2" fill="{C["amber"]}" filter="url(#glow)">'
        f'<animate attributeName="cx" from="236" to="-20" dur="2.6s" begin="-{b}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.66;.68;1" dur="2.6s" begin="-{b}s" repeatCount="indefinite"/>'
        f'</circle>' for b in (0, .9, 1.7))

    def fudder(y, dur, delay, laser=False):
        eye = '<circle cx="-4" cy="-2" r="2.4" fill="#fff"/><circle cx="4" cy="-2" r="2.4" fill="#fff"/>'
        beam = (f'<line x1="-12" y1="0" x2="-60" y2="0" stroke="{C["red"]}" stroke-width="2" class="blink" '
                f'filter="url(#glow)"/>' if laser else "")
        return (f'<g><animateTransform attributeName="transform" type="translate" from="250 {y}" to="-40 {y}" '
                f'dur="{dur}s" begin="-{delay}s" repeatCount="indefinite"/>{beam}'
                f'<path d="M-10,6 Q-12,-10 0,-11 Q12,-10 10,6 L6,2 L3,7 L0,2 L-3,7 L-6,2Z" fill="{C["pink"]}"/>{eye}</g>')

    scene = (f'<rect width="{VS}" height="168" fill="url(#cyber)"/>'
             f'<g class="par1">{far}</g><g class="par2">{near}</g>{rain}{road}'
             + collect + fudder(96, 3.6, .4, laser=True) + fudder(158, 2.8, 1.9) + pod
             + _label(10, 20, "LVL 37/100", C["lime"], 10, extra='font-weight="700"')
             + _label(206, 20, "SEEDS 128", C["amber"], 10, "end", 'font-weight="700"')
             + _label(10, 33, "world: CYBER · weather: rain", C["muted"], 7.5))
    defs = (f'<linearGradient id="cyber" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["bg"]}"/>'
            f'<stop offset="1" stop-color="#2a0f3f"/></linearGradient>'
            f'<radialGradient id="podg" cx=".35" cy=".3"><stop offset="0" stop-color="#fde68a"/>'
            f'<stop offset="1" stop-color="{C["amber"]}"/></radialGradient>')
    style = (".par1{animation:p1 24s linear infinite}@keyframes p1{to{transform:translateX(-216px)}}"
             ".par2{animation:p2 10s linear infinite}@keyframes p2{to{transform:translateX(-216px)}}"
             ".dash{animation:dash .7s linear infinite}@keyframes dash{to{transform:translateX(-46px)}}"
             ".bob{animation:bob 1.4s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-14px)}}"
             ".flame{transform-box:fill-box;transform-origin:right center;animation:fl .12s steps(2) infinite alternate}"
             "@keyframes fl{to{transform:scaleX(.6)}}"
             ".rain{animation:rain .8s linear infinite}@keyframes rain{to{transform:translate(-12px,24px)}}")
    return card(6, "GAME DEV", ["Superspeed Seeds:", "Racing Royale"],
                ["A 100-level seed-powered racer with",
                 "Fudders, wild weather & 4 SeedDrivers.",
                 "Built for the SuperSeed Tesla Contest."],
                ["Python", "Game Dev", "100 levels"], "lime", scene, style, defs,
                aria="Card: a glowing seed pod races through a rainy cyber city collecting seeds while Fudders fly past.")


# --- 07  Habit tracker -----------------------------------------------------------------
def habits():
    rnd = random.Random(11)
    cols, rows, s, g = 7, 7, 12, 3
    x0, y0 = 14, 36
    cells = ""
    for c in range(cols):
        for r in range(rows):
            idx = c * rows + r
            lvl = rnd.choice([1, 2, 3, 3, 4, 4, 4]) if idx % 9 != 4 else 0
            col = [C["line"], "#365314", "#4d7c0f", "#65a30d", C["lime"]][lvl]
            x, y = x0 + c * (s + g), y0 + r * (s + g)
            cells += f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="3" fill="{C["line"]}"/>'
            if lvl:
                cells += (f'<rect class="hc" x="{x}" y="{y}" width="{s}" height="{s}" rx="3" fill="{col}" '
                          f'style="animation-delay:{idx * .09:.2f}s"/>')
    cx, cy, rad = 164, 86, 32
    circ = 2 * math.pi * rad
    ring = (f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="{C["line"]}" stroke-width="8"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="{C["lime"]}" stroke-width="8" stroke-linecap="round" '
            f'stroke-dasharray="{circ:.1f}" transform="rotate(-90 {cx} {cy})" filter="url(#glow)">'
            f'<animate attributeName="stroke-dashoffset" dur="8s" repeatCount="indefinite" keyTimes="0;.55;.9;1" '
            f'values="{circ:.1f};{circ * .13:.1f};{circ * .13:.1f};{circ:.1f}" calcMode="spline" '
            f'keySplines=".3 0 .2 1;0 0 1 1;.4 0 1 1"/></circle>'
            + _label(cx, cy + 4, "87%", "#fff", 15, "middle", 'font-weight="700"')
            + _label(cx, cy + 16, "this month", C["muted"], 7, "middle"))
    checks = ""
    for i, h in enumerate(["read 20 pages", "workout", "ship 1 commit"]):
        y = 160 + i * 16
        checks += (f'<rect x="14" y="{y - 8}" width="10" height="10" rx="2" fill="none" stroke="{C["lime"]}"/>'
                   f'<path class="ck" d="M16,{y - 3} l3,3 l5,-6" fill="none" stroke="{C["lime"]}" stroke-width="2" '
                   f'style="animation-delay:{1 + i * .6:.1f}s"/>' + _label(30, y + 1, h, C["text"], 8.5))
    scene = (_label(14, 22, "$ habit analyze --all", C["text"], 9.5) + cells + ring + checks
             + _label(206, 168, "streak", C["muted"], 8, "end") + _label(206, 184, "21 days", C["lime"], 11, "end", 'font-weight="700"')
             + _label(206, 200, "best 42", C["cyan"], 8.5, "end"))
    style = (".hc{opacity:0;animation:hc 8s steps(1) infinite}@keyframes hc{0%{opacity:0}1%,88%{opacity:1}100%{opacity:0}}"
             ".ck{stroke-dasharray:14;stroke-dashoffset:14;animation:ck 8s ease-out infinite}"
             "@keyframes ck{0%{stroke-dashoffset:14}6%,88%{stroke-dashoffset:0}100%{stroke-dashoffset:14}}")
    return card(7, "PYTHON APP", ["Habit Tracker"],
                ["Create habits, log completions and",
                 "analyze current & longest streaks,",
                 "daily or weekly. Clean OOP Python."],
                ["Python", "OOP", "Analytics"], "lime", scene, style,
                aria="Card: a streak calendar fills up, a progress ring climbs to 87 percent and habits get checked off.")


# --- 08  Classified -----------------------------------------------------------------------
def classified():
    cx, cy = 108, 98
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["red"]}" stroke-opacity=".3"/>'
                    for r in (22, 46, 70))
    cross = (f'<line x1="{cx - 78}" x2="{cx + 78}" y1="{cy}" y2="{cy}" stroke="{C["red"]}" stroke-opacity=".2"/>'
             f'<line x1="{cx}" x2="{cx}" y1="{cy - 78}" y2="{cy + 78}" stroke="{C["red"]}" stroke-opacity=".2"/>')
    sweep = (f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" '
             f'dur="4s" repeatCount="indefinite"/>'
             f'<path d="M{cx},{cy} L{cx + 72},{cy} A72,72 0 0 0 {cx + 72 * math.cos(math.radians(-40)):.1f},'
             f'{cy + 72 * math.sin(math.radians(-40)):.1f} Z" fill="url(#sweepg)"/>'
             f'<line x1="{cx}" y1="{cy}" x2="{cx + 72}" y2="{cy}" stroke="{C["red"]}" stroke-width="1.5" filter="url(#glow)"/></g>')
    blips = ""
    for a, d in [(30, 50), (140, 34), (250, 60), (320, 26)]:
        bx, by = cx + d * math.cos(math.radians(a)), cy + d * math.sin(math.radians(a))
        blips += (f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="3.5" fill="{C["red"]}" class="blip" filter="url(#glow)" '
                  f'style="animation-delay:{(a / 360) * 4:.2f}s"/>')
    rnd = random.Random(8)
    hexes = "".join(_label(10 + c * 50, 20 + r * 11, "".join(rnd.choice("0123456789ABCDEF") for _ in range(6)),
                           C["red"], 7, extra='opacity=".18"') for c in range(4) for r in range(18))
    denied = (f'<g class="deny"><rect x="40" y="{cy - 12}" width="136" height="22" fill="{C["bg"]}" stroke="{C["red"]}"/>'
              + _label(108, cy + 3, "ACCESS DENIED", C["red"], 11, "middle", 'font-weight="700"') + "</g>")
    scene = (hexes + rings + cross + sweep + blips + denied
             + f'<rect x="38" y="186" width="140" height="20" rx="3" fill="none" stroke="{C["red"]}" class="redact"/>'
             + _label(108, 200, "CLEARANCE REQUIRED", C["red"], 9.5, "middle", 'font-weight="700"'))
    defs = (f'<linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["red"]}" stop-opacity=".05"/>'
            f'<stop offset="1" stop-color="{C["red"]}" stop-opacity=".55"/></linearGradient>')
    style = (".blip{opacity:0;animation:blip 4s ease-out infinite}@keyframes blip{0%{opacity:1}60%,100%{opacity:0}}"
             ".deny{opacity:0;animation:deny 6s steps(1) infinite}"
             "@keyframes deny{0%,72%{opacity:0}73%{opacity:1;transform:translateX(-3px)}75%{transform:translateX(3px)}"
             "77%,88%{opacity:1;transform:none}89%,100%{opacity:0}}")
    return card(8, "STEALTH MODE", [[("Project ", False), ("████████", True)], "in progress"],
                [[("A browser ", False), ("████████", True), (" with on-chain", False)],
                 [("████████", True), (". Contracts, game loop,", False)],
                 [("the whole stack. Reveal: soon", False), ("™", False)]],
                ["TypeScript", "Solidity", "????"], "red", scene, style, defs,
                aria="Card: a redacted stealth project with a radar sweep, hex noise and an access denied flash.")


def build_all():
    return [("01-iot", iot()), ("02-emotion", emotion()), ("03-video", video()), ("04-sentiment", sentiment()),
            ("05-terraform", terraform()), ("06-seeds", seeds()), ("07-habits", habits()),
            ("08-classified", classified())]
