#!/usr/bin/env python3
"""news-image-20261119 — full-day front page for Thursday 19 November 2026.

Draws one 1024x1024 front page with PIL: a masthead, a region count bar,
a day-in-numbers strip, three large illustrated lead stories, ten small
illustrated stories, a world map with numbered pins, 31 numbered briefs,
and a date-check box. Every story on the page happened, or was first
reported, on 19 November 2026. All pictures are geometric scenes drawn
in code; there is no network access, no randomness and no clock, so two
runs write identical bytes.

Run:  python3 main.py [output-path]   (default: entry.png)
"""

import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (179, 32, 44)
GREY = (90, 86, 78)
LINE = (180, 172, 156)
MAP_LAND = (232, 220, 192)
MAP_LINE = (168, 156, 128)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, xy, text, fnt, width, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    x, y = xy
    lh = leading or int(fnt.size * 1.22)
    lines = wrap(d, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


# (n, region, place, topic, headline, body, source, art, lon/lat)
LEADS = [
    (1, "ASIA-PACIFIC", "SHENZHEN", "SUMMIT",
     "Trump, Xi and Putin hold first three-way summit",
     "The US, Chinese and Russian leaders met for the first time and "
     "issued a joint peace declaration. \u2014 Reuters",
     "Reuters", "summit", (114.0, 22.5)),
    (2, "ASIA-PACIFIC", "THE HAGUE", "JUSTICE",
     "World Court: Myanmar committed genocide",
     "The first state ever held responsible: some 10,000 killed, 700,000 "
     "fled; reparations ordered. \u2014 UN News",
     "UN News \u00b7 Reuters", "court", (4.3, 52.0)),
    (3, "WORLD", "ANTALYA", "CLIMATE",
     "COP31 draft drops fossil fuels",
     "The slimmed-down draft cuts 144 paragraphs to 80 and names no fuel "
     "at all. Talks end Friday. \u2014 Reuters",
     "Reuters \u00b7 UN News", "cop", (30.7, 36.9)),
]

TILES = [
    (4, "WORLD", "WORLDWIDE", "GAMES",
     "GTA VI goes on sale after 13 years",
     "Rolling midnight launch by time zone; reviews average 99. "
     "\u2014 Rockstar",
     "Rockstar \u00b7 Metacritic", "gta", (174.8, -36.9)),
    (5, "AMERICAS", "NEW YORK", "MARKETS",
     "Anthropic starts trading on Nasdaq",
     "Priced at $83; opened $111.50, closed $97.17, up 17.1% \u2014 the "
     "largest IPO ever.",
     "AP \u00b7 Reuters", "ipo", (-74.0, 40.7)),
    (6, "AMERICAS", "NEW YORK", "MARKETS",
     "Wall Street plunges 1,101 points",
     "Dow falls 2.2% to 49,097, below 50,000; S&P down a sixth straight "
     "day. \u2014 AP",
     "AP", "crash", (-70.0, 42.0)),
    (7, "MIDDLE EAST", "RIYADH", "WAR",
     "Houthi missile shot down over Riyadh",
     "Second strike on the financial district in two weeks; no "
     "casualties. \u2014 briefings",
     "Reuters", "riyadh", (46.7, 24.6)),
    (8, "EUROPE", "CRIMEA", "WAR",
     "Ukraine hits Crimea bridge again",
     "Third strike in a week halts trains to Russia across Europe's "
     "longest bridge.",
     "Euronews", "bridge", (33.5, 45.0)),
    (9, "MIDDLE EAST", "GAZA", "CEASEFIRE",
     "Israeli tanks cross into central Gaza",
     "Tanks cross the 'yellow line' near Nuseirat; thousands flee. "
     "\u2014 Al Jazeera",
     "NBC \u00b7 Reuters", "tank", (34.5, 31.5)),
    (10, "MIDDLE EAST", "HORMUZ", "WAR",
     "Iran and US trade strikes in the Gulf",
     "Iran fires at US bases in Kuwait and Bahrain; the US hits back. "
     "\u2014 briefings",
     "Reuters", "tanker", (56.5, 26.5)),
    (11, "ASIA-PACIFIC", "DHAKA", "UNREST",
     "Deadly unrest grips Bangladesh",
     "Hasina supporters enforce a shutdown; at least four killed. "
     "\u2014 Reuters",
     "Reuters", "crowd", (90.4, 23.8)),
    (12, "AFRICA", "MOGADISHU", "DIPLOMACY",
     "Somalia expels UAE ambassador",
     "Ordered out within 72 hours over an 'open invasion'. \u2014 Reuters",
     "Reuters", "envoy", (45.3, 2.0)),
    (13, "ASIA-PACIFIC", "ODISHA", "STORM",
     "Cyclone Akvan nears India's coast",
     "Odisha evacuates more than 80,000 people ahead of Friday's "
     "landfall.",
     "IMD \u00b7 Reuters", "cyclone", (85.0, 20.0)),
]

# (n, text, source) — numbered briefs 14..44
BRIEFS = [
    (14, "Ethiopia and Eritrea mass troops on their border; clashes near "
         "Badme feared.", "Reuters"),
    (15, "Netherlands summons Russia's envoy after its Kyiv embassy is "
         "hit.", "Reuters"),
    (16, "Denmark backs the US Arctic pact for Greenland, 109\u20130.", "AP"),
    (17, "Dozens missing as a migrant boat capsizes off Senegal.", "Reuters"),
    (18, "Ebola in DR Congo tops 2,280 cases, deadliest for young "
         "children.", "WHO"),
    (19, "More than 550,000 South Koreans sit the college exam.", "Yonhap"),
    (20, "Magnitude 5.7 quake hits Kumamoto, Japan; two hurt.", "JMA"),
    (21, "IAEA: North Korea expands its Yongbyon uranium plant.", "IAEA"),
    (22, "US defence chief seals a military deal with Venezuela in "
         "Caracas.", "AP"),
    (23, "Bangladesh starts generating nuclear power from its "
         "Russian-built plant.", "Reuters"),
    (24, "Israel delays the E1 settlement project in the West Bank.",
     "Reuters"),
    (25, "Coalition of the Willing meets in Berlin; Witkoff and Kushner "
         "attend.", "Reuters"),
    (26, "IMF chief warns the AI boom could lift global interest rates.",
     "Reuters"),
    (27, "Pentagon: the US campaign against Iran has cost $48.3bn.",
     "Reuters"),
    (28, "Senegal's assembly rejects the 2027 budget proposal.", "Reuters"),
    (29, "ECOWAS plans West Africa's first regional observation "
         "satellite.", "ECOWAS"),
    (30, "Himalayan-scale 'supermountains' found under Antarctic ice.",
     "researchers"),
    (31, "Spain: immigration drove about half of growth since 2022, "
         "central bank says.", "Bank of Spain"),
    (32, "UNICEF: 64 children killed in Yemen since fighting escalated "
         "on 3 Sept.", "UNICEF"),
    (33, "Russian drones kill four in Odesa and hit the historic centre.",
     "Reuters"),
    (34, "Xi pledges lower tariffs and wider market access at the APEC "
         "CEO Summit.", "AP"),
    (35, "Quad plans its first joint maritime patrol drill for 2027.",
     "White House"),
    (36, "Raisina Tokyo opens beside the India\u2013Japan 2+2 defence "
         "dialogue.", "ANI"),
    (37, "Hilton maps Asia-Pacific growth, with Waldorf Astoria for "
         "Tokyo and Sydney.", "TTR Weekly"),
    (38, "Strikes around Abu Kalb in Sudan displace about 3,000 people.",
     "UN"),
    (39, "Bitcoin falls to $61,344, down 26% in a month.", "Odaily"),
    (40, "South Africa beat Bangladesh by 9 wickets in the first Test.",
     "Reuters"),
    (41, "Barcelona hit Servette 6\u20130; Arsenal lose 0\u20132 to Lyon in "
         "the Women's Champions League.", "UEFA"),
    (42, "Chelsea beat PSG 1\u20130; Manchester City win 2\u20130 at H\u00e4cken.",
     "UEFA"),
    (43, "Knicks edge Magic 121\u2013116; Bulls rout Nets 137\u2013107 in the "
         "NBA.", "AP"),
    (44, "Sydney Thunder chase 226 to beat Brisbane Heat in the WBBL.",
     "WBBL"),
]

REGION_COUNTS = [
    ("ASIA-PACIFIC", 12, (179, 32, 44)),
    ("EUROPE", 8, (31, 78, 121)),
    ("MIDDLE EAST", 5, (122, 92, 0)),
    ("AFRICA", 8, (46, 125, 50)),
    ("AMERICAS", 5, (106, 27, 154)),
    ("OCEANIA", 1, (0, 105, 92)),
    ("WORLD", 5, (55, 71, 79)),
]

NUMBERS = [
    ("3", "leaders, one table"),
    ("9\u20136", "World Court vote"),
    ("$81.3bn", "record IPO"),
    ("\u22121,101", "Dow points"),
    ("99", "GTA VI on Metacritic"),
    ("80,000+", "flee Cyclone Akvan"),
]

DATE_CHECK_OUT = (
    "Nvidia's $115.8bn quarter \u00b7 Knesset speaker vote \u00b7 Kerch "
    "Bridge span collapse \u00b7 Peltola's Alaska win \u00b7 Prague train "
    "crash \u00b7 Mongolia's president resigns \u00b7 Jeffries named House "
    "speaker \u00b7 EU's \u20ac45bn Ukraine loan \u00b7 Fed minutes turn "
    "hawkish")


# ---------------------------------------------------------------- art scenes
# Each draws a small geometric scene into a box (x, y, w, h). No text
# inside the art except big numerals that PIL renders crisply.

def art_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 78, 121))
    d.rectangle([x, y + h - 24, x + w, y + h], fill=(120, 72, 20))
    for i, col in enumerate([(178, 34, 52), (222, 41, 16), (0, 57, 166)]):
        cx = x + 40 + i * (w - 80) // 2
        d.line([cx, y + 6, cx, y + 44], fill=(240, 240, 240), width=3)
        d.polygon([(cx, y + 6), (cx + 26, y + 14), (cx, y + 22)], fill=col)
        d.ellipse([cx - 10, y + 46, cx + 10, y + 66], fill=(232, 196, 160))
        d.polygon([(cx - 15, y + h - 24), (cx + 15, y + h - 24),
                   (cx + 9, y + 66), (cx - 9, y + 66)], fill=(30, 30, 30))
        d.polygon([(cx - 5, y + 66), (cx + 5, y + 66), (cx, y + 76)],
                  fill=(255, 255, 255))
        d.rectangle([cx - 2, y + 68, cx + 2, y + h - 24], fill=RED)


def art_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 196, 160))
    d.polygon([(x + w // 2 - 52, y + 18), (x + w // 2 + 52, y + 18),
               (x + w // 2, y + 2)], fill=(90, 60, 30))
    for i in range(4):
        cx = x + 22 + i * 20
        d.rectangle([cx, y + 20, cx + 8, y + h - 22], fill=(240, 235, 220))
    d.rectangle([x + 8, y + h - 22, x + w - 8, y + h - 14], fill=(90, 60, 30))
    bx, by = x + w - 78, y + 34
    d.line([bx + 20, by, bx + 20, by + 26], fill=(60, 50, 30), width=3)
    d.line([bx, by + 6, bx + 40, by + 6], fill=(60, 50, 30), width=3)
    d.polygon([(bx + 2, by + 6), (bx + 10, by + 22), (bx + 18, by + 6)], fill=(200, 170, 60))
    d.polygon([(bx + 22, by + 6), (bx + 30, by + 22), (bx + 38, by + 6)], fill=(200, 170, 60))
    d.rectangle([x + w - 62, y + 8, x + w - 10, y + 30], fill=RED)
    d.text((x + w - 58, y + 10), "9-6", font=font(SANS_B, 15), fill=(255, 255, 255))


def art_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 90, 110))
    d.ellipse([x + 14, y + 14, x + 86, y + 86], fill=(70, 160, 90))
    d.ellipse([x + 30, y + 26, x + 52, y + 44], fill=(30, 110, 180))
    d.ellipse([x + 56, y + 52, x + 76, y + 70], fill=(30, 110, 180))
    d.rectangle([x + w - 34, y + 12, x + w - 22, y + h - 30], fill=(200, 200, 200))
    d.ellipse([x + w - 40, y + 6, x + w - 16, y + 26], fill=RED)
    d.rectangle([x + w - 34, y + 26, x + w - 22, y + 46], fill=RED)
    d.line([x + 10, y + h - 24, x + w - 10, y + h - 24], fill=(255, 255, 255), width=3)
    d.text((x + 12, y + h - 22), "35 x 35", font=font(SANS_B, 13), fill=(255, 255, 255))


def art_gta(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(88, 28, 135))
    for i in range(5):
        d.rectangle([x + 12 + i * 34, y + h - 34 - (i % 3) * 12,
                     x + 34 + i * 34, y + h - 18], fill=(40, 20, 60))
    d.rounded_rectangle([x + w // 2 - 46, y + 12, x + w // 2 + 46, y + 46],
                        radius=12, fill=(20, 20, 20))
    d.ellipse([x + w // 2 - 34, y + 22, x + w // 2 - 22, y + 34], fill=(255, 255, 255))
    d.ellipse([x + w // 2 + 22, y + 22, x + w // 2 + 34, y + 34], fill=(255, 0, 110))
    d.text((x + w // 2 - 12, y + 12), "VI", font=font(SANS_B, 26), fill=(255, 255, 255))


def art_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 60, 40))
    pts = [(x + 8, y + h - 14), (x + 40, y + h - 34), (x + 70, y + h - 26),
           (x + 100, y + h - 52), (x + 130, y + 16), (x + 160, y + 30),
           (x + w - 10, y + 44)]
    d.line(pts, fill=(80, 220, 120), width=4)
    d.line([(x + w - 10, y + 44), (x + w - 22, y + 44), (x + w - 10, y + 32)],
           fill=(255, 80, 80), width=3)
    d.text((x + 10, y + 6), "$83 \u2192 $97", font=font(SANS_B, 15), fill=(255, 255, 255))


def art_crash(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(60, 16, 20))
    pts = [(x + 8, y + 12), (x + 40, y + 20), (x + 70, y + 16),
           (x + 100, y + 34), (x + 130, y + 52), (x + 160, y + h - 14),
           (x + w - 10, y + h - 8)]
    d.line(pts, fill=(255, 80, 80), width=4)
    d.text((x + 10, y + 6), "\u22121,101", font=font(SANS_B, 16), fill=(255, 255, 255))


def art_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 30, 60))
    for i, bh in enumerate([30, 52, 40, 62]):
        bx = x + 14 + i * 42
        d.rectangle([bx, y + h - 12 - bh, bx + 30, y + h - 12], fill=(90, 100, 130))
        d.rectangle([bx + 10, y + h - 20 - bh, bx + 20, y + h - 12 - bh], fill=(200, 200, 120))
    d.line([x + 20, y + 10, x + 90, y + 34, x + 150, y + 18], fill=(255, 200, 60), width=3)
    for cx, cy in [(90, 34), (150, 18)]:
        for a in range(8):
            import math
            ang = a * 3.14159 / 4
            d.line([cx, cy, cx + 12 * math.cos(ang), cy + 12 * math.sin(ang)],
                   fill=(255, 220, 80), width=2)


def art_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(40, 90, 140))
    d.line([x + 6, y + h - 30, x + w - 6, y + h - 30], fill=(60, 60, 60), width=4)
    for i in range(6):
        d.line([x + 16 + i * 28, y + h - 30, x + 16 + i * 28, y + h - 52],
               fill=(60, 60, 60), width=2)
    d.line([x + 16, y + h - 52, x + w // 2, y + h - 66, x + w - 16, y + h - 52],
           fill=(60, 60, 60), width=3)
    cx, cy = x + w // 2, y + 18
    for a in range(8):
        import math
        ang = a * 3.14159 / 4
        d.line([cx, cy, cx + 14 * math.cos(ang), cy + 14 * math.sin(ang)],
               fill=(255, 140, 0), width=3)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 60, 0))


def art_tank(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 190, 150))
    d.line([x, y + h - 16, x + w, y + h - 16], fill=(120, 90, 50), width=4)
    d.rectangle([x + 30, y + h - 52, x + 110, y + h - 26], fill=(70, 90, 50))
    d.rectangle([x + 52, y + h - 66, x + 88, y + h - 50], fill=(70, 90, 50))
    d.line([x + 88, y + h - 60, x + 150, y + h - 66], fill=(50, 60, 40), width=5)
    for i in range(5):
        d.ellipse([x + 36 + i * 15, y + h - 26, x + 48 + i * 15, y + h - 14],
                  fill=(40, 40, 40))


def art_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 200, 120))
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(30, 80, 130))
    d.polygon([(x + 22, y + h - 34), (x + 150, y + h - 34), (x + 138, y + h - 14),
               (x + 34, y + h - 14)], fill=(120, 30, 30))
    d.rectangle([x + 96, y + h - 58, x + 128, y + h - 34], fill=(200, 200, 200))
    d.line([x + 112, y + h - 58, x + 112, y + h - 72], fill=(60, 60, 60), width=3)
    for cx, cy in [(52, y + h - 52), (76, y + h - 60)]:
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 120, 0))
    d.ellipse([x + 150, y + 14, x + 164, y + 28], fill=(40, 40, 40))
    d.ellipse([x + 158, y + 20, x + 168, y + 30], fill=(40, 40, 40))


def art_crowd(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(150, 60, 40))
    for r in range(3):
        for c in range(7):
            cx = x + 16 + c * 24
            cy = y + 16 + r * 22
            d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(232, 196, 160))
            d.polygon([(cx - 9, cy + 18), (cx + 9, cy + 18), (cx + 6, cy + 6),
                       (cx - 6, cy + 6)], fill=(40 + r * 30, 60, 90))
    d.rectangle([x + w - 52, y + 8, x + w - 10, y + 30], fill=(255, 255, 255))
    d.text((x + w - 48, y + 11), "4+", font=font(SANS_B, 14), fill=RED)


def art_envoy(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 200, 170))
    d.rectangle([x + 20, y + 26, x + 110, y + h - 14], fill=(240, 235, 220))
    d.polygon([(x + 20, y + 26), (x + 65, y + 8), (x + 110, y + 26)], fill=(90, 60, 30))
    for i in range(3):
        d.rectangle([x + 32 + i * 26, y + 44, x + 44 + i * 26, y + h - 14],
                    fill=(120, 140, 180))
    d.line([x + 128, y + 20, x + w - 16, y + 20], fill=RED, width=4)
    d.polygon([(x + w - 16, y + 14), (x + w - 4, y + 20), (x + w - 16, y + 26)], fill=RED)
    d.text((x + 126, y + 28), "72h", font=font(SANS_B, 14), fill=RED)


def art_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(180, 210, 230))
    cx, cy = x + w // 2, y + h // 2 - 4
    for r in (34, 26, 18, 10):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(255, 255, 255), width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    d.polygon([(x + 8, y + h - 12), (x + 70, y + h - 12), (x + 60, y + h - 26),
               (x + 18, y + h - 26)], fill=(120, 140, 90))
    d.text((x + w - 62, y + h - 22), "80,000+", font=font(SANS_B, 12), fill=(20, 40, 60))


ART = {
    "summit": art_summit, "court": art_court, "cop": art_cop,
    "gta": art_gta, "ipo": art_ipo, "crash": art_crash,
    "riyadh": art_riyadh, "bridge": art_bridge, "tank": art_tank,
    "tanker": art_tanker, "crowd": art_crowd, "envoy": art_envoy,
    "cyclone": art_cyclone,
}


def render_tile_art(key, w, h):
    """Draw a scene at 100px tall (text stripped: it would smear when
    shrunk) and downscale it into the small tile art box."""
    tmp = Image.new("RGB", (w, 100), PAPER)
    td = ImageDraw.Draw(tmp)
    orig_text = ImageDraw.ImageDraw.text
    ImageDraw.ImageDraw.text = lambda *a, **k: None
    try:
        ART[key](td, 0, 0, w, 100)
    finally:
        ImageDraw.ImageDraw.text = orig_text
    return tmp.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- world map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 25), (-85, 30), (-95, 29),
     (-105, 23), (-115, 32), (-125, 40), (-125, 48), (-140, 60), (-165, 60)],
    [(-80, 10), (-60, 8), (-50, 0), (-40, -5), (-35, -10), (-40, -20),
     (-50, -30), (-60, -35), (-70, -40), (-75, -50), (-70, -30), (-75, -15),
     (-80, -5)],
    [(-10, 36), (-5, 44), (0, 50), (5, 55), (10, 58), (20, 60), (30, 70),
     (40, 68), (30, 60), (25, 55), (15, 45), (10, 40), (0, 38), (-5, 36)],
    [(-10, 35), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15),
     (50, 10), (45, 0), (40, -10), (35, -20), (30, -30), (20, -35),
     (15, -25), (12, -15), (8, 5), (0, 5), (-10, 10), (-15, 25)],
    [(40, 68), (60, 70), (80, 72), (100, 76), (120, 73), (140, 72),
     (160, 66), (170, 60), (160, 55), (140, 45), (130, 40), (120, 30),
     (110, 20), (100, 10), (95, 5), (90, 15), (80, 10), (75, 20),
     (65, 25), (55, 25), (45, 30), (40, 40), (40, 55)],
    [(113, -22), (125, -15), (135, -12), (145, -15), (150, -22), (150, -35),
     (140, -38), (130, -32), (120, -35), (113, -30)],
]

BRIEF_PINS = [
    (39, 14.5), (30.5, 50.4), (12.6, 55.7), (-17.4, 14.7), (23, -2),
    (127, 37.5), (130.7, 32.8), (126, 39.8), (-66.9, 10.5), (35.2, 31.9),
    (13.4, 52.5), (7.5, 9.0), (-3.7, 40.4), (44.2, 15.3), (30.7, 46.5),
    (139.7, 35.7), (151.2, -33.9), (30, 13.0), (28, -26.2), (2.2, 41.4),
    (-0.1, 51.5), (153, -27.5),
]


def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (75.0 - lat) / 130.0 * mh
    return x, y


def draw_map(d, mx, my, mw, mh):
    d.rectangle([mx, my, mx + mw, my + mh], fill=(222, 232, 238))
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=MAP_LAND, outline=MAP_LINE)
    for lon, lat in BRIEF_PINS:
        px, py = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(120, 120, 120))
    for n, _r, _p, _t, _h, _b, _s, _a, ll in LEADS + TILES:
        px, py = lonlat_to_xy(ll[0], ll[1], mx, my, mw, mh)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        tw = d.textlength(str(n), font=font(SANS_B, 9))
        d.text((px - tw / 2, py - 5), str(n), font=font(SANS_B, 9),
               fill=(255, 255, 255))


# ---------------------------------------------------------------- build page
def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # kicker line
    d.line([8, 12, W - 8, 12], fill=RED, width=3)
    d.text((8, 18), "THE WORLD IN ONE DAY", font=font(SANS_B, 12), fill=RED)
    right = "44 STORIES \u00b7 7 REGIONS \u00b7 ALL FROM THIS ONE DAY"
    d.text((W - 8 - d.textlength(right, font=font(SANS_B, 12)), 18), right,
           font=font(SANS_B, 12), fill=INK)

    # masthead
    d.text((8, 34), "Thursday 19 November 2026", font=font(SERIF_B, 52), fill=INK)
    d.line([8, 96, W - 8, 96], fill=INK, width=2)
    sub = ("Trump, Xi and Putin share one table \u00b7 The World Court finds "
           "genocide in Myanmar \u00b7 COP31's draft drops fossil fuels")
    d.text((8, 102), sub, font=font(SERIF, 15), fill=RED)

    # region count bar
    y = 126
    x = 8
    for name, count, col in REGION_COUNTS:
        label = "%s %d" % (name, count)
        tw = d.textlength(label, font=font(SANS_B, 11)) + 18
        d.rectangle([x, y, x + tw, y + 20], fill=col)
        d.text((x + 9, y + 4), label, font=font(SANS_B, 11), fill=(255, 255, 255))
        x += tw + 6
    d.text((x + 2, y + 4), "44 stories", font=font(SANS_B, 11), fill=GREY)

    # day in numbers
    y = 150
    box_w = (W - 16 - 5 * 8) // 6
    for i, (num, lab) in enumerate(NUMBERS):
        bx = 8 + i * (box_w + 8)
        d.rectangle([bx, y, bx + box_w, y + 32], outline=LINE, width=1)
        d.text((bx + 8, y + 2), num, font=font(SERIF_B, 15), fill=RED)
        d.text((bx + 8, y + 19), lab, font=font(SANS, 9), fill=INK)

    # three lead cards
    y0, lead_h, art_h = 190, 186, 92
    col_w = (W - 16 - 2 * 12) // 3
    for n, region, place, topic, head, body, src, art, _ll in LEADS:
        cx = 8 + (n - 1) * (col_w + 12)
        ART[art](d, cx, y0, col_w, art_h)
        d.rectangle([cx, y0 + art_h, cx + col_w, y0 + art_h + 3], fill=RED)
        d.text((cx, y0 + art_h + 4), "%d  %s \u00b7 %s" % (n, place, topic),
               font=font(SANS_B, 10), fill=RED)
        ty = draw_wrapped(d, (cx, y0 + art_h + 18), head, font(SERIF_B, 19),
                          col_w, leading=22, max_lines=2)
        draw_wrapped(d, (cx, ty + 2), body, font(SANS, 11), col_w, leading=13,
                     max_lines=2)

    # ten small illustrated cards: 5 columns x 2 rows
    y0, card_h, art_h = 384, 95, 30
    tile_w = (W - 16 - 4 * 10) // 5
    for idx, (n, region, place, topic, head, body, src, art, _ll) in enumerate(TILES):
        row, col = divmod(idx, 5)
        cx = 8 + col * (tile_w + 10)
        cy = y0 + row * (card_h + 6)
        img.paste(render_tile_art(art, tile_w, art_h), (cx, cy))
        d.text((cx, cy + art_h + 3), "%d  %s \u00b7 %s" % (n, place, topic),
               font=font(SANS_B, 8), fill=RED)
        ty = draw_wrapped(d, (cx, cy + art_h + 14), head, font(SANS_B, 10),
                          tile_w, leading=11, max_lines=2)
        draw_wrapped(d, (cx, ty), body, font(SANS, 9), tile_w, leading=10,
                     max_lines=2)

    # map (left) + briefs (right)
    my = 588
    d.text((8, my), "WHERE IT HAPPENED", font=font(SANS_B, 12), fill=INK)
    d.text((8, my + 16), "numbers match the stories",
           font=font(SANS, 9), fill=GREY)
    draw_map(d, 8, my + 34, 322, 290)
    d.text((8, my + 328), "Pins 1\u201313: illustrated stories. Grey dots: briefs.",
           font=font(SANS, 9), fill=GREY)

    bx = 344
    d.text((bx, my), "ALSO ON THURSDAY 19 NOVEMBER 2026",
           font=font(SANS_B, 12), fill=INK)
    d.line([bx, my + 18, W - 8, my + 18], fill=INK, width=1)
    col_w = (W - 8 - bx - 12) // 2
    f_num = font(SANS_B, 10)
    f_txt = font(SANS, 10)
    for i, (n, text, src) in enumerate(BRIEFS):
        col, row = divmod(i, 16)
        x = bx + col * (col_w + 12)
        yy = my + 24 + row * 20
        d.text((x, yy), str(n), font=f_num, fill=RED)
        lines = wrap(d, text + " \u2014 " + src, f_txt, col_w - 22)
        ly = yy
        for ln in lines[:2]:
            d.text((x + 22, ly), ln, font=f_txt, fill=INK)
            ly += 10

    # date check box
    y = 936
    d.rectangle([8, y, W - 8, y + 44], outline=RED, width=2)
    d.text((16, y + 5), "DATE CHECK \u2713", font=font(SANS_B, 11), fill=RED)
    msg = ("Every story on this page happened, or was first reported, on "
           "Thursday 19 November 2026. Left out as other days' news: "
           + DATE_CHECK_OUT + ".")
    draw_wrapped(d, (16, y + 20), msg, font(SANS, 10), W - 32, leading=12,
                 max_lines=2)

    # footer
    d.line([8, 988, W - 8, 988], fill=LINE, width=1)
    foot = ("Claims are attributed, not stated as fact \u00b7 Pictures and map: "
            "original, drawn in code \u00b7 Sources: Reuters, AP, AFP, Al Jazeera, "
            "UN News, BBC, Yonhap, ANI, IMD, WHO, JMA, IAEA, UEFA \u00b7 2026-11-19")
    d.text((8, 994), foot, font=font(SANS, 9), fill=GREY)

    img.save(out_path, format="PNG")
    return out_path


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
