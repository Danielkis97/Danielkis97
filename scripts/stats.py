"""Render assets/generated/stats.svg from the GitHub GraphQL API (no third-party services).

Usage: python scripts/stats.py [dist/snake-dark.svg]
Env: GH_TOKEN (or GITHUB_TOKEN), optional GH_LOGIN (default Danielkis97).
A personal token with `repo` scope also counts private repos' languages; the
Action's built-in token only sees public ones.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
import snake  # noqa: E402
from art_common import C, esc, frame, frame_defs, mono_w, svg, write  # noqa: E402

LOGIN = os.environ.get("GH_LOGIN", "Danielkis97")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      nodes {
        isPrivate
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today not counted yet doesn't break the streak
        i -= 1
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    return current, longest


def render(u, snake_raw=None):
    W, H = 1200, 360
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    total = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    days = [d for w in weeks for d in w["contributionDays"]]
    cur, longest = streaks(days)
    repos = u["repositories"]["nodes"]
    public = sum(1 for r in repos if not r["isPrivate"])
    stars = sum(r["stargazerCount"] for r in repos)

    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or C["muted"]])[0] += e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    lang_total = sum(v[0] for _, v in top) or 1

    tiles = [("contributions", f"{total:,}", "last 12 months", C["cyan"]),
             ("current streak", f"{cur}d", "keep it alive", C["lime"]),
             ("longest streak", f"{longest}d", "personal best", C["pink"]),
             ("repositories", f"{len(repos)}", f"{public} public · {stars} stars", C["violet"])]
    body = frame(W, H)
    body += (f'<text x="40" y="44" font-size="15" fill="{C["muted"]}"><tspan fill="{C["lime"]}">$</tspan> '
             f'git log --stats <tspan fill="{C["dim"]}">--since=1.year</tspan></text>'
             f'<text x="{W - 40}" y="44" font-size="12" fill="{C["dim"]}" text-anchor="end">'
             f'updated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC</text>')
    tw = (W - 80 - 3 * 16) / 4
    for i, (label, value, sub, col) in enumerate(tiles):
        x = 40 + i * (tw + 16)
        body += (f'<g class="tile" style="animation-delay:{i * .12:.2f}s">'
                 f'<rect x="{x:.1f}" y="66" width="{tw:.1f}" height="104" rx="12" fill="{C["panel"]}" stroke="{C["line"]}"/>'
                 f'<rect x="{x:.1f}" y="66" width="{tw:.1f}" height="3" rx="1.5" fill="{col}" class="bar" '
                 f'style="animation-delay:{.3 + i * .12:.2f}s"/>'
                 f'<text x="{x + 20:.1f}" y="96" font-size="12" fill="{C["muted"]}">{esc(label)}</text>'
                 f'<text x="{x + 20:.1f}" y="138" font-size="34" font-weight="700" fill="{col}">{esc(value)}</text>'
                 f'<text x="{x + 20:.1f}" y="158" font-size="11" fill="{C["dim"]}">{esc(sub)}</text></g>')

    s, g = 9, 2
    hx, hy = 40, 200
    if snake_raw:
        # the snake eats the real contribution grid right inside the card
        body += (f'<text x="{hx}" y="{hy - 10}" font-size="12" fill="{C["muted"]}">contribution heatmap '
                 f'<tspan fill="{C["dim"]}">// fed to the snake daily</tspan></text>')
        grid, gh = snake.nest(snake_raw, hx - 8, hy - 18, 600)
        body += grid
    else:
        levels = [C["line"], "#3b0764", "#6d28d9", "#a855f7", C["pink"]]
        peak = max((d["contributionCount"] for d in days), default=1) or 1
        cells = ""
        for wi, w in enumerate(weeks[-53:]):
            for d in w["contributionDays"]:
                c = d["contributionCount"]
                lvl = 0 if c == 0 else min(4, 1 + int(3 * c / peak))
                wd = dt.date.fromisoformat(d["date"]).isoweekday() % 7
                cells += (f'<rect class="hm" x="{hx + wi * (s + g)}" y="{hy + wd * (s + g)}" width="{s}" height="{s}" '
                          f'rx="2" fill="{levels[lvl]}" style="animation-delay:{wi * .05:.2f}s"/>')
        body += f'<text x="{hx}" y="{hy - 10}" font-size="12" fill="{C["muted"]}">contribution heatmap</text>{cells}'
        body += (f'<text x="{hx}" y="{hy + 7 * (s + g) + 22}" font-size="11" fill="{C["dim"]}">less</text>'
                 + "".join(f'<rect x="{hx + 34 + i * 13}" y="{hy + 7 * (s + g) + 13}" width="10" height="10" rx="2" fill="{c}"/>'
                           for i, c in enumerate(levels))
                 + f'<text x="{hx + 34 + 5 * 13 + 4}" y="{hy + 7 * (s + g) + 22}" font-size="11" fill="{C["dim"]}">more</text>')

    # top languages
    lx, ly, lw = 680, 200, 480
    body += f'<text x="{lx}" y="{ly - 10}" font-size="12" fill="{C["muted"]}">top languages</text>'
    x = lx
    for i, (name, (size, col)) in enumerate(top):
        w = lw * size / lang_total
        body += (f'<rect class="seg" x="{x:.1f}" y="{ly}" width="{max(w - 2, 1):.1f}" height="12" rx="3" fill="{col}" '
                 f'style="animation-delay:{.4 + i * .1:.2f}s"/>')
        x += w
    for i, (name, (size, col)) in enumerate(top):
        cx, cy = lx + (i % 2) * 240, ly + 40 + (i // 2) * 24
        pct = 100 * size / lang_total
        body += (f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{col}"/>'
                 f'<text x="{cx + 18}" y="{cy}" font-size="13" fill="{C["text"]}">{esc(name)}'
                 f'<tspan fill="{C["muted"]}"> {pct:.1f}%</tspan></text>')

    style = """
.tile{animation:rise .7s cubic-bezier(.2,.8,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.bar,.seg{transform-box:fill-box;transform-origin:left;animation:grow 1.1s cubic-bezier(.2,.8,.2,1) both}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.hm{animation:wave 5.3s ease-in-out infinite}
@keyframes wave{0%,100%{opacity:1}8%{opacity:.35}16%{opacity:1}}
"""
    return svg(W, H, body, "GitHub stats",
               f"{total} contributions in the last year, current streak {cur} days, longest streak {longest} days, "
               f"{len(repos)} repositories. Top languages: " + ", ".join(n for n, _ in top) + ".",
               style=style, defs=frame_defs())


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("set GH_TOKEN or GITHUB_TOKEN")
    snake_raw = None
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], encoding="utf-8") as f:
            snake_raw = f.read()
    write("generated/stats.svg", render(fetch(), snake_raw))
