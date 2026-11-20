#!/usr/bin/env python3
"""news-image-20261119 — full-day rebuild, written fresh 20 Nov 2026.

One-image newspaper front page summing up Thursday 19 November 2026:
44 verified stories, 7 regions, 3 illustrated leads, 10 illustrated
tiles, a world map with numbered pins, 31 numbered briefs and a
date-check footer. PIL only — no network, no randomness, no clock,
no image model. Every picture on the page is a geometric scene drawn
in code, so no text can come out garbled.

Layout (1024x1024): masthead, region count bar, day-in-numbers strip,
lead 1 (full width), leads 2-3 (two columns), 10 tiles (5x2 grid),
world map, 31 briefs (3 columns), date-check footer.

Usage: python3 main.py [output.png]   (default: entry.png)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24                       # outer margin
CW = W - 2 * M               # content width: 976

PAPER = (251, 246, 236)
INK = (20, 20, 20)
MUTED = (96, 92, 84)
RULE = (20, 20, 20)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
SEA = (213, 231, 241)
LAND = (233, 221, 196)
LAND_EDGE = (186, 171, 136)
GOLD = (176, 141, 60)
GREEN = (46, 110, 69)
PURPLE = (107, 78, 142)
TEAL = (46, 127, 134)
GREY = (85, 85, 85)
PANEL = (241, 233, 216)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF = FONT_DIR + "DejaVuSerif-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANS_B = FONT_DIR + "DejaVuSans-Bold.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, lines, fnt, fill=INK, leading=None):
    """Draw lines top-to-bottom; return y just below the last line."""
    if leading is None:
        leading = fnt.size + 3
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def badge(d, x, y, n, size=18):
    """Small red square with a white story number."""
    d.rectangle([x, y, x + size - 1, y + size - 1], fill=RED)
    fnt = font(SANS_B, 11 if size <= 18 else 13)
    s = str(n)
    tw = fnt.getlength(s)
    th = fnt.getbbox(s)[3] - fnt.getbbox(s)[1]
    d.text((x + (size - tw) / 2, y + (size - th) / 2 - 1), s,
           font=fnt, fill=(255, 255, 255))


def rule(d, x0, y, x1, weight=2):
    d.line([(x0, y), (x1, y)], fill=RULE, width=weight)


# ---------------------------------------------------------------- data
# n, kind, region, kicker, headline, body, scene, lon, lat.
# Leads 1-3 and tiles 4-13 carry a map pin (lon/lat); briefs 14-44 are
# one-liners. Regions are counted by the code; the bar must sum to 44.
STORIES = [
    dict(n=1, kind="lead", region="Asia-Pacific",
         kicker="SUMMIT IN SHENZHEN",
         head="Trump, Xi and Putin meet in Shenzhen",
         body="The three leaders hold their first three-way summit and sign "
              "a joint peace declaration - the day's biggest diplomatic "
              "set-piece.",
         scene="summit", lon=114.05, lat=22.55),
    dict(n=2, kind="lead", region="Asia-Pacific",
         kicker="THE HAGUE",
         head="World Court: Myanmar guilty of genocide",
         body="The International Court of Justice rules 9-6 against Myanmar "
              "over the Rohingya - the first state ever held responsible "
              "for genocide.",
         scene="scales", lon=4.30, lat=52.08),
    dict(n=3, kind="lead", region="Global",
         kicker="COP31",
         head="COP31 draft drops fossil fuels",
         body="The climate summit's draft text cuts all fossil-fuel language "
              "as negotiators slash 144 paragraphs down to 80.",
         scene="leaf", lon=30.70, lat=36.90),
    dict(n=4, kind="tile", region="Americas",
         head="GTA VI goes on sale after 13 years",
         body="The decade's most awaited game arrives - 99 on Metacritic.",
         scene="city", lon=-74.00, lat=40.70),
    dict(n=5, kind="tile", region="Americas",
         head="Anthropic debuts on Nasdaq",
         body="Priced $83, closes $97.17, up 17.1% - the largest IPO ever.",
         scene="chart", lon=-122.40, lat=37.80),
    dict(n=6, kind="tile", region="Americas",
         head="Wall Street plunges 1,101 points",
         body="The Dow sheds 1,101 points in a brutal session.",
         scene="fall", lon=-74.01, lat=40.71),
    dict(n=7, kind="tile", region="Middle East",
         head="Houthi missile shot down over Riyadh",
         body="Saudi defences intercept a missile over the capital.",
         scene="burst", lon=46.70, lat=24.70),
    dict(n=8, kind="tile", region="Europe",
         head="Ukraine hits the Crimea bridge again",
         body="Kyiv strikes the Kerch crossing for a second time.",
         scene="bridge", lon=35.40, lat=45.30),
    dict(n=9, kind="tile", region="Middle East",
         head="Israeli tanks cross into central Gaza",
         body="Armour pushes into the centre of the Strip.",
         scene="tank", lon=34.45, lat=31.50),
    dict(n=10, kind="tile", region="Middle East",
         head="Iran and US trade strikes in the Gulf",
         body="Tehran and Washington exchange fire across the Gulf.",
         scene="ship", lon=56.30, lat=26.60),
    dict(n=11, kind="tile", region="Asia-Pacific",
         head="Deadly unrest grips Bangladesh",
         body="Protests turn deadly across the country.",
         scene="crowd", lon=90.40, lat=23.80),
    dict(n=12, kind="tile", region="Africa",
         head="Somalia expels the UAE ambassador",
         body="Mogadishu orders the Emirati envoy out.",
         scene="flag", lon=45.30, lat=2.00),
    dict(n=13, kind="tile", region="Asia-Pacific",
         head="Cyclone Akvan nears India's coast",
         body="More than 80,000 people evacuated as the storm closes in.",
         scene="cyclone", lon=88.00, lat=16.00),
]

BRIEFS = [
    (14, "Africa", "Ethiopia-Eritrea troop build-up on the border"),
    (15, "Europe", "Netherlands summons Russia's envoy"),
    (16, "Europe", "Denmark backs US Arctic pact on Greenland, 109-0"),
    (17, "Africa", "Migrant boat capsizes off Senegal"),
    (18, "Africa", "Ebola in DR Congo passes 2,280 cases"),
    (19, "Asia-Pacific", "550,000+ South Koreans sit the college exam"),
    (20, "Asia-Pacific", "Magnitude 5.7 quake shakes Kumamoto"),
    (21, "Asia-Pacific", "IAEA flags North Korea's Yongbyon expansion"),
    (22, "Americas", "US defence chief seals deal with Venezuela"),
    (23, "Asia-Pacific", "Bangladesh switches on nuclear power"),
    (24, "Middle East", "Israel delays the E1 settlement plan"),
    (25, "Europe", "Coalition of the Willing meets in Berlin"),
    (26, "Global", "IMF chief: AI boom could lift interest rates"),
    (27, "Middle East", "Pentagon puts Iran campaign cost at $48.3bn"),
    (28, "Africa", "Senegal rejects its 2027 budget"),
    (29, "Africa", "ECOWAS launches regional observation satellite"),
    (30, "Global", "'Supermountains' found under Antarctic ice"),
    (31, "Europe", "Spain's central bank hails immigration-led growth"),
    (32, "Middle East", "UNICEF: 64 children killed in Yemen since 3 Sept"),
    (33, "Europe", "Russian drones kill four in Odesa"),
    (34, "Asia-Pacific", "Xi pledges tariff cuts at APEC"),
    (35, "Asia-Pacific", "Quad plans first joint maritime patrol for 2027"),
    (36, "Asia-Pacific", "Raisina Dialogue opens in Tokyo"),
    (37, "Asia-Pacific", "India and Japan hold 2+2 talks"),
    (38, "Asia-Pacific", "Hilton bets big on Asia-Pacific growth"),
    (39, "Middle East", "Strikes near Abu Kalb displace about 3,000"),
    (40, "Global", "Bitcoin slides to $61,344, down 26% in a month"),
    (41, "Africa", "South Africa beat Bangladesh by nine wickets"),
    (42, "Europe", "Women's Champions League: the night's results"),
    (43, "Americas", "NBA: the night's scores from across the league"),
    (44, "Oceania", "Sydney Thunder chase 226 in the WBBL"),
]

REGIONS = ["Asia-Pacific", "Europe", "Middle East", "Africa",
           "Americas", "Oceania", "Global"]
REGION_COLORS = {"Asia-Pacific": BLUE, "Europe": GREEN,
                 "Middle East": RED, "Africa": GOLD,
                 "Americas": PURPLE, "Oceania": TEAL, "Global": GREY}

NUMBERS = ["44 STORIES", "7 REGIONS", "DOW -1,101", "BITCOIN $61,344",
           "550,000+ SIT KOREA'S EXAM", "80,000+ EVACUATED"]

SOURCES = ("Sources: Reuters - AP - AFP - Al Jazeera - UN News - BBC - "
           "Yonhap - ANI - IMD - WHO - JMA - IAEA - UEFA")


# ------------------------------------------------------- picture scenes
def _rel(box, fx, fy):
    x0, y0, x1, y1 = box
    return (x0 + fx * (x1 - x0), y0 + fy * (y1 - y0))


def _rect(d, box, fx, fy, fw, fh, **kw):
    """Rectangle from fractions of the scene box."""
    x0, y0, x1, y1 = box
    d.rectangle([x0 + fx * (x1 - x0), y0 + fy * (y1 - y0),
                 x0 + (fx + fw) * (x1 - x0), y0 + (fy + fh) * (y1 - y0)],
                **kw)


def _ell(d, box, cx, cy, rx, ry, **kw):
    """Ellipse centred at fractions (cx, cy) with radii as fractions."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.ellipse([x0 + (cx - rx) * w, y0 + (cy - ry) * h,
               x0 + (cx + rx) * w, y0 + (cy + ry) * h], **kw)


def _scene_draw(d, box, kind):
    """Draw a small geometric scene for one story inside box.

    All geometry is fractions of the box, so the same scene works in a
    tall lead illustration and in a 34 px tile strip.
    """
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    d.rectangle(box, fill=(238, 233, 220), outline=(200, 192, 172))
    if kind == "summit":
        # three flag poles, three buildings, a rising sun
        _ell(d, box, 0.50, 0.30, 0.10, 0.28, fill=GOLD)
        for i, col in enumerate((RED, BLUE, GREEN)):
            fx = 0.22 + 0.28 * i
            px, top = _rel(box, fx, 0.15)
            d.line([(px, y0 + bh * 0.90), (px, top)], fill=INK, width=3)
            d.polygon([(px, top), (px + bw * 0.16, top + bh * 0.08),
                       (px, top + bh * 0.16)], fill=col)
        for i in range(3):
            _rect(d, box, 0.10 + 0.30 * i, 0.72, 0.20, 0.23, fill=INK)
    elif kind == "scales":
        # balance scale: pole, beam, two pans
        cx, _ = _rel(box, 0.50, 0)
        d.line([(cx, y0 + bh * 0.08), (cx, y0 + bh * 0.92)], fill=INK,
               width=4)
        d.line([_rel(box, 0.12, 0.22), _rel(box, 0.88, 0.22)], fill=INK,
               width=4)
        for s in (0.12, 0.88):
            px, py = _rel(box, s, 0.22)
            d.line([(px, py), _rel(box, s - 0.08, 0.45)], fill=INK, width=2)
            d.line([(px, py), _rel(box, s + 0.08, 0.45)], fill=INK, width=2)
            d.pieslice([px - bw * 0.08, y0 + bh * 0.42,
                        px + bw * 0.08, y0 + bh * 0.58], 0, 180, fill=GOLD)
        _ell(d, box, 0.50, 0.10, 0.03, 0.05, fill=RED)
    elif kind == "leaf":
        # globe with a leaf
        _ell(d, box, 0.45, 0.55, 0.17, 0.36, fill=BLUE)
        d.arc([x0 + bw * 0.28, y0 + bh * 0.19, x0 + bw * 0.62,
               y0 + bh * 0.91], 200, 340, fill=GREEN, width=5)
        d.arc([x0 + bw * 0.28, y0 + bh * 0.19, x0 + bw * 0.62,
               y0 + bh * 0.91], 20, 160, fill=GREEN, width=5)
        _ell(d, box, 0.73, 0.27, 0.17, 0.21, fill=GREEN)
        d.line([_rel(box, 0.60, 0.44), _rel(box, 0.86, 0.10)],
               fill=(255, 255, 255), width=2)
    elif kind == "city":
        # skyline at dusk + big VI
        d.rectangle(box, fill=(30, 32, 48))
        tops = [0.42, 0.30, 0.48, 0.24, 0.40, 0.34]
        for i, t in enumerate(tops):
            _rect(d, box, i / 6 + 0.01, t, 1 / 6 - 0.02, 0.95 - t,
                  fill=(70, 72, 100))
            for wy in range(3):
                _rect(d, box, i / 6 + 0.04, t + 0.10 + wy * 0.16, 0.05,
                      0.08, fill=GOLD)
        fnt = font(SERIF, max(12, int(bh * 0.72)))
        tw = fnt.getlength("VI")
        cx, _ = _rel(box, 0.50, 0)
        d.text((cx - tw / 2, y0 + bh * 0.06), "VI", font=fnt,
               fill=(255, 255, 255))
    elif kind in ("chart", "fall"):
        # line chart, rising green or falling red
        d.line([(x0 + bw * 0.05, y1 - bh * 0.12),
                (x1 - bw * 0.04, y1 - bh * 0.12)], fill=MUTED, width=2)
        d.line([(x0 + bw * 0.05, y1 - bh * 0.12),
                (x0 + bw * 0.05, y0 + bh * 0.10)], fill=MUTED, width=2)
        if kind == "chart":
            pts = [(0.12, 0.78), (0.30, 0.62), (0.48, 0.66), (0.66, 0.40),
                   (0.84, 0.22)]
            col = GREEN
        else:
            pts = [(0.12, 0.22), (0.30, 0.40), (0.48, 0.36), (0.66, 0.62),
                   (0.84, 0.82)]
            col = RED
        xy = [_rel(box, fx, fy) for fx, fy in pts]
        d.line(xy, fill=col, width=4, joint="curve")
        ex, ey = xy[-1]
        d.polygon([(ex, ey - bh * 0.22), (ex + bw * 0.05, ey + bh * 0.05),
                   (ex - bw * 0.01, ey + bh * 0.20)], fill=col)
    elif kind == "burst":
        # interception burst in the sky over rooftops
        import math
        cx, cy = _rel(box, 0.50, 0.40)
        r = bh * 0.34
        for i in range(8):
            a = math.pi * i / 4
            d.line([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))],
                   fill=GOLD, width=3)
        _ell(d, box, 0.50, 0.40, 0.06, 0.16, fill=RED)
        _ell(d, box, 0.50, 0.40, 0.025, 0.07, fill=(255, 255, 255))
        for i in range(4):
            _rect(d, box, 0.08 + 0.24 * i, 0.82, 0.16, 0.15, fill=INK)
    elif kind == "bridge":
        # arched bridge over water
        d.arc([x0 + bw * 0.05, y0 + bh * 0.05, x1 - bw * 0.05,
               y1 - bh * 0.15], 180, 360, fill=INK, width=5)
        for fx in (0.25, 0.5, 0.75):
            px, _ = _rel(box, fx, 0)
            d.line([(px, y0 + bh * 0.12), (px, y0 + bh * 0.80)], fill=INK,
                   width=3)
        for fy in (0.88, 0.92, 0.96):
            d.line([_rel(box, 0.05, fy), _rel(box, 0.95, fy)], fill=BLUE,
                   width=2)
    elif kind == "tank":
        # simple tank silhouette
        _rect(d, box, 0.08, 0.42, 0.84, 0.26, fill=GREEN)
        _rect(d, box, 0.32, 0.24, 0.34, 0.20, fill=GREEN)
        d.line([_rel(box, 0.64, 0.32), _rel(box, 0.97, 0.26)], fill=INK,
               width=5)
        for i in range(5):
            _ell(d, box, 0.16 + i * 0.17, 0.80, 0.05, 0.10, fill=INK)
    elif kind == "ship":
        # ship on waves with an explosion star
        d.polygon([_rel(box, 0.10, 0.55), _rel(box, 0.90, 0.55),
                   _rel(box, 0.78, 0.80), _rel(box, 0.22, 0.80)], fill=INK)
        d.line([_rel(box, 0.50, 0.55), _rel(box, 0.50, 0.12)], fill=INK,
               width=3)
        d.polygon([_rel(box, 0.50, 0.12), _rel(box, 0.72, 0.26),
                   _rel(box, 0.50, 0.28)], fill=RED)
        import math
        ex, ey = _rel(box, 0.84, 0.26)
        r = bh * 0.16
        for i in range(6):
            a = math.pi * i / 3
            d.line([(ex, ey), (ex + r * math.cos(a), ey + r * math.sin(a))],
                   fill=GOLD, width=3)
        _ell(d, box, 0.84, 0.26, 0.04, 0.10, fill=GOLD)
        for fy in (0.88, 0.92, 0.96):
            d.line([_rel(box, 0.05, fy), _rel(box, 0.95, fy)], fill=BLUE,
                   width=2)
    elif kind == "crowd":
        # row of heads and shoulders
        for i in range(5):
            cx = 0.14 + 0.18 * i
            _ell(d, box, cx, 0.31, 0.05, 0.15, fill=(222, 190, 150))
            _rect(d, box, cx - 0.075, 0.48, 0.15, 0.44,
                  fill=(RED if i % 2 else BLUE))
        _rect(d, box, 0.04, 0.93, 0.92, 0.04, fill=INK)
    elif kind == "flag":
        # flagpole, waving flag, embassy block
        px, _ = _rel(box, 0.22, 0)
        d.line([(px, y0 + bh * 0.08), (px, y0 + bh * 0.92)], fill=INK,
               width=3)
        d.polygon([_rel(box, 0.22, 0.08), _rel(box, 0.52, 0.18),
                   _rel(box, 0.22, 0.28)], fill=RED)
        _rect(d, box, 0.48, 0.58, 0.47, 0.37, fill=(210, 198, 170))
        for i in range(3):
            _rect(d, box, 0.52 + i * 0.15, 0.64, 0.09, 0.14, fill=BLUE)
    elif kind == "cyclone":
        # spiral storm over sea
        cx, cy = _rel(box, 0.50, 0.42)
        for f in (0.42, 0.32, 0.22, 0.12):
            r = bh * f
            d.arc([cx - r, cy - r, cx + r, cy + r], 40, 300, fill=BLUE,
                  width=4)
        _ell(d, box, 0.50, 0.42, 0.025, 0.07, fill=RED)
        for fy in (0.88, 0.92, 0.96):
            d.line([_rel(box, 0.05, fy), _rel(box, 0.95, fy)], fill=BLUE,
                   width=2)


def scene(img, box, kind):
    """Draw a scene clipped to its box: no paint may escape the box."""
    x0, y0, x1, y1 = (int(v) for v in box)
    bw, bh = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    _scene_draw(ImageDraw.Draw(layer), (0, 0, bw, bh), kind)
    img.paste(layer, (x0, y0), layer)


# ------------------------------------------------------------- world map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
     (-80, 32), (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
     (-125, 49), (-140, 60), (-165, 60)],
    # South America
    [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-40, -5), (-35, -8),
     (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -52),
     (-73, -44), (-73, -30), (-77, -15), (-81, -5)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -18),
     (28, -33), (20, -35), (15, -27), (12, -18), (9, 4), (-8, 5),
     (-13, 8)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (30, 60), (28, 65), (40, 68),
     (55, 69), (70, 72), (90, 75), (110, 76), (130, 72), (150, 70),
     (170, 66), (178, 65), (170, 60), (162, 56), (158, 52), (142, 50),
     (140, 40), (135, 35), (130, 33), (122, 30), (120, 22), (110, 20),
     (108, 12), (105, 9), (100, 8), (97, 16), (92, 21), (88, 22),
     (80, 15), (77, 8), (72, 20), (66, 25), (60, 25), (57, 26),
     (52, 28), (48, 29), (44, 29), (40, 31), (36, 36), (30, 36),
     (26, 38), (22, 37), (19, 40), (12, 44), (3, 43), (-2, 37),
     (-6, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
     (132, -32), (137, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -11),
     (137, -12), (135, -15), (130, -13), (126, -14), (122, -17),
     (118, -20)],
]


def project(box, lon, lat):
    x0, y0, x1, y1 = box
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (75.0 - lat) / 135.0 * (y1 - y0)
    return (x, y)


def draw_map(d, box):
    d.rectangle(box, fill=SEA, outline=(180, 195, 205))
    for poly in CONTINENTS:
        pts = [project(box, lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # numbered pins for the 13 illustrated stories
    pin_font = font(SANS_B, 11)
    for s in STORIES:
        px, py = project(box, s["lon"], s["lat"])
        if s["n"] == 6:      # Wall Street shares NYC with GTA VI
            px += 20
            py += 13
        if s["n"] == 3:      # COP31 sits on the Crimea/Gaza cluster
            px -= 16
            py -= 12
        if s["n"] == 8:      # Crimea bridge, away from the cluster
            px += 14
            py -= 10
        if s["n"] == 13:     # Cyclone Akvan sits on Dhaka's pin
            px += 18
            py += 14
        r = 9
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=2)
        label = str(s["n"])
        tw = pin_font.getlength(label)
        th = pin_font.getbbox(label)[3] - pin_font.getbbox(label)[1]
        d.text((px - tw / 2, py - th / 2 - 1), label, font=pin_font,
               fill=(255, 255, 255))


# --------------------------------------------------------------- layout
def build(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x1 = W - M

    # ---- masthead
    title_f = font(SERIF, 56)
    title = "THE WORLD TODAY"
    tw = title_f.getlength(title)
    d.text(((W - tw) / 2, 12), title, font=title_f, fill=INK)
    sub_f = font(SANS_B, 17)
    sub = "Thursday, 19 November 2026  -  44 stories  -  7 regions"
    tw = sub_f.getlength(sub)
    d.text(((W - tw) / 2, 76), sub, font=sub_f, fill=RED)
    rule(d, M, 102, x1, 3)
    rule(d, M, 107, x1, 1)

    # ---- region count bar (counts computed from the data)
    counts = {r: 0 for r in REGIONS}
    for s in STORIES:
        counts[s["region"]] += 1
    for n, r, _ in BRIEFS:
        counts[r] += 1
    assert sum(counts.values()) == 44, counts
    seg_w = CW / len(REGIONS)
    bar_y, bar_h = 114, 22
    bar_f = font(SANS_B, 11)
    for i, r in enumerate(REGIONS):
        sx = M + i * seg_w
        d.rectangle([sx, bar_y, sx + seg_w - 1, bar_y + bar_h - 1],
                    fill=REGION_COLORS[r])
        label = "%s %d" % (r.upper(), counts[r])
        tw = bar_f.getlength(label)
        d.text((sx + (seg_w - tw) / 2, bar_y + 4), label, font=bar_f,
               fill=(255, 255, 255))

    # ---- day-in-numbers strip
    num_f = font(SANS_B, 13)
    nums = "   -   ".join(NUMBERS)
    tw = num_f.getlength(nums)
    d.text(((W - tw) / 2, 144), nums, font=num_f, fill=INK)
    rule(d, M, 166, x1, 1)

    # ---- lead 1 (full width)
    s = STORIES[0]
    ly, lh = 174, 132
    ill = (M, ly, M + 320, ly + lh)
    scene(img, ill, s["scene"])
    badge(d, ill[0] + 4, ill[1] + 4, s["n"])
    tx = M + 336
    tw_ = x1 - tx
    y = ly + 6
    d.text((tx, y), s["kicker"], font=font(SANS_B, 11), fill=RED)
    y += 16
    head_lines = wrap(s["head"], font(SERIF, 25), tw_)
    assert len(head_lines) <= 2, head_lines
    y = para(d, tx, y, head_lines, font(SERIF, 25), leading=29)
    body_lines = wrap(s["body"], font(SANS, 12), tw_)
    assert len(body_lines) <= 4, body_lines
    para(d, tx, y + 4, body_lines, font(SANS, 12), leading=15)
    rule(d, M, 314, x1, 1)

    # ---- leads 2 and 3 (two columns)
    col_w = (CW - 12) // 2
    for i, s in enumerate(STORIES[1:3]):
        cx0 = M + i * (col_w + 12)
        cy, ch = 322, 124
        ill = (cx0, cy, cx0 + 150, cy + ch)
        scene(img, ill, s["scene"])
        badge(d, ill[0] + 4, ill[1] + 4, s["n"])
        tx = cx0 + 162
        tw_ = cx0 + col_w - tx
        y = cy + 2
        d.text((tx, y), s["kicker"], font=font(SANS_B, 10), fill=RED)
        y += 14
        head_lines = wrap(s["head"], font(SERIF, 17), tw_)
        assert len(head_lines) <= 3, head_lines
        y = para(d, tx, y, head_lines, font(SERIF, 17), leading=20)
        body_lines = wrap(s["body"], font(SANS, 11), tw_)
        assert len(body_lines) <= 4, body_lines
        para(d, tx, y + 3, body_lines, font(SANS, 11), leading=14)

    # ---- tiles header + 10 tiles (5 x 2)
    hdr_f = font(SANS_B, 12)
    d.text((M, 452), "THE DAY IN PICTURES - 10 MORE STORIES",
           font=hdr_f, fill=INK)
    rule(d, M, 468, x1, 1)
    tile_w = (CW - 4 * 8) // 5
    tile_h, gap = 87, 8
    for idx, s in enumerate(STORIES[3:]):
        r, c = divmod(idx, 5)
        tx0 = M + c * (tile_w + gap)
        ty0 = 474 + r * (tile_h + gap)
        ill = (tx0, ty0, tx0 + tile_w, ty0 + 34)
        scene(img, ill, s["scene"])
        badge(d, ill[0] + 3, ill[1] + 3, s["n"], size=15)
        inner = tile_w - 8
        head_lines = wrap(s["head"], font(SANS_B, 11), inner)
        assert len(head_lines) <= 2, head_lines
        y = para(d, tx0 + 4, ty0 + 38, head_lines, font(SANS_B, 11),
                 leading=13)
        body_lines = wrap(s["body"], font(SANS, 10), inner)
        assert len(body_lines) <= 2, body_lines
        para(d, tx0 + 4, y + 1, body_lines, font(SANS, 10), leading=12)

    # ---- world map
    d.text((M, 660), "THE WORLD IN ONE LOOK - 13 PLACES THAT MADE THE DAY",
           font=hdr_f, fill=INK)
    draw_map(d, (M, 678, x1, 800))

    # ---- 31 briefs (3 columns, one line each)
    d.text((M, 808), "THE REST OF THE DAY - 31 BRIEFS",
           font=hdr_f, fill=INK)
    rule(d, M, 824, x1, 1)
    brief_f = font(SANS, 10)
    col_w = (CW - 2 * 11) // 3
    cols = [BRIEFS[0:11], BRIEFS[11:21], BRIEFS[21:31]]
    for ci, col in enumerate(cols):
        bx = M + ci * (col_w + 11)
        for ri, (n, _region, text) in enumerate(col):
            line = "%d  %s" % (n, text)
            assert brief_f.getlength(line) <= col_w, line
            d.text((bx, 830 + ri * 14), line, font=brief_f, fill=INK)

    # ---- date-check footer
    d.rectangle([M, 986, x1, 1014], fill=PANEL, outline=RULE)
    foot_f = font(SANS_B, 10)
    d.text((M + 8, 990),
           "DATE CHECK - Every story here happened or was first reported "
           "on Thursday 19 November 2026; stories from other days were "
           "left out.",
           font=foot_f, fill=INK)
    d.text((M + 8, 1003), SOURCES + "  -  Drawn entirely in code.",
           font=font(SANS, 9), fill=MUTED)

    img.save(path, "PNG")
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
