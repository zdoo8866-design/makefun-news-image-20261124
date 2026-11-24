#!/usr/bin/env python3
"""Compose the 24 November 2026 front page: one 1024x1024 newspaper page
that sums up a single day of world news in 36 stories.

Everything on the page is drawn with PIL primitives -- masthead, tally
bar, number strip, thirteen story cards with small spot illustrations, a
schematic world map with numbered pins, a briefs column block, the red
DATE CHECK box and the footer. No photographs, no external assets.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worldmap_data import CONTINENTS, ISLANDS

PAGE = 1024
MARGIN = 26

PAPER = (246, 241, 230)
PAPER_DARK = (236, 229, 211)
INK = (24, 28, 38)
NAVY = (18, 38, 84)
RED = (178, 32, 38)
GOLD = (176, 132, 40)
GREY = (96, 98, 104)
CARD_BG = (252, 250, 244)
SCENE_BG = (238, 233, 219)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def serif(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif_plain(size):
    return font("DejaVuSerif.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def sans_bold(size):
    return font("DejaVuSans-Bold.ttf", size)


def sans_italic(size):
    # this system has no oblique DejaVu; the serif face carries the
    # standfirst and the small italic notes instead
    return font("DejaVuSerif.ttf", size)


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap_lines(draw, s, fnt, width, max_lines=None):
    """Greedy word wrap; falls back to character steps for long words."""
    out = []
    for para in s.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if text_w(draw, trial, fnt) <= width:
                cur = trial
                continue
            if cur:
                out.append(cur)
                cur = ""
            while text_w(draw, w, fnt) > width and len(w) > 1:
                cut = len(w)
                while cut > 1 and text_w(draw, w[:cut], fnt) > width:
                    cut -= 1
                out.append(w[:cut])
                w = w[cut:]
            cur = w
        out.append(cur)
    if max_lines and len(out) > max_lines:
        out = out[:max_lines]
    return out


def para(draw, xy, s, fnt, fill, width, leading, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    x, y = xy
    lines = wrap_lines(draw, s, fnt, width, max_lines)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def centred(draw, cx, y, s, fnt, fill):
    draw.text((cx - text_w(draw, s, fnt) / 2, y), s, font=fnt, fill=fill)


def hline(draw, x0, x1, y, fill=INK, w=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)


def box(draw, rect, fill=None, outline=None, w=1):
    draw.rectangle(rect, fill=fill, outline=outline, width=w)


def rbox(draw, rect, radius, fill=None, outline=None, w=1):
    draw.rounded_rectangle(rect, radius=radius, fill=fill,
                           outline=outline, width=w)


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def smoke(draw, x, y, scale=1.0, tone=(150, 148, 142)):
    for i, (dx, dy, r) in enumerate([(0, 0, 9), (6, -10, 12),
                                     (14, -22, 15), (24, -36, 18)]):
        draw.ellipse([x + dx * scale - r * scale, y + dy * scale - r * scale,
                      x + dx * scale + r * scale, y + dy * scale + r * scale],
                     fill=tone)


# ---------------------------------------------------------------- content
KICKER = "THE WORLD IN ONE DAY"
MASTHEAD = "Tuesday 24 November 2026"
STANDFIRST = ("A boardroom U-turn in Santa Clara · a Politburo probe in "
              "Shanghai · drones over Kyiv · a $41bn drug deal in Paris")

HEROES = [
    dict(n=1, city="SANTA CLARA", tag="TECH & MARKETS", scene="nvidia",
         head="Nvidia board's Huang U-turn draws fire as US blacklists "
              "Alibaba units",
         src="Reuters"),
    dict(n=2, city="SHANGHAI", tag="POLITICS", scene="shanghai",
         head="Shanghai chief Chen Jining under investigation, Xinhua says",
         src="Reuters · Xinhua"),
    dict(n=3, city="KYIV", tag="WAR", scene="kyiv",
         head="Russian barrage kills 9 across Ukraine; Kyiv debris fire "
              "kills two",
         src="Kyiv Independent · Reuters"),
]

SMALLS = [
    dict(n=4, city="PARIS", tag="BUSINESS", scene="sanofi",
         head="Sanofi to buy Insmed for $41bn cash",
         src="Reuters"),
    dict(n=5, city="HANOI", tag="DISASTER", scene="hanoi",
         head="Hotpot gas blast kills at least six",
         src="AP"),
    dict(n=6, city="GAZA CITY", tag="WAR", scene="gaza",
         head="Israeli strikes kill six in Gaza",
         src="Reuters"),
    dict(n=7, city="BENGHAZI", tag="SECURITY · CLAIM", scene="benghazi",
         head="Ukraine: Russian corvette sunk in Libya",
         src="Reuters · UN News"),
    dict(n=8, city="BRUSSELS", tag="SPACE", scene="space",
         head="NATO vows space defence",
         src="BBC"),
    dict(n=9, city="ITURI, DR CONGO", tag="HEALTH", scene="congo",
         head="Fighting traps Ebola teams a day",
         src="UN News · WHO"),
    dict(n=10, city="DHAKA", tag="POLITICS", scene="dhaka",
         head="Hasina plans Dec 16 flight home",
         src="Reuters"),
    dict(n=11, city="KATHMANDU", tag="EARTHQUAKE", scene="quake",
         head="M5.4 quake felt in three countries",
         src="The Statesman"),
    dict(n=12, city="WASHINGTON", tag="LAW & TECH", scene="grok",
         head="US states sue Musk firms over Grok",
         src="SCMP"),
    dict(n=13, city="SERANG", tag="DISASTER", scene="factory",
         head="Factory-fire toll confirmed at 26",
         src="AP"),
]

BRIEFS = [
    (14, "LONDON", "GTA VI hacker sentenced to seven years in the UK — but walks free"),
    (15, "LONDON", "UK sanctions Myanmar's president and generals after genocide ruling"),
    (16, "YEREVAN", "Armenia unveils draft constitution, key to peace with Azerbaijan"),
    (17, "PYONGYANG", "North Korea threatens to shut Swiss office over youth-camp sanctions"),
    (18, "BRUSSELS", "EU proposes banning Russian flags at sports events"),
    (19, "BERLIN", "Germany first country to gain access to Ukraine's Delta system"),
    (20, "JERUSALEM", "Eisenkot given until Dec 6 to build a government"),
    (21, "WASHINGTON", "US envoy casts doubt on Trump's $3.8bn Israel funding pledge"),
    (22, "WEST BANK", "Israel investigates fires blamed on settlers"),
    (23, "BAGHDAD", "Iraq's PM puts disputed oilfields under the federal ministry"),
    (24, "GENEVA", "Landmine casualties hit a five-year high of 7,000"),
    (25, "MEXICO CITY", "'El Chapo Isidro' will be tried in Mexico despite US request"),
    (26, "BRASÍLIA", "Brazil raises 2027 inflation forecast to 4.5%, cuts growth"),
    (27, "SUVA", "Fiji closes all schools for five days as drought deepens"),
    (28, "CANBERRA", "Australia pursues a new security deal with Solomon Islands"),
    (29, "WELLINGTON", "NZ central bank's chief economist rebukes the government"),
    (30, "ZURICH", "US to host 2031 Women's World Cup; the UK gets 2035"),
    (31, "MANILA", "Trump offers Philippines $2.4bn for self-defence — with a catch"),
    (32, "PORT VILA", "Australia–Vanuatu treaty loses bipartisan backing on climate"),
    (33, "TAIPEI", "Taiwan's chip sector welcomes Huang's Nvidia comeback"),
    (34, "WASHINGTON", "Trump targets Newsom in crime speech on death sentences"),
    (35, "PARIS", "France faces calls to suspend tear gas after 10,000 complaints"),
    (36, "MOSCOW", "Russia accuses Estonia of acts 'on the verge of open war'"),
]

NUMBERS = [
    ("+31%", "Nvidia's one-day surge as Huang returned"),
    ("$41bn", "Sanofi's cash takeover of Insmed"),
    ("7,000", "landmine casualties in a year, a 5-year high"),
    ("M5.4", "quake in Nepal's Koshi province"),
    ("96", "drones launched at Ukraine overnight"),
    ("26", "factory-fire deaths confirmed Tuesday"),
]

REGIONS = [("EUROPE", 9), ("ASIA", 9), ("AMERICAS", 6), ("MIDDLE EAST", 4),
           ("OCEANIA", 4), ("AFRICA", 2), ("GLOBAL", 2)]

DATE_CHECK = (
    "NOT TUESDAY — Sun 22 Nov: Kyiv-region strikes kill 15 at Dymer; 12,000 "
    "evacuated from a Manchester arena show. Mon 23 Nov: COP31 collapses in "
    "Antalya; Nvidia reinstates Huang; US court clears the Iowa detonation; "
    "Democrats clinch their biggest House majority since 1992. Sat 21 Nov: "
    "the Banten factory fire itself. NOT YET: the Iowa blast (Wed) · "
    "Eisenkot's deadline (Dec 6) · Hasina's flight home (Dec 16)."
)

FOOTER = ("Sources: Reuters · AP · BBC · SCMP · Kyiv Independent · UN News · "
          "WHO · The Statesman · Xinhua · PINA · Bloomberg · MercoPress — "
          "every story above was reported on Tuesday 24 November 2026.")

# pin positions for the thirteen cards: story number -> (lon, lat)
PINS = {
    1: (-122, 37), 2: (121, 31), 3: (30, 50), 4: (2, 49), 5: (106, 21),
    6: (34, 31), 7: (20, 32), 8: (4, 51), 9: (29, 1), 10: (90, 24),
    11: (85, 28), 12: (-77, 39), 13: (106, -6),
}


# ----------------------------------------------------------------- scenes
def sc_nvidia(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(16, 42, 30))
    cx, cy, s = x + w * 0.34, y + h * 0.52, min(w, h) * 0.26
    rbox(d, [cx - s, cy - s, cx + s, cy + s], 5, fill=(118, 185, 0))
    rbox(d, [cx - s * 0.55, cy - s * 0.55, cx + s * 0.55, cy + s * 0.55], 3,
         fill=(10, 30, 20), outline=(220, 240, 200), w=2)
    for i in range(5):
        px = cx - s + i * (2 * s / 4)
        d.line([(px, cy - s), (px, cy - s - 8)], fill=(200, 220, 180), width=3)
        d.line([(px, cy + s), (px, cy + s + 8)], fill=(200, 220, 180), width=3)
    bx = x + w * 0.62
    for i, bh in enumerate([0.25, 0.4, 0.62, 0.95]):
        bw = w * 0.07
        box(d, [bx + i * (bw + 5), y + h * 0.88 - bh * h * 0.6,
                bx + i * (bw + 5) + bw, y + h * 0.88], fill=(118, 185, 0))
    d.polygon([(x + w - 26, y + 10), (x + w - 10, y + 10), (x + w - 18, y + 24)],
              fill=RED)


def sc_shanghai(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(206, 216, 232))
    base = y + h * 0.92
    towers = [(0.04, 0.45), (0.14, 0.62), (0.26, 0.38), (0.36, 0.55),
              (0.62, 0.42), (0.72, 0.58), (0.84, 0.36)]
    for fx, fh in towers:
        box(d, [x + w * fx, base - h * fh, x + w * fx + w * 0.08, base],
            fill=NAVY)
    tx = x + w * 0.47
    box(d, [tx, base - h * 0.78, tx + w * 0.09, base], fill=(44, 62, 110))
    d.ellipse([tx - 3, base - h * 0.86, tx + w * 0.09 + 3, base - h * 0.72],
              fill=(44, 62, 110))
    d.line([(tx + w * 0.045, base - h * 0.86), (tx + w * 0.045, base - h * 0.97)],
           fill=INK, width=2)
    d.ellipse([x + w * 0.70, y + h * 0.10, x + w * 0.70 + 34, y + h * 0.10 + 34],
              outline=RED, width=4)
    d.line([(x + w * 0.70 + 26, y + h * 0.10 + 28),
            (x + w * 0.70 + 42, y + h * 0.10 + 44)], fill=RED, width=4)


def sc_kyiv(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(14, 20, 44))
    base = y + h * 0.94
    for fx, fw, fh in [(0.03, 0.16, 0.5), (0.22, 0.13, 0.66), (0.38, 0.17, 0.44),
                       (0.58, 0.14, 0.6), (0.75, 0.2, 0.48)]:
        box(d, [x + w * fx, base - h * fh, x + w * (fx + fw), base],
            fill=(30, 40, 74))
        for r in range(3):
            for c in range(2):
                if (r * 2 + c + int(fx * 10)) % 3:
                    box(d, [x + w * fx + 5 + c * 11,
                            base - h * fh + 6 + r * 12,
                            x + w * fx + 11 + c * 11,
                            base - h * fh + 13 + r * 12], fill=GOLD)
    for fx, fy in [(0.2, 0.2), (0.45, 0.13), (0.68, 0.22), (0.85, 0.12)]:
        d.ellipse([x + w * fx, y + h * fy, x + w * fx + 5, y + h * fy + 5],
                  fill=(230, 230, 220))
    star(d, x + w * 0.63, y + h * 0.52, 15, RED)
    star(d, x + w * 0.3, y + h * 0.34, 9, GOLD)


def sc_sanofi(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(222, 232, 244))
    cx, cy = x + w * 0.36, y + h * 0.5
    d.rounded_rectangle([cx - 52, cy - 17, cx + 52, cy + 17], radius=17,
                        fill=(240, 244, 250), outline=NAVY, width=3)
    d.line([(cx, cy - 17), (cx, cy + 17)], fill=NAVY, width=3)
    box(d, [cx - 52, cy - 17, cx, cy + 17], fill=(150, 190, 235))
    d.rounded_rectangle([cx - 52, cy - 17, cx + 52, cy + 17], radius=17,
                        outline=NAVY, width=3)
    gx, gy = x + w * 0.78, y + h * 0.52
    d.ellipse([gx - 30, gy - 30, gx + 30, gy + 30], fill=GOLD,
              outline=(120, 88, 20), width=2)
    tf = sans_bold(30)
    d.text((gx - text_w(d, "$", tf) / 2, gy - 19), "$", font=tf,
           fill=(60, 44, 6))


def sc_hanoi(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(240, 228, 208))
    cx, base = x + w * 0.5, y + h * 0.92
    for dx in (-30, 0, 30):
        d.arc([cx + dx - 8, y + h * 0.05, cx + dx + 8, y + h * 0.34],
              200, 320, fill=(150, 150, 150), width=3)
    d.pieslice([cx - 58, base - 44, cx + 58, base + 4], 0, 180,
               fill=(70, 74, 84))
    box(d, [cx - 58, base - 25, cx + 58, base - 18], fill=(52, 56, 66))
    for dx in (-24, 0, 24):
        d.polygon([(cx + dx - 7, base - 1), (cx + dx + 7, base - 1),
                   (cx + dx, base - 15)], fill=(232, 120, 30))
    star(d, x + w * 0.84, y + h * 0.22, 11, RED)


def sc_gaza(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(226, 216, 198))
    base = y + h * 0.94
    for fx, fw, fh in [(0.04, 0.2, 0.55), (0.28, 0.16, 0.72), (0.48, 0.2, 0.5),
                       (0.72, 0.22, 0.64)]:
        box(d, [x + w * fx, base - h * fh, x + w * (fx + fw), base],
            fill=(120, 110, 96))
    smoke(d, x + w * 0.33, base - h * 0.72, 0.9)
    smoke(d, x + w * 0.8, base - h * 0.64, 0.7)
    d.line([(x + w * 0.6, y + h * 0.1), (x + w * 0.52, y + h * 0.3)],
           fill=RED, width=3)
    star(d, x + w * 0.5, y + h * 0.36, 9, RED)


def sc_benghazi(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(196, 222, 236))
    for i in range(3):
        yy = y + h * (0.68 + i * 0.11)
        d.arc([x + 6, yy, x + w - 6, yy + 14], 0, 180, fill=(60, 110, 160),
              width=2)
    hx, hy = x + w * 0.3, y + h * 0.6
    d.polygon([(hx, hy), (hx + w * 0.42, hy), (hx + w * 0.36, hy + 14),
               (hx + 6, hy + 14)], fill=(70, 78, 92))
    box(d, [hx + w * 0.1, hy - 12, hx + w * 0.3, hy], fill=(96, 104, 120))
    box(d, [hx + w * 0.17, hy - 22, hx + w * 0.23, hy - 12], fill=(96, 104, 120))
    d.ellipse([x + w * 0.68, y + h * 0.16, x + w * 0.68 + 16, y + h * 0.16 + 7],
              fill=INK)
    d.line([(x + w * 0.7, y + h * 0.24), (x + w * 0.58, y + h * 0.5)],
           fill=INK, width=2)


def sc_space(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(10, 14, 34))
    for fx, fy in [(0.1, 0.2), (0.3, 0.65), (0.55, 0.15), (0.8, 0.6),
                   (0.9, 0.25), (0.65, 0.8), (0.2, 0.85)]:
        d.ellipse([x + w * fx, y + h * fy, x + w * fx + 3, y + h * fy + 3],
                  fill=(235, 235, 220))
    cx, cy = x + w * 0.5, y + h * 0.48
    box(d, [cx - 20, cy - 13, cx + 20, cy + 13], fill=(200, 205, 215))
    box(d, [cx - 64, cy - 10, cx - 25, cy + 10], fill=(70, 110, 190))
    box(d, [cx + 25, cy - 10, cx + 64, cy + 10], fill=(70, 110, 190))
    d.arc([x + w * 0.08, y + h * 0.06, x + w * 0.92, y + h * 0.94], 300, 130,
          fill=GOLD, width=2)
    d.ellipse([cx + 48, cy - 36, cx + 56, cy - 28], fill=RED)


def sc_congo(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(206, 228, 200))
    bx, by, bw, bh = x + w * 0.3, y + h * 0.26, w * 0.4, h * 0.56
    box(d, [bx, by, bx + bw, by + bh], fill=(246, 246, 240), outline=INK, w=2)
    box(d, [bx + bw * 0.4, by + bh * 0.18, bx + bw * 0.6, by + bh * 0.5], fill=RED)
    box(d, [bx + bw * 0.31, by + bh * 0.27, bx + bw * 0.69, by + bh * 0.41],
        fill=RED)
    for i in range(6):
        sx = x + 8 + i * (w - 16) / 5
        d.line([(sx, y + h * 0.9), (sx + 8, y + h * 0.9)], fill=INK, width=3)
    d.polygon([(x + w * 0.1, y + h * 0.2), (x + w * 0.2, y + h * 0.34),
               (x + w * 0.08, y + h * 0.36)], fill=(90, 140, 70))
    d.polygon([(x + w * 0.82, y + h * 0.24), (x + w * 0.92, y + h * 0.38),
               (x + w * 0.8, y + h * 0.4)], fill=(90, 140, 70))


def sc_dhaka(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(210, 226, 240))
    cy = y + h * 0.42
    d.polygon([(x + w * 0.12, cy), (x + w * 0.78, cy - 6), (x + w * 0.9, cy + 4),
               (x + w * 0.78, cy + 10), (x + w * 0.14, cy + 8)], fill=(240, 242, 246))
    d.polygon([(x + w * 0.12, cy), (x + w * 0.02, cy - 16), (x + w * 0.16, cy + 2)],
              fill=(0, 106, 78))
    d.polygon([(x + w * 0.4, cy - 4), (x + w * 0.52, cy - 24), (x + w * 0.6, cy - 4)],
              fill=(0, 106, 78))
    d.ellipse([x + w * 0.2, cy - 1, x + w * 0.27, cy + 6], fill=(244, 42, 65))
    box(d, [x + 6, y + h * 0.82, x + w - 6, y + h * 0.88], fill=(90, 96, 108))
    for i in range(7):
        box(d, [x + 14 + i * (w - 28) / 7, y + h * 0.845,
                x + 26 + i * (w - 28) / 7, y + h * 0.855], fill=(240, 240, 230))


def sc_quake(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(216, 224, 234))
    base = y + h * 0.88
    for fx, fw, fh, snow in [(0.02, 0.4, 0.62, True), (0.34, 0.44, 0.8, True),
                             (0.66, 0.32, 0.52, False)]:
        d.polygon([(x + w * fx, base), (x + w * (fx + fw / 2), base - h * fh),
                   (x + w * (fx + fw), base)], fill=(96, 110, 138))
        if snow:
            mx = x + w * (fx + fw / 2)
            d.polygon([(mx - 9, base - h * fh + 13), (mx, base - h * fh),
                       (mx + 9, base - h * fh + 13)], fill=(245, 247, 250))
    d.line([(x + w * 0.5, base - h * 0.4), (x + w * 0.46, base - h * 0.24),
            (x + w * 0.53, base - h * 0.12), (x + w * 0.5, base)],
           fill=RED, width=3)
    for i in range(3):
        d.arc([x + w * 0.06 + i * 7, base + 2, x + w * 0.3 + i * 7, base + 12],
              0, 180, fill=(70, 100, 150), width=2)


def sc_grok(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(224, 226, 232))
    px, py, pw, ph = x + w * 0.34, y + h * 0.1, w * 0.32, h * 0.8
    rbox(d, [px, py, px + pw, py + ph], 9, fill=(30, 32, 40))
    rbox(d, [px + 6, py + 12, px + pw - 6, py + 34], 6, fill=(70, 74, 88))
    rbox(d, [px + 6, py + 42, px + pw - 16, py + 60], 6, fill=(52, 56, 68))
    rbox(d, [px + 16, py + 68, px + pw - 6, py + 86], 6, fill=(90, 96, 112))
    tx, ty = x + w * 0.76, y + h * 0.3
    d.polygon([(tx, ty), (tx + 34, ty + 52), (tx - 34, ty + 52)], outline=RED,
              width=4)
    tf = sans_bold(30)
    d.text((tx - text_w(d, "!", tf) / 2, ty + 14), "!", font=tf, fill=RED)


def sc_factory(d, x, y, w, h):
    box(d, [x, y, x + w, y + h], fill=(232, 222, 204))
    base = y + h * 0.92
    box(d, [x + w * 0.08, base - h * 0.5, x + w * 0.62, base], fill=(130, 118, 100))
    for i in range(4):
        box(d, [x + w * (0.13 + i * 0.12), base - h * 0.4,
                x + w * (0.2 + i * 0.12), base - h * 0.26], fill=(60, 58, 54))
    box(d, [x + w * 0.68, base - h * 0.78, x + w * 0.76, base], fill=(110, 100, 86))
    smoke(d, x + w * 0.72, base - h * 0.8, 0.8, tone=(90, 88, 86))
    for dx in (0.2, 0.34, 0.48):
        d.polygon([(x + w * dx - 7, base - h * 0.5), (x + w * dx + 7, base - h * 0.5),
                   (x + w * dx, base - h * 0.68)], fill=(232, 110, 26))
    d.polygon([(x + w * 0.86, y + h * 0.12), (x + w * 0.94, y + h * 0.12),
               (x + w * 0.9, y + h * 0.26)], fill=RED)


SCENES = {
    "nvidia": sc_nvidia, "shanghai": sc_shanghai, "kyiv": sc_kyiv,
    "sanofi": sc_sanofi, "hanoi": sc_hanoi, "gaza": sc_gaza,
    "benghazi": sc_benghazi, "space": sc_space, "congo": sc_congo,
    "dhaka": sc_dhaka, "quake": sc_quake, "grok": sc_grok,
    "factory": sc_factory,
}




# ----------------------------------------------------------------- layout
BODY = {
    1: "Governance critics say the board dented its independence by "
       "restoring Huang before its conduct probes ended. Trump claimed "
       "credit.",
    2: "Xinhua said Tuesday the Shanghai party chief and Politburo member "
       "is under investigation — a fourth top-body probe since 2025.",
    3: "Russia launched 96 drones overnight; the past day's attacks killed "
       "9 and injured 77. Debris set a central Kyiv block ablaze, "
       "killing two.",
    4: "At $175 a share, a 46% premium; Sanofi shares +5.6%.",
    5: "08:30 blast in a Dong Da hotpot restaurant; 10 in intensive care.",
    6: "Health and police officials said two of the dead were police.",
    7: "Sea drones from a mother ship, Zelenskiy says; UN urges a probe.",
    8: "After reports Moscow may orbit a nuclear-armed satellite.",
    9: "Fighting near a hospital forced Ebola teams to take cover 24h.",
    10: "In exile in India; a minister warns she may return in handcuffs.",
    11: "Koshi province quake felt across India, Bhutan, Bangladesh.",
    12: "Oregon and Virginia sue over alleged Grok abuse images.",
    13: "Most died on the 2nd floor reaching the emergency exit.",
}

STATUS = {7: "CLAIM"}

BRIEF_LINES = [
    (14, "LONDON", "GTA VI hacker gets 7 years, walks free", "SCMP"),
    (15, "LONDON", "UK sanctions Myanmar president and generals", "SCMP"),
    (16, "YEREVAN", "Armenia drafts constitution for peace", "SCMP"),
    (17, "PYONGYANG", "N. Korea threatens Swiss office closure", "SCMP"),
    (18, "BRUSSELS", "EU may ban Russian flags at sports events", "SCMP"),
    (19, "BERLIN", "Germany first to access Delta system", "Kyiv Ind."),
    (20, "JERUSALEM", "Eisenkot has Dec 6 government deadline", "SCMP"),
    (21, "WASHINGTON", "Envoy doubts $3.8bn Israel pledge", "SCMP"),
    (22, "WEST BANK", "Israel probes fires blamed on settlers", "SCMP"),
    (23, "BAGHDAD", "Iraq PM takes disputed oilfields federal", "Reuters"),
    (24, "GENEVA", "Landmine casualties hit 5-year high: 7,000", "SCMP"),
    (25, "MEXICO CITY", "'El Chapo Isidro' to be tried at home", "Reuters"),
    (26, "BRASÍLIA", "Brazil lifts 2027 inflation view to 4.5%", "MercoPress"),
    (27, "SUVA", "Fiji shuts schools 5 days as drought deepens", "PINA"),
    (28, "CANBERRA", "Australia pursues Solomon Is. pact", "Bloomberg"),
    (29, "WELLINGTON", "RBNZ economist rebukes government", "Bloomberg"),
    (30, "ZURICH", "US hosts 2031 World Cup, UK 2035", "Japan Times"),
    (31, "MANILA", "Trump offers Philippines $2.4bn, with a catch", "SCMP"),
    (32, "PORT VILA", "Australia–Vanuatu treaty loses backing", "PINA"),
    (33, "TAIPEI", "Chip sector welcomes Huang comeback", "SCMP"),
    (34, "WASHINGTON", "Trump targets Newsom in crime speech", "SCMP"),
    (35, "PARIS", "Calls to suspend tear gas after complaints", "SCMP"),
    (36, "MOSCOW", "Russia: Estonia acts 'on the verge of war'", "Reuters"),
]

REGION_COLOURS = [(70, 90, 140), (96, 108, 128), (64, 128, 120),
                  (128, 102, 140), (120, 130, 80), (170, 110, 70),
                  (110, 110, 110)]
# order matches REGIONS after sorting by the bar's display order below
REGION_BAR = [("EUROPE", 9), ("ASIA", 9), ("AMERICAS", 6),
              ("MIDDLE EAST", 4), ("OCEANIA", 4), ("AFRICA", 2),
              ("GLOBAL", 2)]
REGION_BAR_COLOURS = [(70, 90, 140), (96, 108, 128), (64, 128, 120),
                      (128, 102, 140), (120, 130, 80), (170, 110, 70),
                      (110, 110, 110)]


def draw_header(d):
    kf = sans_bold(14)
    d.text((MARGIN, 20), KICKER, font=kf, fill=RED)
    right = "36 STORIES · EVERY CONTINENT · ALL FROM THIS ONE DAY"
    d.text((PAGE - MARGIN - text_w(d, right, kf), 20), right, font=kf,
           fill=NAVY)
    d.text((MARGIN, 38), MASTHEAD, font=serif(54), fill=INK)
    d.text((MARGIN, 100), STANDFIRST, font=sans_italic(14.5), fill=RED)
    hline(d, MARGIN, PAGE - MARGIN, 124, fill=INK, w=3)


def draw_regions(d, y):
    total = sum(c for _, c in REGION_BAR)
    x = MARGIN
    f = sans_bold(9.8)
    for (name, count), colour in zip(REGION_BAR, REGION_BAR_COLOURS):
        wseg = (PAGE - 2 * MARGIN) * count / total
        box(d, [x, y, x + wseg, y + 22], fill=colour)
        label = "%s %d" % (name, count)
        d.text((x + wseg / 2 - text_w(d, label, f) / 2, y + 5), label,
               font=f, fill=(250, 248, 240))
        x += wseg


def draw_numbers(d, y):
    box(d, [MARGIN, y, MARGIN + 96, y + 48], fill=RED)
    f = sans_bold(12.5)
    d.text((MARGIN + 48 - text_w(d, "THE DAY IN", f) / 2, y + 7),
           "THE DAY IN", font=f, fill=(255, 252, 244))
    d.text((MARGIN + 48 - text_w(d, "NUMBERS", f) / 2, y + 25),
           "NUMBERS", font=f, fill=(255, 252, 244))
    seg = (PAGE - MARGIN - (MARGIN + 96)) / 6
    big = serif(23)
    small = sans(9.3)
    for i, (num, label) in enumerate(NUMBERS):
        cx = MARGIN + 96 + seg * i + seg / 2
        d.text((cx - text_w(d, num, big) / 2, y), num, font=big, fill=RED)
        ly = y + 30
        for ln in wrap_lines(d, label, small, seg - 8)[:2]:
            d.text((cx - text_w(d, ln, small) / 2, ly), ln, font=small,
                   fill=(52, 54, 62))
            ly += 12
    hline(d, MARGIN, PAGE - MARGIN, y + 52, fill=INK, w=1)


def status_chip(d, x_right, y, status):
    if status == "CLAIM":
        bg, fg = GOLD, (40, 30, 4)
    else:
        bg, fg = (84, 140, 84), (250, 252, 246)
    f = sans_bold(8)
    wchip = text_w(d, status, f) + 10
    rbox(d, [x_right - wchip, y, x_right, y + 13], 3, fill=bg)
    d.text((x_right - wchip + 5, y + 2), status, font=f, fill=fg)


def draw_card(img, d, card, x, y, w, h, hero):
    box(d, [x, y, x + w, y + h], fill=CARD_BG, outline=INK, w=2)
    scene_h = 80 if hero else 52
    strip_h = 15 if hero else 13
    # render the spot illustration on its own canvas so nothing a scene
    # draws can spill over the card's border
    canvas = Image.new("RGB", (w - 4, scene_h), SCENE_BG)
    SCENES[card["scene"]](ImageDraw.Draw(canvas), 0, 0, w - 4, scene_h)
    img.paste(canvas, (x + 2, y + 2))
    sy = y + 2 + scene_h
    box(d, [x + 2, sy, x + w - 2, sy + strip_h], fill=NAVY)
    tf = sans_bold(9 if hero else 8)
    d.text((x + 7, sy + (3 if hero else 2)),
           "%s · %s" % (card["city"], card["tag"]), font=tf,
           fill=(240, 242, 248))
    status_chip(d, x + w - 7, sy + 1, STATUS.get(card["n"], "REPORTED"))
    cy = sy + strip_h + 6
    n = str(card["n"])
    nf = sans_bold(11 if hero else 9.5)
    box(d, [x + 8, cy, x + 8 + 17, cy + 17], fill=RED)
    d.text((x + 8 + 8.5 - text_w(d, n, nf) / 2, cy + 2), n, font=nf,
           fill=(255, 252, 244))
    cf = sans_bold(11.5 if hero else 9.5)
    d.text((x + 31, cy + 2), "%s · %s" % (card["city"], card["tag"]),
           font=cf, fill=NAVY)
    hf = serif(15 if hero else 12.5)
    yend = para(d, (x + 9, cy + 22), card["head"], hf, INK, w - 18,
                18.5 if hero else 14.5, max_lines=2)
    bf = sans(9.3 if hero else 8.5)
    body = BODY[card["n"]] + " — " + card["src"]
    para(d, (x + 9, yend + 1), body, bf, (52, 54, 62), w - 18,
         11.5 if hero else 11, max_lines=3 if hero else 2)


def draw_map(d, x, y, w):
    tf = sans_bold(12)
    d.text((x, y), "WHERE IT HAPPENED", font=tf, fill=INK)
    note = "numbers match the stories"
    d.text((x + w - text_w(d, note, sans_italic(9)), y + 2), note,
           font=sans_italic(9), fill=GREY)
    my, mh = y + 18, 96
    box(d, [x, my, x + w, my + mh], fill=(24, 44, 84))
    lon0, lon1, lat0, lat1 = -170, 195, -58, 82

    def proj(lon, lat):
        return (x + (lon - lon0) / (lon1 - lon0) * w,
                my + (lat1 - lat) / (lat1 - lat0) * mh)

    for loop in CONTINENTS.values():
        d.polygon([proj(lon, lat) for lon, lat in loop],
                  fill=(168, 178, 160), outline=(110, 120, 104))
    for lon, lat, r in ISLANDS:
        cx, cy = proj(lon, lat)
        rad = r / (lon1 - lon0) * w
        d.ellipse([cx - rad, cy - rad * 0.7, cx + rad, cy + rad * 0.7],
                  fill=(168, 178, 160), outline=(110, 120, 104))
    nf = sans_bold(8.5)
    for n, (lon, lat) in PINS.items():
        cx, cy = proj(lon, lat)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                  outline=(255, 252, 244), width=1)
        s = str(n)
        d.text((cx - text_w(d, s, nf) / 2, cy - 5), s, font=nf,
               fill=(255, 252, 244))
    cf = sans(8.5)
    d.text((x, my + mh + 5), "Pins 1–13 are the card stories above.",
           font=cf, fill=GREY)
    d.text((x, my + mh + 16),
           "UTC 01:30 Hanoi blast · 08:34 Sanofi jumps in Paris",
           font=cf, fill=GREY)


def draw_briefs(d, x, y, w):
    hf = sans_bold(13)
    d.text((x, y), "ALSO ON TUESDAY", font=hf, fill=RED)
    d.text((x + text_w(d, "ALSO ON TUESDAY", hf) + 8, y),
           "— 23 MORE STORIES", font=hf, fill=INK)
    note = "place · what happened · source"
    d.text((x + w - text_w(d, note, sans_italic(9.5)), y + 2), note,
           font=sans_italic(9.5), fill=GREY)
    hline(d, x, x + w, y + 18, fill=INK, w=2)
    col_w = (w - 16) / 2
    nf = sans_bold(9.0)
    cf = sans_bold(9.0)
    bf = sans(9.0)
    for idx, (n, city, text, src) in enumerate(BRIEF_LINES):
        col, row = divmod(idx, 12)
        cx = x + col * (col_w + 16)
        ly = y + 24 + row * 11.8
        d.text((cx, ly), str(n), font=nf, fill=RED)
        d.text((cx + 20, ly), city, font=cf, fill=NAVY)
        city_w = text_w(d, city, cf)
        d.text((cx + 24 + city_w, ly), " — " + text + " · " + src,
               font=bf, fill=INK)


def draw_date_check(d, x, y, w):
    box(d, [x, y, x + w, y + 66], fill=(250, 240, 238), outline=RED, w=2)
    tf = sans_bold(12.5)
    d.text((x + 10, y + 7), "✓ DATE CHECK", font=tf, fill=RED)
    para(d, (x + 10 + text_w(d, "✓ DATE CHECK", tf) + 10, y + 8),
         "Every story on this page happened, or was first reported, on "
         "Tuesday 24 November 2026. " + DATE_CHECK,
         sans(10), (52, 44, 42), w - 30 - text_w(d, "✓ DATE CHECK", tf), 13.5)


def draw_footer(d):
    hline(d, MARGIN, PAGE - MARGIN, 970, fill=INK, w=2)
    d.text((MARGIN, 976), FOOTER, font=sans(9.3), fill=GREY)
    tail = "Pictures and map drawn in code, not photographs"
    d.text((PAGE - MARGIN - text_w(d, tail, sans(9.3)), 990), tail,
           font=sans(9.3), fill=GREY)


def build(out_path):
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    draw_regions(d, 132)
    draw_numbers(d, 162)
    cards = HEROES + SMALLS
    for i, card in enumerate(cards[:3]):
        draw_card(img, d, card, [MARGIN, 353, 680][i], 220, 318, 200, True)
    for i, card in enumerate(cards[3:]):
        row, col = divmod(i, 5)
        draw_card(img, d, card, MARGIN + col * 196, 428 + row * 150, 188,
                  146, False)
    draw_map(d, MARGIN, 732, 322)
    draw_briefs(d, 364, 732, 634)
    draw_date_check(d, MARGIN, 898, PAGE - 2 * MARGIN)
    draw_footer(d)
    img.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    build(target)
    print("wrote", target)
