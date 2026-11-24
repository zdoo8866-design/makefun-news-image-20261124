#!/usr/bin/env python3
"""Compose entry.png for news-image-20261124: a 1024x1024 newspaper front
page in the style of the competition's winning pages -- masthead, region
tally, the day in numbers, 13 drawn story cards, a where-it-happened map,
23 one-line briefs and a date-check box. Every element is drawn in code;
all type is set programmatically so every word and figure is exact.
Story pool and dating notes: ../../work-20261124-frontpage/stories.md
(the v5 front-page system of news-image-20261121, reused: dev 0.9834)."""
import os
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFont

W = H = 1024
WORK = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WORK, "..", "entry.png")
sys.path.insert(0, WORK)
from worldmap_data import POLYS_HQ

NOTO = "/usr/share/fonts/truetype/noto"
SERIF_B = f"{NOTO}/NotoSerif-Bold.ttf"
SERIF_I = f"{NOTO}/NotoSerif-Italic.ttf"
SANS_B = f"{NOTO}/NotoSans-Bold.ttf"
SANS_SB = f"{NOTO}/NotoSans-SemiBold.ttf"
SANS_R = f"{NOTO}/NotoSans-Regular.ttf"
SANS_I = f"{NOTO}/NotoSans-Italic.ttf"

PAPER = (243, 234, 214)
INK = (26, 38, 52)
NAVY = (24, 42, 66)
RED = (168, 30, 30)
DARKRED = (142, 26, 26)
SOFT = (88, 94, 92)
CARD = (255, 254, 248)
BORDER = (178, 168, 142)
GOLD = (232, 190, 92)
GREEN = (56, 116, 62)
AMBER = (172, 116, 28)
STEEL = (64, 98, 138)

def F(path, size):
    return ImageFont.truetype(path, size)

def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def fit(d, text, path, size, maxw, floor=10):
    """Shrink a one-line font until the text fits maxw."""
    while size > floor and d.textlength(text, font=F(path, size)) > maxw:
        size -= 1
    return F(path, size)

def badge(d, cx, cy, r, num, fsize):
    # drawn on a 4x tile and downscaled: a 1x PIL ellipse is visibly
    # pixel-stepped, and these numbered badges sit on every card
    ss = 4
    R = int(round(r * ss)) + ss
    tile = Image.new("RGBA", (R * 2, R * 2), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    rr = r * ss
    td.ellipse([R - rr, R - rr, R + rr, R + rr], fill=RED + (255,))
    td.text((R, R), str(num), font=F(SANS_B, int(fsize * ss)),
            fill=(255, 255, 255, 255), anchor="mm")
    tile = tile.resize((R * 2 // ss, R * 2 // ss), Image.LANCZOS)
    canvas.paste(tile, (int(cx - R // ss), int(cy - R // ss)), tile)

def pill(d, x, y, label):
    f = F(SANS_B, 8)
    w = d.textlength(label, font=f) + 10
    col = {"REPORTED": GREEN, "CLAIM": AMBER, "FORECAST": STEEL}[label]
    d.rounded_rectangle([x, y, x + w, y + 12], 3, fill=col)
    d.text((x + 5, y + 1), label, font=f, fill=(255, 255, 255))
    return w

# ---------------------------------------------------------------- data ----
REGIONS = [  # (label, count, colour) -- real tally of the 36 stories
    ("EUROPE", 9, (43, 92, 140)),
    ("ASIA", 9, (176, 62, 40)),
    ("MIDDLE EAST", 4, (146, 118, 56)),
    ("AMERICAS", 6, (104, 74, 132)),
    ("OCEANIA", 4, (46, 118, 112)),
    ("AFRICA", 2, (86, 128, 64)),
    ("GLOBAL", 2, (58, 58, 58)),
]

STATS = [  # (big, caption)
    ("+31%", "Nvidia's one-day surge as Huang returned"),
    ("$41bn", "Sanofi's cash takeover of Insmed, agreed Tuesday"),
    ("7,000", "landmine casualties in a year — a five-year high"),
    ("M5.4", "quake in Nepal, felt in three neighbouring lands"),
    ("96", "drones Russia launched at Ukraine overnight"),
    ("26", "workers confirmed dead in the Banten factory fire"),
]

HEROES = [
    dict(n=1, scene="nvidia", loc="SANTA CLARA", cat="TECH · MARKETS",
         bl="NVIDIA HQ · SANTA CLARA", br="THE DAY AFTER", tag="REPORTED",
         head="Huang is back at Nvidia — the fight isn\u2019t over",
         body="Critics say the board reinstated its CEO before its own "
              "probes ended. Washington blacklists Alibaba\u2019s Apex "
              "and Megaspeed in the scandal; Trump claims the credit.",
         src="Reuters"),
    dict(n=2, scene="shanghai", loc="SHANGHAI", cat="POLITICS",
         bl="SHANGHAI · PARTY CHIEF", br="4TH SINCE 2025", tag="REPORTED",
         head="Politburo member Chen Jining under investigation",
         body="Xinhua says the Shanghai party chief is being probed — "
              "the fourth member of China\u2019s top body investigated "
              "since 2025. No details of the case were given.",
         src="Reuters · Xinhua"),
    dict(n=3, scene="kyiv2", loc="KYIV", cat="WAR",
         bl="KYIV · OVERNIGHT", br="96 DRONES", tag="REPORTED",
         head="Overnight barrage kills nine across Ukraine",
         body="Russia launches 96 drones overnight; nine killed and "
              "77 hurt in the past day. Debris sparks a fatal fire "
              "in central Kyiv; Zaporizhzhia is hit.",
         src="Kyiv Independent · Reuters"),
]

SMALLS = [
    dict(n=4, scene="sanofi", loc="PARIS", cat="BUSINESS", tag="REPORTED",
         band="PARIS · SANOFI–INSMED",
         head="Sanofi bets $41bn on Insmed",
         body="Cash deal at $175 a share — a 46% premium.",
         src="Reuters"),
    dict(n=5, scene="hanoi", loc="HANOI", cat="DISASTER", tag="REPORTED",
         band="HANOI · DONG DA",
         head="Restaurant blast kills at least six",
         body="Gas blast at a hotpot eatery, 08:30; 10 in intensive care.",
         src="AP"),
    dict(n=6, scene="gaza2", loc="GAZA CITY", cat="WAR", tag="REPORTED",
         band="GAZA CITY · TUESDAY",
         head="Airstrikes kill at least six in Gaza",
         body="Two police officers among the dead, officials say.",
         src="Reuters"),
    dict(n=7, scene="hormuz", loc="BENGHAZI", cat="SECURITY",
         tag="CLAIM", band="BENGHAZI · LIBYA",
         head="Ukraine says it sank a Russian corvette",
         body="Sea drones hit the Merkury; the UN urges a probe.",
         src="Reuters · UN News"),
    dict(n=8, scene="space", loc="BRUSSELS", cat="SPACE", tag="REPORTED",
         band="BRUSSELS · NATO",
         head="NATO vows to counter a space threat",
         body="Alarm at reports of a nuclear-armed satellite.",
         src="BBC"),
    dict(n=9, scene="congo", loc="ITURI", cat="HEALTH", tag="REPORTED",
         band="ITURI · DR CONGO",
         head="Fighting traps Ebola teams by a hospital",
         body="Responders pinned under cover for over 24 hours.",
         src="UN News · WHO"),
    dict(n=10, scene="dhaka", loc="DHAKA", cat="POLITICS", tag="REPORTED",
         band="DHAKA · HASINA",
         head="Hasina bids to fly home on Dec 16",
         body="Exiled ex-PM seeks a Dec 16 return; \u2018handcuffs\u2019 warned.",
         src="Reuters"),
    dict(n=11, scene="banda", loc="KATHMANDU", cat="EARTHQUAKE",
         tag="REPORTED", band="KOSHI · NEPAL",
         head="M5.4 quake rattles Nepal\u2019s east",
         body="Tremors felt in India, Bhutan and Bangladesh.",
         src="The Statesman"),
    dict(n=12, scene="grok", loc="WASHINGTON", cat="LAW · TECH",
         tag="REPORTED", band="WASHINGTON · GROK SUIT",
         head="States sue Musk firms over Grok images",
         body="Suit targets sexualised images made by Grok.",
         src="SCMP"),
    dict(n=13, scene="basra", loc="SERANG", cat="DISASTER", tag="REPORTED",
         band="SERANG · BANTEN",
         head="Factory-fire toll confirmed at 26",
         body="Most died fleeing for an exit, rescuers say.",
         src="AP"),
]

# (number, place, fact, source) -- the 23 briefs, stories 14-36
BRIEFS = [
    (14, "London", "GTA VI hacker jailed seven years, walks free", "SCMP"),
    (15, "London", "UK sanctions Myanmar\u2019s president, generals", "SCMP"),
    (16, "Yerevan", "Draft constitution unveiled, key to peace", "SCMP"),
    (17, "Pyongyang", "Threat to shut Swiss office in sanctions row", "SCMP"),
    (18, "Brussels", "EU may ban Russian flags at sports events", "SCMP"),
    (19, "Berlin", "Germany first to access Ukraine\u2019s Delta system", "Kyiv Ind."),
    (20, "Jerusalem", "Eisenkot has to Dec 6 to form a government", "SCMP"),
    (21, "Washington", "Envoy casts doubt on ending $3.8bn Israel aid", "SCMP"),
    (22, "West Bank", "Israel investigates fires blamed on settlers", "SCMP"),
    (23, "Baghdad", "PM orders ministry to run Kurdish-area oilfields", "Reuters"),
    (24, "Geneva", "Landmine deaths hit 5-year high: 7,000", "SCMP"),
    (25, "Mexico City", "\u2018El Chapo Isidro\u2019 to be tried at home, not US", "Reuters"),
    (26, "Bras\u00edlia", "2027 inflation view up to 4.5%, growth cut", "MercoPress"),
    (27, "Suva", "Fiji shuts all schools 5 days in El Ni\u00f1o drought", "PINA"),
    (28, "Canberra", "Australia courts Solomons in security push", "Bloomberg"),
    (29, "Wellington", "Bank chief: stop \u2018messing with\u2019 our mandate", "Bloomberg"),
    (30, "Zurich", "2031 Women\u2019s World Cup to US group, 2035 UK", "Japan Times"),
    (31, "Manila", "Trump offers $2.4bn for self-defence, with a catch", "SCMP"),
    (32, "Port Vila", "Australia treaty deal loses bipartisan backing", "PINA"),
    (33, "Taipei", "Chip sector welcomes Huang\u2019s Nvidia comeback", "SCMP"),
    (34, "Washington", "Trump slams Newsom\u2019s death-row commutations", "SCMP"),
    (35, "Paris", "Calls to suspend tear gas over health complaints", "SCMP"),
    (36, "Moscow", "Estonia moves \u2018verge of open war\u2019 — Russia", "Reuters"),
]

# region of each brief; its number is drawn in the region-bar colour
BRIEF_REGION = {
    14: "EUROPE", 15: "EUROPE", 16: "ASIA", 17: "ASIA", 18: "EUROPE",
    19: "EUROPE", 20: "MIDDLE EAST", 21: "AMERICAS", 22: "MIDDLE EAST",
    23: "MIDDLE EAST", 24: "GLOBAL", 25: "AMERICAS", 26: "AMERICAS",
    27: "OCEANIA", 28: "OCEANIA", 29: "OCEANIA", 30: "GLOBAL",
    31: "ASIA", 32: "OCEANIA", 33: "ASIA", 34: "AMERICAS",
    35: "EUROPE", 36: "EUROPE",
}
REGION_COL = {name: col for name, _cnt, col in REGIONS}

# map pins for the 13 cards: (number, lon, lat)
PINS = [
    (1, -122.0, 37.4), (2, 121.5, 31.2), (3, 30.5, 50.4), (4, 2.35, 48.9),
    (5, 105.9, 21.0), (6, 34.3, 31.5), (7, 20.1, 32.1), (8, 5.6, 51.6),
    (9, 29.3, 1.7), (10, 90.4, 23.8), (11, 85.3, 27.7), (12, -77.0, 38.9),
    (13, 106.1, -6.1),
]
# dots for briefs: (lon, lat)
DOTS = [
    (-0.1, 51.5), (44.5, 40.2), (125.8, 39.0), (13.4, 52.5), (35.2, 31.8),
    (44.4, 33.3), (6.1, 46.2), (-99.1, 19.4), (-47.9, -15.8), (178.4, -18.1),
    (149.1, -35.3), (174.8, -41.3), (8.5, 47.4), (121.0, 14.6), (168.3, -17.7),
    (121.6, 25.0), (37.6, 55.8),
]

# ------------------------------------------------------------- scenes -----
def _tile(w, h, bg):
    t = Image.new("RGB", (w, h), bg)
    return t, ImageDraw.Draw(t, "RGBA")
SS = 3

def vgrad(d, w, y0, y1, top, bottom):
    """Vertical gradient band drawn as 1px lines; scenes render at 3x,
    so the steps vanish in the downscale."""
    y0, y1 = int(y0), int(y1)
    span = max(1, y1 - y0)
    for yy in range(y0, y1):
        f = (yy - y0) / span
        col = tuple(int(top[i] + (bottom[i] - top[i]) * f) for i in range(3))
        d.line([(0, yy), (w, yy)], fill=col)

def render_scene(name, w, h):
    """Render a scene at 3x and downscale: smooth edges instead of
    pixel-stepped shapes, plus a whisper of grain so flat fills read
    as print rather than plastic."""
    t = SCENES[name](w * SS, h * SS).resize((w, h), Image.LANCZOS)
    noise = Image.effect_noise((w, h), 5).convert("RGB")
    return ImageChops.add(t, noise, 1, -128)


def _tanker(d, x, y, s, smoke=False):
    hull = (30, 36, 44)
    d.polygon([(x, y), (x + s, y), (x + s * 0.92, y + s * 0.16), (x + s * 0.1, y + s * 0.16)],
              fill=hull)
    d.rectangle([x + s * 0.06, y - s * 0.05, x + s * 0.8, y], fill=(172, 44, 40))
    d.rectangle([x + s * 0.68, y - s * 0.2, x + s * 0.8, y - s * 0.05], fill=(226, 222, 210))
    d.rectangle([x + s * 0.71, y - s * 0.17, x + s * 0.77, y - s * 0.11], fill=(90, 130, 160))
    if smoke:
        for i, (dx, dy, r) in enumerate([(0.74, -0.34, 0.1), (0.8, -0.48, 0.14), (0.88, -0.62, 0.19)]):
            d.ellipse([x + s * dx - s * r, y + s * dy - s * r, x + s * dx + s * r, y + s * dy + s * r],
                      fill=(96, 100, 104, 200))

def sc_hormuz(w, h):
    t, d = _tile(w, h, (188, 208, 220))
    vgrad(d, w, 0, h * 0.52, (208, 226, 238), (176, 196, 212))
    vgrad(d, w, h * 0.52, h, (60, 104, 130), (32, 68, 92))
    for i in range(9):  # wave ticks
        x = (i * 53) % int(w)
        y = h * (0.62 + (i % 3) * 0.11)
        d.line([x, y, x + w * 0.05, y], fill=(120, 170, 196), width=2)
    _tanker(d, w * 0.06, h * 0.52, w * 0.34)
    _tanker(d, w * 0.56, h * 0.6, w * 0.38, smoke=True)
    # hit flash on the second tanker's engine room
    fx, fy = w * 0.9, h * 0.52
    for a in range(0, 360, 45):
        import math
        x2 = fx + math.cos(math.radians(a)) * w * 0.035
        y2 = fy + math.sin(math.radians(a)) * h * 0.07
        d.line([fx, fy, x2, y2], fill=(232, 92, 40), width=3)
    d.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], fill=(246, 170, 50))
    return t

def sc_basra(w, h):
    t, d = _tile(w, h, (206, 170, 142))
    vgrad(d, w, 0, h, (218, 184, 152), (190, 154, 124))
    base = h * 0.86
    sil = (64, 56, 52)
    # cooling tower + chimney + blocks
    d.polygon([(w * 0.1, base), (w * 0.16, h * 0.3), (w * 0.26, h * 0.3), (w * 0.32, base)], fill=sil)
    d.rectangle([w * 0.62, h * 0.14, w * 0.68, base], fill=sil)
    d.rectangle([w * 0.36, h * 0.52, w * 0.6, base], fill=sil)
    d.rectangle([w * 0.7, h * 0.6, w * 0.94, base], fill=(84, 72, 66))
    # smoke
    for (cx, cy, r) in [(0.65, 0.1, 0.09), (0.72, 0.05, 0.12), (0.2, 0.2, 0.08)]:
        d.ellipse([w * cx - w * r, h * cy - h * r, w * cx + w * r, h * cy + h * r],
                  fill=(110, 104, 100, 190))
    # flames along the base
    import math
    for i in range(9):
        fx = w * (0.08 + i * 0.1)
        fh = h * (0.24 + 0.1 * abs(math.sin(i * 1.7)))
        d.polygon([(fx - w * 0.035, base), (fx, base - fh), (fx + w * 0.035, base)],
                  fill=(226, 108, 32))
        d.polygon([(fx - w * 0.018, base), (fx, base - fh * 0.6), (fx + w * 0.018, base)],
                  fill=(246, 186, 60))
    d.rectangle([0, base, w, h], fill=(52, 46, 44))
    return t

def sc_vanuatu(w, h):
    t, d = _tile(w, h, (168, 202, 220))
    vgrad(d, w, 0, h * 0.55, (188, 218, 236), (156, 190, 210))
    vgrad(d, w, h * 0.55, h, (66, 124, 162), (38, 92, 126))
    # island mound
    d.polygon([(w * 0.3, h * 0.56), (w * 0.44, h * 0.34), (w * 0.56, h * 0.3),
               (w * 0.7, h * 0.56)], fill=(96, 138, 84))
    d.polygon([(w * 0.44, h * 0.34), (w * 0.56, h * 0.3), (w * 0.62, h * 0.56),
               (w * 0.48, h * 0.56)], fill=(80, 118, 70))
    # crack down the island
    d.line([(w * 0.5, h * 0.33), (w * 0.47, h * 0.42), (w * 0.53, h * 0.48), (w * 0.5, h * 0.56)],
           fill=(52, 44, 36), width=max(2, h // 26))
    # seismic rings in the sea
    cx, cy = w * 0.18, h * 0.74
    for i, r in enumerate((0.05, 0.1, 0.15)):
        d.arc([cx - w * r, cy - h * r * 1.4, cx + w * r, cy + h * r * 1.4], 300, 60,
              fill=(232, 92, 40), width=max(2, h // 30))
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(232, 92, 40))
    return t

def sc_banda(w, h):
    # Banda Sea quake: same island-and-crack motif as the Vanuatu scene
    # (both are Pacific island quakes, drawn in code, not a photograph).
    return sc_vanuatu(w, h)

# ------------------------------------------------------- rich text --------

def rich_wrap(d, segments, maxw):
    """Wrap mixed-style segments into lines of (text, font, colour, width)."""
    tokens = []
    for text, fnt, col in segments:
        for w_ in text.split(" "):
            if w_:
                tokens.append((w_, fnt, col))
    lines, cur, curw = [], [], 0.0
    space = d.textlength(" ", font=segments[0][1])
    for w_, fnt, col in tokens:
        ww = d.textlength(w_, font=fnt)
        add = ww if not cur else ww + space
        if cur and curw + add > maxw:
            lines.append(cur)
            cur, curw = [(w_, fnt, col, ww)], ww
        else:
            cur.append((w_, fnt, col, ww))
            curw += add
    if cur:
        lines.append(cur)
    return lines

def draw_rich(d, x, y, lines, lh, space_fnt):
    space = d.textlength(" ", font=space_fnt)
    for line in lines:
        cx = x
        for w_, fnt, col, ww in line:
            d.text((cx, y), w_, font=fnt, fill=col)
            cx += ww + space
        y += lh
    return y



# ------------------------------------------------- new scenes (24 Nov) -----
def sc_nvidia(w, h):
    t, d = _tile(w, h, (14, 26, 20))
    vgrad(d, w, 0, h, (18, 34, 26), (10, 18, 14))
    # circuit traces
    for i, yy in enumerate((0.18, 0.82)):
        d.line([0, h * yy, w * 0.3, h * yy, w * 0.38, h * 0.5], fill=(46, 84, 60), width=max(2, h // 40))
        d.line([w, h * yy, w * 0.7, h * yy, w * 0.62, h * 0.5], fill=(46, 84, 60), width=max(2, h // 40))
        d.ellipse([w * 0.03, h * yy - 3, w * 0.03 + 6, h * yy + 3], fill=(118, 184, 60))
        d.ellipse([w * 0.95, h * yy - 3, w * 0.95 + 6, h * yy + 3], fill=(118, 184, 60))
    # the chip
    cx, cy, s = w * 0.5, h * 0.5, h * 0.62
    for k in range(5):  # pins
        px = cx - s * 0.4 + k * s * 0.2
        d.rectangle([px - 2, cy - s * 0.62, px + 2, cy - s * 0.5], fill=(150, 160, 150))
        d.rectangle([px - 2, cy + s * 0.5, px + 2, cy + s * 0.62], fill=(150, 160, 150))
    d.rounded_rectangle([cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.5],
                        int(s * 0.08), fill=(24, 30, 28), outline=(118, 184, 60), width=max(2, h // 30))
    d.rounded_rectangle([cx - s * 0.32, cy - s * 0.32, cx + s * 0.32, cy + s * 0.32],
                        int(s * 0.05), fill=(32, 40, 36), outline=(70, 110, 80), width=2)
    d.text((cx, cy), "AI", font=F(SANS_B, int(s * 0.34)), fill=(150, 205, 92), anchor="mm")
    # rising green line, bottom right
    pts = [(w * 0.66, h * 0.86), (w * 0.76, h * 0.78), (w * 0.84, h * 0.8), (w * 0.95, h * 0.6)]
    d.line(pts, fill=(118, 205, 74), width=max(3, h // 22))
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - w * 0.05, ey + h * 0.01), (ex - w * 0.008, ey + h * 0.09)],
              fill=(118, 205, 74))
    return t

def sc_shanghai(w, h):
    t, d = _tile(w, h, (44, 40, 66))
    vgrad(d, w, 0, h, (66, 52, 84), (30, 28, 52))
    # big red sun / seal disc behind the skyline
    d.ellipse([w * 0.6, h * 0.04, w * 0.94, h * 0.72], fill=(178, 44, 40))
    d.ellipse([w * 0.63, h * 0.08, w * 0.91, h * 0.66], fill=(192, 56, 48))
    base = h * 0.97
    sil = (16, 14, 28)
    # skyline blocks
    for (fx, fw, fh) in [(0.0, 0.1, 0.5), (0.1, 0.07, 0.66), (0.19, 0.09, 0.44),
                         (0.3, 0.06, 0.58), (0.68, 0.08, 0.4), (0.78, 0.06, 0.55),
                         (0.86, 0.09, 0.36), (0.96, 0.05, 0.48)]:
        d.rectangle([w * fx, base - h * fh, w * (fx + fw), base], fill=sil)
    # pearl-tower silhouette: column, two spheres
    tx = w * 0.47
    d.rectangle([tx - w * 0.012, base - h * 0.8, tx + w * 0.012, base], fill=sil)
    d.ellipse([tx - w * 0.045, base - h * 0.52, tx + w * 0.045, base - h * 0.34], fill=sil)
    d.ellipse([tx - w * 0.03, base - h * 0.8, tx + w * 0.03, base - h * 0.66], fill=sil)
    # lit windows
    for i in range(22):
        x = (i * 41) % int(w)
        y = h * 0.55 + (i * 29) % int(h * 0.38)
        d.rectangle([x, y, x + 2, y + 3], fill=(240, 205, 110, 170))
    d.rectangle([0, base, w, h], fill=(10, 9, 20))
    return t

def sc_kyiv2(w, h):
    t, d = _tile(w, h, (16, 22, 40))
    vgrad(d, w, 0, h, (24, 32, 56), (10, 14, 28))
    # horizon glow (fires far off)
    d.ellipse([w * 0.55, h * 0.52, w * 1.05, h * 0.95], fill=(120, 52, 30))
    d.ellipse([w * 0.62, h * 0.6, w * 0.98, h * 0.92], fill=(178, 84, 36))
    base = h * 0.96
    sil = (6, 8, 16)
    for (fx, fw, fh) in [(0.0, 0.12, 0.42), (0.13, 0.08, 0.55), (0.23, 0.1, 0.38),
                         (0.35, 0.07, 0.48), (0.6, 0.09, 0.34), (0.72, 0.07, 0.44),
                         (0.82, 0.1, 0.3), (0.94, 0.07, 0.4)]:
        d.rectangle([w * fx, base - h * fh, w * (fx + fw), base], fill=sil)
    # searchlight beams
    for bx in (0.2, 0.45):
        d.polygon([(w * bx, base), (w * (bx + 0.1), h * 0.05), (w * (bx + 0.17), h * 0.05)],
                  fill=(210, 220, 235, 60))
    # drones: small x silhouettes with red eyes
    import math
    for (dx, dy, s) in [(0.3, 0.22, 0.05), (0.55, 0.14, 0.065), (0.78, 0.3, 0.045)]:
        cx, cy = w * dx, h * dy
        for a in (45, 135, 225, 315):
            x2 = cx + math.cos(math.radians(a)) * w * s
            y2 = cy + math.sin(math.radians(a)) * h * s * 0.8
            d.line([cx, cy, x2, y2], fill=(190, 198, 210), width=max(2, h // 34))
            d.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], fill=(190, 198, 210))
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(232, 60, 48))
    d.rectangle([0, base, w, h], fill=(4, 5, 10))
    return t

def sc_sanofi(w, h):
    t, d = _tile(w, h, (206, 224, 228))
    vgrad(d, w, 0, h, (216, 233, 236), (192, 210, 214))
    # molecule circles behind
    for (mx, my, r, col) in [(0.14, 0.3, 0.1, (150, 190, 200)), (0.24, 0.52, 0.06, (120, 170, 190)),
                             (0.86, 0.24, 0.08, (150, 190, 200)), (0.78, 0.44, 0.05, (120, 170, 190))]:
        d.ellipse([w * (mx - r), h * (my - r * 1.6), w * (mx + r), h * (my + r * 1.6)], fill=col)
    d.line([w * 0.17, h * 0.4, w * 0.22, h * 0.48], fill=(120, 170, 190), width=3)
    d.line([w * 0.83, h * 0.3, w * 0.79, h * 0.4], fill=(120, 170, 190), width=3)
    # big capsule, diagonal
    import math
    cx, cy, L, R = w * 0.5, h * 0.52, w * 0.52, h * 0.21
    ang = -24
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    px, py = -dy, dx
    x0, y0 = cx - dx * L / 2, cy - dy * L / 2
    x1, y1 = cx + dx * L / 2, cy + dy * L / 2
    d.line([x0, y0, x1, y1], fill=(238, 240, 244), width=int(R * 2))
    d.line([x0, y0, cx, cy], fill=(52, 110, 168), width=int(R * 2))
    d.ellipse([x0 - R, y0 - R, x0 + R, y0 + R], fill=(52, 110, 168))
    d.ellipse([x1 - R, y1 - R, x1 + R, y1 + R], fill=(238, 240, 244))
    d.line([x0 + px * R, y0 + py * R, x1 + px * R, y1 + py * R], fill=(90, 100, 110), width=2)
    d.line([x0 - px * R, y0 - py * R, x1 - px * R, y1 - py * R], fill=(90, 100, 110), width=2)
    return t

def sc_hanoi(w, h):
    t, d = _tile(w, h, (214, 196, 168))
    vgrad(d, w, 0, h, (226, 208, 178), (196, 172, 140))
    ground = h * 0.88
    # neighbouring facades
    d.rectangle([0, h * 0.18, w * 0.2, ground], fill=(168, 148, 122))
    d.rectangle([w * 0.82, h * 0.12, w, ground], fill=(160, 140, 116))
    for i in range(3):
        d.rectangle([w * 0.04, h * (0.3 + i * 0.18), w * 0.13, h * (0.4 + i * 0.18)], fill=(96, 92, 88))
        d.rectangle([w * 0.87, h * (0.26 + i * 0.18), w * 0.96, h * (0.36 + i * 0.18)], fill=(96, 92, 88))
    # the stricken eatery: walls, blown-out front
    d.rectangle([w * 0.24, h * 0.3, w * 0.78, ground], fill=(188, 168, 138))
    d.rectangle([w * 0.3, h * 0.52, w * 0.72, ground], fill=(52, 46, 42))
    d.rectangle([w * 0.24, h * 0.3, w * 0.78, h * 0.4], fill=(120, 60, 44))  # awning band
    # flames + smoke from the opening
    import math
    for i in range(7):
        fx = w * (0.36 + i * 0.05)
        fh = h * (0.2 + 0.12 * abs(math.sin(i * 2.1)))
        d.polygon([(fx - w * 0.028, h * 0.62), (fx, h * 0.62 - fh), (fx + w * 0.028, h * 0.62)],
                  fill=(232, 110, 40))
        d.polygon([(fx - w * 0.015, h * 0.62), (fx, h * 0.62 - fh * 0.55), (fx + w * 0.015, h * 0.62)],
                  fill=(246, 178, 60))
    for (sx, sy, r) in [(0.42, 0.2, 0.09), (0.55, 0.12, 0.12), (0.68, 0.18, 0.08)]:
        d.ellipse([w * (sx - r), h * (sy - r), w * (sx + r), h * (sy + r)], fill=(104, 98, 94, 190))
    # debris
    for (dx, dy, s) in [(0.3, 0.9, 0.05), (0.55, 0.93, 0.04), (0.7, 0.9, 0.06)]:
        d.polygon([(w * dx, h * dy), (w * (dx + s), h * dy), (w * (dx + s * 0.4), h * (dy - 0.05))],
                  fill=(120, 108, 92))
    d.rectangle([0, ground, w, h], fill=(150, 130, 104))
    return t

def sc_gaza2(w, h):
    t, d = _tile(w, h, (226, 204, 170))
    vgrad(d, w, 0, h, (236, 216, 182), (206, 182, 142))
    d.ellipse([w * 0.8, h * 0.06, w * 0.94, h * 0.26], fill=(246, 200, 92))
    ground = h * 0.86
    sil = (120, 104, 84)
    # damaged skyline: blocks with notched tops
    for (fx, fw, fh, notch) in [(0.02, 0.14, 0.5, 0.0), (0.18, 0.1, 0.62, 0.12),
                                (0.3, 0.13, 0.44, 0.0), (0.45, 0.09, 0.56, 0.2),
                                (0.56, 0.12, 0.4, 0.0), (0.7, 0.1, 0.52, 0.1),
                                (0.82, 0.15, 0.46, 0.0)]:
        d.rectangle([w * fx, ground - h * fh, w * (fx + fw), ground], fill=sil)
        if notch:
            d.rectangle([w * (fx + fw * 0.3), ground - h * fh, w * (fx + fw * 0.75),
                         ground - h * (fh - notch)], fill=(226, 204, 170))
    # smoke plumes
    for (sx, sy, r) in [(0.23, 0.2, 0.07), (0.27, 0.1, 0.1), (0.62, 0.26, 0.06), (0.66, 0.16, 0.09)]:
        d.ellipse([w * (sx - r), h * (sy - r * 0.8), w * (sx + r), h * (sy + r * 0.8)],
                  fill=(110, 102, 96, 200))
    d.rectangle([0, ground, w, h], fill=(188, 164, 124))
    return t

def sc_space(w, h):
    t, d = _tile(w, h, (12, 18, 38))
    vgrad(d, w, 0, h, (16, 24, 48), (8, 12, 28))
    # stars
    for i in range(30):
        x = (i * 53) % int(w)
        y = (i * 31) % int(h * 0.8)
        d.ellipse([x, y, x + 2, y + 2], fill=(220, 226, 240))
    # earth arc at bottom
    d.ellipse([w * -0.3, h * 0.72, w * 1.3, h * 2.2], fill=(52, 96, 150))
    d.ellipse([w * 0.1, h * 0.86, w * 0.5, h * 1.3], fill=(70, 130, 90))
    # orbit ellipse
    d.ellipse([w * 0.08, h * 0.08, w * 0.95, h * 0.72], outline=(120, 140, 170), width=2)
    # satellite: body + two panel wings
    cx, cy = w * 0.52, h * 0.38
    d.rectangle([cx - w * 0.05, cy - h * 0.09, cx + w * 0.05, cy + h * 0.09], fill=(200, 204, 210))
    for sgn in (-1, 1):
        x0 = cx + sgn * w * 0.06
        x1 = cx + sgn * w * 0.24
        d.rectangle([min(x0, x1), cy - h * 0.13, max(x0, x1), cy + h * 0.13], fill=(52, 84, 150),
                    outline=(120, 150, 200), width=1)
        for k in (0.33, 0.66):
            lx = x0 + (x1 - x0) * k
            d.line([lx, cy - h * 0.13, lx, cy + h * 0.13], fill=(120, 150, 200), width=1)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(240, 200, 90))
    # the reported second satellite, small, red-lit, upper right on the orbit
    sx, sy = w * 0.86, h * 0.16
    d.rectangle([sx - w * 0.02, sy - h * 0.04, sx + w * 0.02, sy + h * 0.04], fill=(150, 150, 158))
    d.rectangle([sx - w * 0.09, sy - h * 0.025, sx - w * 0.025, sy + h * 0.025], fill=(70, 60, 80))
    d.rectangle([sx + w * 0.025, sy - h * 0.025, sx + w * 0.09, sy + h * 0.025], fill=(70, 60, 80))
    d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(232, 60, 48))
    return t

def sc_congo(w, h):
    t, d = _tile(w, h, (84, 120, 74))
    vgrad(d, w, 0, h, (96, 134, 82), (66, 100, 58))
    # jungle canopy blobs
    for (bx, by, r) in [(0.08, 0.2, 0.16), (0.3, 0.1, 0.13), (0.9, 0.16, 0.15), (0.72, 0.08, 0.11)]:
        d.ellipse([w * (bx - r), h * (by - r), w * (bx + r), h * (by + r)], fill=(58, 96, 52))
    ground = h * 0.84
    d.rectangle([0, ground, w, h], fill=(150, 124, 88))  # dirt
    # white field hospital
    hx, hy, hw, hh = w * 0.3, ground - h * 0.52, w * 0.42, h * 0.52
    d.rectangle([hx, hy, hx + hw, ground], fill=(246, 244, 238), outline=(170, 164, 150), width=1)
    d.polygon([(hx - w * 0.03, hy), (hx + hw * 0.5, hy - h * 0.16), (hx + hw + w * 0.03, hy)],
              fill=(196, 60, 52))
    # red cross
    ccx, ccy, cs = hx + hw * 0.5, hy + hh * 0.42, h * 0.13
    d.rectangle([ccx - cs * 0.32, ccy - cs, ccx + cs * 0.32, ccy + cs], fill=(206, 44, 40))
    d.rectangle([ccx - cs, ccy - cs * 0.32, ccx + cs, ccy + cs * 0.32], fill=(206, 44, 40))
    d.rectangle([hx + hw * 0.08, ground - h * 0.2, hx + hw * 0.26, ground], fill=(90, 84, 78))
    # ambulance hint at right
    ax, ay = w * 0.78, ground - h * 0.2
    d.rounded_rectangle([ax, ay, ax + w * 0.18, ground], int(h * 0.03), fill=(240, 238, 232))
    d.ellipse([ax + w * 0.03, ground - h * 0.045, ax + w * 0.07, ground], fill=(40, 40, 44))
    d.ellipse([ax + w * 0.12, ground - h * 0.045, ax + w * 0.16, ground], fill=(40, 40, 44))
    d.rectangle([ax + w * 0.075, ay + h * 0.05, ax + w * 0.105, ay + h * 0.11], fill=(206, 44, 40))
    return t

def sc_dhaka(w, h):
    t, d = _tile(w, h, (150, 190, 216))
    vgrad(d, w, 0, h, (170, 205, 228), (128, 168, 198))
    d.ellipse([w * 0.82, h * 0.08, w * 0.95, h * 0.3], fill=(246, 210, 100))  # sun
    # bangladesh flag disc, upper left
    d.ellipse([w * 0.05, h * 0.1, w * 0.24, h * 0.52], fill=(0, 106, 78))
    d.ellipse([w * 0.095, h * 0.17, w * 0.2, h * 0.45], fill=(244, 42, 65))
    # airliner climbing, side profile (simplified from the Davao scene)
    ax, ay, aw = w * 0.3, h * 0.44, w * 0.6
    d.rounded_rectangle([ax, ay, ax + aw, ay + h * 0.17], int(h * 0.045), fill=(238, 238, 234))
    d.polygon([(ax + aw * 0.86, ay - h * 0.14), (ax + aw * 0.99, ay + h * 0.02),
               (ax + aw * 0.86, ay + h * 0.04)], fill=(0, 106, 78))
    d.polygon([(ax + aw * 0.3, ay + h * 0.14), (ax + aw * 0.52, ay + h * 0.14),
               (ax + aw * 0.44, ay + h * 0.24), (ax + aw * 0.34, ay + h * 0.24)],
              fill=(200, 200, 196))
    for i in range(7):
        wx = ax + aw * (0.14 + i * 0.09)
        d.ellipse([wx, ay + h * 0.045, wx + w * 0.018, ay + h * 0.09], fill=(90, 130, 165))
    # climb trail
    d.line([w * 0.06, h * 0.92, ax + w * 0.02, ay + h * 0.2], fill=(240, 244, 248), width=3)
    d.rectangle([0, h * 0.94, w, h], fill=(90, 110, 96))
    return t

def sc_grok(w, h):
    t, d = _tile(w, h, (30, 32, 44))
    vgrad(d, w, 0, h, (38, 40, 56), (22, 24, 34))
    # smartphone
    px, py, pw, ph = w * 0.36, h * 0.06, w * 0.28, h * 0.88
    d.rounded_rectangle([px, py, px + pw, py + ph], int(h * 0.05), fill=(16, 17, 24),
                        outline=(120, 126, 140), width=2)
    d.rectangle([px + pw * 0.12, py + ph * 0.1, px + pw * 0.88, py + ph * 0.52], fill=(52, 58, 76))
    # picture glyph inside the screen: hills + sun
    d.ellipse([px + pw * 0.58, py + ph * 0.16, px + pw * 0.76, py + ph * 0.3], fill=(240, 200, 90))
    d.polygon([(px + pw * 0.14, py + ph * 0.5), (px + pw * 0.44, py + ph * 0.26),
               (px + pw * 0.62, py + ph * 0.5)], fill=(90, 140, 100))
    # chat lines below
    for i in range(2):
        yy = py + ph * (0.62 + i * 0.14)
        d.rounded_rectangle([px + pw * 0.12, yy, px + pw * (0.8 - i * 0.18), yy + ph * 0.08],
                            int(h * 0.02), fill=(70, 76, 94))
    # warning triangle over the phone's corner
    tx, ty, ts = px + pw * 0.92, py + ph * 0.62, h * 0.3
    d.polygon([(tx, ty - ts * 0.55), (tx - ts * 0.5, ty + ts * 0.4), (tx + ts * 0.5, ty + ts * 0.4)],
              fill=(232, 170, 40), outline=(150, 110, 20), width=2)
    d.text((tx, ty + ts * 0.02), "!", font=F(SANS_B, int(ts * 0.62)), fill=(40, 32, 8), anchor="mm")
    return t

SCENES = {
    "nvidia": sc_nvidia, "shanghai": sc_shanghai, "kyiv2": sc_kyiv2,
    "sanofi": sc_sanofi, "hanoi": sc_hanoi, "gaza2": sc_gaza2,
    "hormuz": sc_hormuz, "space": sc_space, "congo": sc_congo,
    "dhaka": sc_dhaka, "banda": sc_banda, "grok": sc_grok,
    "basra": sc_basra,
}


# ------------------------------------------------------------- canvas -----
MX = 16
CW = W - 2 * MX           # 992
canvas = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(canvas, "RGBA")

# kicker
d.text((MX, 11), "THE WORLD IN ONE DAY", font=F(SERIF_B, 16), fill=RED)
d.text((W - MX, 13), "36 STORIES · EVERY CONTINENT · ALL FROM THIS ONE DAY",
       font=F(SANS_B, 12.5), fill=INK, anchor="ra")
d.line([(MX, 35), (W - MX, 35)], fill=INK, width=2)

# masthead
mh = fit(d, "Tuesday 24 November 2026", SERIF_B, 68, CW)
d.text((MX, 38), "Tuesday 24 November 2026", font=mh, fill=INK)
ink_bottom = d.textbbox((MX, 38), "Tuesday 24 November 2026", font=mh)[3]

# standfirst (placed from the masthead's real ink bottom, never over it)
sf_text = ("A Politburo member falls in Shanghai · Nvidia\u2019s returned king faces a boardroom revolt · Sanofi bets $41bn on a drugmaker")
sf = fit(d, sf_text, SERIF_I, 17, CW, floor=12)
d.text((MX, ink_bottom + 3), sf_text, font=sf, fill=DARKRED)

# region tally bar
ry, rh = 152, 22
rf = F(SANS_B, 11.5)
mins = [d.textlength(f"{n} {c}", font=rf) + 20 for n, c, _ in REGIONS]
extra = CW - sum(mins)
tot = sum(c for _, c, _ in REGIONS)
x = MX
for (name, cnt, col), mn in zip(REGIONS, mins):
    wseg = mn + extra * cnt / tot
    d.rectangle([x, ry, x + wseg, ry + rh], fill=col)
    d.text((x + wseg / 2, ry + rh / 2), f"{name} {cnt}", font=rf,
           fill=(255, 255, 255), anchor="mm")
    x += wseg

# the day in numbers
sy, sh = 178, 42
d.rectangle([MX, sy, MX + 92, sy + sh], fill=RED)
lab = wrap(d, "THE DAY IN NUMBERS", F(SANS_B, 12), 84)
ly = sy + (sh - len(lab) * 13) / 2
for ln in lab:
    d.text((MX + 46, ly), ln, font=F(SANS_B, 12), fill=(255, 255, 255), anchor="ma")
    ly += 13
sx = MX + 100
scw = (W - MX - sx) / 6
for i, (big, cap) in enumerate(STATS):
    cx = sx + i * scw
    bf = fit(d, big, SERIF_B, 23, scw - 8, floor=14)
    d.text((cx + scw / 2, sy), big, font=bf, fill=DARKRED, anchor="ma")
    cf = F(SANS_R, 9.5)
    for j, ln in enumerate(wrap(d, cap, cf, scw - 10)[:2]):
        d.text((cx + scw / 2, sy + 24 + j * 10.5), ln, font=cf, fill=SOFT, anchor="ma")
d.line([(MX, 228), (W - MX, 228)], fill=INK, width=1)

# ------------------------------------------------------------- heroes -----
HY, HH = 234, 218
HW = (CW - 2 * 13) // 3   # 322
for i, hd in enumerate(HEROES):
    x = MX + i * (HW + 13)
    y = HY
    d.rectangle([x, y, x + HW, y + HH], fill=CARD, outline=BORDER, width=1)
    tile = render_scene(hd["scene"], HW, 96)
    canvas.paste(tile, (x, y))
    by = y + 96 - 17
    d.rectangle([x, by, x + HW, y + 96], fill=NAVY + (238,))
    d.text((x + 8, by + 2.5), hd["bl"], font=F(SANS_B, 10), fill=(255, 255, 255))
    d.text((x + HW - 8, by + 2.5), hd["br"], font=F(SANS_B, 10), fill=GOLD, anchor="ra")
    ty = y + 96 + 6
    badge(d, x + 13, ty + 7, 8.5, hd["n"], 9)
    d.text((x + 27, ty + 1), f"{hd['loc']} · {hd['cat']}", font=F(SANS_B, 10.5),
           fill=DARKRED)
    pill(d, x + HW - 8 - (d.textlength(hd["tag"], font=F(SANS_B, 8)) + 10), ty + 1, hd["tag"])
    hyy = ty + 19
    hf = F(SERIF_B, 19)
    for ln in wrap(d, hd["head"], hf, HW - 20)[:2]:
        d.text((x + 10, hyy), ln, font=hf, fill=INK)
        hyy += 21
    bf = F(SANS_R, 11)
    for ln in wrap(d, hd["body"], bf, HW - 20)[:3]:
        d.text((x + 10, hyy + 1), ln, font=bf, fill=(52, 58, 60))
        hyy += 12
    d.text((x + 10, hyy + 3), hd["src"], font=F(SANS_I, 9.5), fill=SOFT)

# ------------------------------------------------------------- smalls -----
GY = HY + HH + 6
SW = (CW - 4 * 10) / 5    # 190.4
SH = 148
for i, sd_ in enumerate(SMALLS):
    r, c = divmod(i, 5)
    x = int(MX + c * (SW + 10))
    y = GY + r * (SH + 6)
    wpx = int(SW)
    d.rectangle([x, y, x + wpx, y + SH], fill=CARD, outline=BORDER, width=1)
    tile = render_scene(sd_["scene"], wpx, 68)
    canvas.paste(tile, (x, y))
    d.rectangle([x, y + 56, x + wpx, y + 68], fill=NAVY + (238,))
    d.text((x + 6, y + 57.5), sd_["band"], font=F(SANS_B, 8.5), fill=(255, 255, 255))
    ty = y + 72
    badge(d, x + 9, ty + 5, 6, sd_["n"], 7.5)
    d.text((x + 19, ty), f"{sd_['loc']} · {sd_['cat']}", font=F(SANS_B, 8), fill=DARKRED)
    tf = F(SANS_B, 7.5)
    tw = d.textlength(sd_["tag"], font=tf) + 8
    col = {"REPORTED": GREEN, "CLAIM": AMBER, "FORECAST": STEEL}[sd_["tag"]]
    d.rounded_rectangle([x + wpx - 6 - tw, ty, x + wpx - 6, ty + 11], 3, fill=col)
    d.text((x + wpx - 6 - tw + 4, ty + 1), sd_["tag"], font=tf, fill=(255, 255, 255))
    hyy = ty + 13
    hf = F(SERIF_B, 12.5)
    for ln in wrap(d, sd_["head"], hf, wpx - 14)[:2]:
        d.text((x + 7, hyy), ln, font=hf, fill=INK)
        hyy += 14.5
    segs = [(sd_["body"] + " ", F(SANS_R, 9.6), (52, 58, 60)),
            ("\u2014 " + sd_["src"], F(SANS_I, 9.6), SOFT)]
    lines = rich_wrap(d, segs, wpx - 14)[:2]
    draw_rich(d, x + 7, hyy + 1, lines, 11, F(SANS_R, 9.6))

# ------------------------------------------------------------- bottom -----
BY = GY + 2 * SH + 14
d.text((MX, BY), "WHERE IT HAPPENED", font=F(SANS_B, 12.5), fill=INK)
d.text((MX + 168, BY + 2), "numbers match the stories", font=F(SANS_I, 9.5), fill=SOFT)
d.text((428, BY), "ALSO ON TUESDAY", font=F(SANS_B, 12.5), fill=INK)
d.text((428 + 152, BY), "— 23 MORE STORIES", font=F(SANS_B, 12.5), fill=RED)
d.text((W - MX, BY + 2), "place · what happened · source", font=F(SANS_I, 9.5),
       fill=SOFT, anchor="ra")

# map: solid continents (Natural Earth 110m outlines, simplified) on a
# navy panel -- the treatment every finalist page used. Drawn on its own
# layer so antimeridian-crossing polygons clip at the panel edge.
mapx, mapy, mapw, maph = MX + 4, BY + 20, 392, 116
PANEL = (23, 38, 58)
d.rectangle([mapx - 6, mapy - 6, mapx + mapw + 6, mapy + maph + 6], fill=PANEL)
MSS = 3
mapimg = Image.new("RGB", (mapw * MSS, maph * MSS), PANEL)
md = ImageDraw.Draw(mapimg)

def proj(lon, lat):
    return ((lon + 180) / 360 * mapw * MSS, (84 - lat) / 144 * maph * MSS)

LAND = (219, 205, 170)
LAND_EDGE = (188, 170, 128)
for poly in POLYS_HQ:
    md.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
               outline=LAND_EDGE)
for lon, lat in DOTS:
    px, py = proj(lon, lat)
    md.ellipse([px - 2.6 * MSS, py - 2.6 * MSS, px + 2.6 * MSS, py + 2.6 * MSS],
               fill=(126, 200, 188))
for num, lon, lat in PINS:
    px, py = proj(lon, lat)
    md.ellipse([px - 7 * MSS, py - 7 * MSS, px + 7 * MSS, py + 7 * MSS],
               fill=RED, outline=(255, 255, 255), width=MSS)
    md.text((px, py - 0.5 * MSS), str(num), font=F(SANS_B, 8 * MSS),
            fill=(255, 255, 255), anchor="mm")
canvas.paste(mapimg.resize((mapw, maph), Image.LANCZOS), (mapx, mapy))
ly = mapy + maph + 6
d.text((MX, ly), "Red pins: the 13 stories \u00b7 teal dots + coloured numbers: the briefs, by region",
       font=F(SANS_R, 8.5), fill=SOFT)
d.text((MX, ly + 11), "Tags: REPORTED = named sources \u00b7 CLAIM = one side\u2019s account \u00b7 FORECAST = expected",
       font=F(SANS_R, 8.5), fill=SOFT)
d.text((MX, ly + 22), "UTC 01:30 Hanoi blast \u00b7 08:34 Paris: Sanofi +5.6% \u00b7 overnight: 96 drones on Ukraine",
       font=F(SANS_B, 8.5), fill=INK)

# briefs, two columns -- font auto-fitted so the columns end above the
# date-check box (measured before anything is drawn)
cols = [BRIEFS[:12], BRIEFS[12:]]
colw = 284
BRIEF_TOP = BY + 22
BRIEF_BOT = 940
def brief_layout(bsize):
    lh = bsize + 1.9
    out = []
    for col in cols:
        items, total = [], 0.0
        for num, place, fact, src in col:
            segs = [(place, F(SANS_B, bsize), INK),
                    (" \u2014 " + fact + " ", F(SANS_R, bsize), (52, 58, 60)),
                    (src, F(SANS_I, bsize), SOFT)]
            lines = rich_wrap(d, segs, colw - 17)
            items.append((num, lines))
            total += len(lines) * lh + 1.4
        out.append((items, total))
    return out, lh

bsize = 9.6
layout, blh = brief_layout(bsize)
while max(t for _, t in layout) > BRIEF_BOT - BRIEF_TOP and bsize > 8.0:
    bsize -= 0.3
    layout, blh = brief_layout(bsize)
for ci, (items, _t) in enumerate(layout):
    bx = 428 + ci * (colw + 12)
    yy = BRIEF_TOP
    for num, lines in items:
        d.text((bx, yy), str(num), font=F(SANS_B, bsize),
               fill=REGION_COL[BRIEF_REGION[num]])
        yy = draw_rich(d, bx + 17, yy, lines, blh, F(SANS_R, bsize)) + 1.4

# date check box (tick drawn with lines: the serif/sans fonts lack a
# checkmark glyph)
DY = 946
d.rectangle([MX, DY, W - MX, DY + 44], outline=RED, width=2)
d.line([(MX + 12, DY + 13), (MX + 16, DY + 18)], fill=RED, width=3)
d.line([(MX + 16, DY + 18), (MX + 25, DY + 7)], fill=RED, width=3)
dc = [("DATE CHECK  ", F(SANS_B, 10), RED),
      ("Every story on this page happened, or was first reported, on Tuesday "
       "24 November 2026. LEFT OUT AS OTHER DAYS\u2019 NEWS \u2014 Sun 22 Nov: Russian "
       "strikes kill 15 in the Kyiv region \u00b7 12,000 evacuated from a Manchester "
       "arena. Mon 23 Nov: COP31 talks collapse in Antalya, no deal \u00b7 Nvidia "
       "reinstates Huang as CEO \u00b7 court clears the Iowa detonation \u00b7 "
       "Democrats win biggest House majority since 1992. Sat 21 Nov: "
       "the Banten factory fire breaks out (toll confirmed today). "
       "NOT YET: the Iowa detonation, set for Wednesday \u00b7 Eisenkot\u2019s "
       "government (deadline Dec 6) \u00b7 Hasina\u2019s flight home (Dec 16).",
       F(SANS_R, 9.8), INK)]
lines = rich_wrap(d, dc, CW - 42)[:3]
draw_rich(d, MX + 31, DY + 6, lines, 11.5, F(SANS_R, 9.8))

# footer
foot = ("Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 Bloomberg \u00b7 SCMP \u00b7 Xinhua \u00b7 Kyiv Independent \u00b7 "
        "UN News \u00b7 Japan Times \u00b7 PINA \u00b7 MercoPress \u2014 "
        "Claims are attributed, not stated as fact \u00b7 Pictures and map drawn in code, "
        "not photographs")
ff = fit(d, foot, SANS_R, 9, CW, floor=7)
d.text((W // 2, 997), foot, font=ff, fill=SOFT, anchor="ma")

canvas.save(OUT, "PNG", optimize=True)
size = os.path.getsize(OUT)
print("saved", OUT, canvas.size, size, "bytes")
if size > 1000 * 1000:
    q = canvas.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
    q.save(OUT, "PNG", optimize=True)
    print("quantized ->", os.path.getsize(OUT), "bytes")
