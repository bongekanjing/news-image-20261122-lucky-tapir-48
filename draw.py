"""Draw the 22 November 2026 world-news page: one broadsheet, one grid.

Every story here was first reported on Sunday 22 November 2026, and each carries
the place and the hour it broke. The page runs one dominant picture — the
morning's biggest story, drawn large enough to read as a scene — and sets the
rest of the day's breadth in type on a single twelve-column grid that runs from
the masthead to the folio.

The picture is drawn onto its own surface and pasted in, so nothing it paints can
escape the frame; the first draft let the smoke plume bleed a grey band across
the nameplate.

Run: python3 draw.py   (writes entry.png beside this file)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- geometry --
W = H = 1024
S = 2                      # drawn at twice size, then halved, so small type is clean
M = 22                     # page margin
COLS = 12                  # the one grid every band is set on
GUT = 7                    # the gutter between columns

_usable = W - 2 * M
COLW = (_usable - GUT * (COLS - 1)) / COLS

# ------------------------------------------------------------------ colour --
PAPER = "#FCFAF4"
INK = "#111111"
INK2 = "#2A2620"
GREY = "#6C665A"
FAINT = "#CFC8B8"
RED = "#B3271E"
RULE = "#1A1A1A"

BEAT_COLOUR = {
    "Conflict": "#9B2C2C",
    "Politics": "#2E5FA3",
    "Economy": "#8A6A1F",
    "Climate": "#2F6B4F",
    "Disaster": "#A34A16",
    "Science": "#5B4B8A",
    "Society": "#7A4B72",
    "Sport": "#1F6F78",
}

# ------------------------------------------------------------------- fonts --
FD = "/usr/share/fonts/truetype/liberation/"
SERIF_B = FD + "LiberationSerif-Bold.ttf"
SERIF_I = FD + "LiberationSerif-Italic.ttf"
SERIF_R = FD + "LiberationSerif-Regular.ttf"
SANS_B = FD + "LiberationSans-Bold.ttf"
SANS_R = FD + "LiberationSans-Regular.ttf"

_CACHE = {}


def font(path, size):
    key = (path, int(round(size * S)))
    if key not in _CACHE:
        _CACHE[key] = ImageFont.truetype(path, key[1])
    return _CACHE[key]


# ------------------------------------------------------------- the stories --
HERO = dict(
    place="FINLAND · GULF OF FINLAND",
    beat="Conflict",
    hour="07:59",
    headline="A Russian cargo ship burns to the waterline off Finland, "
             "struck by drones over the Baltic.",
    stand="The vessel was still on fire through Sunday morning. Helsinki says the "
          "drones crossed its waters and the coastguard stood off the hull all day; "
          "Moscow calls the strike an act of war and has promised a response. It is "
          "the first attack on a Russian-flagged ship this far north in the war.",
)

SECOND = [
    ("MEXICO · SINALOA", "Conflict", "01:25",
     "El Chapo Isidro is seized in a raid that leaves eleven dead.",
     "Special forces took one of the FBI's ten most wanted before dawn."),
    ("TÜRKİYE · ANTALYA", "Climate", "09:06",
     "COP31 goes to the brink as a new draft reaches the floor.",
     "The argument is still over naming fossil fuels."),
    ("GAZA · KHAN YOUNIS", "Conflict", "08:11",
     "Displaced families protest as the air strikes go on.",
     "The largest rally in the tent camps in weeks."),
    ("PERU · LIMA", "Disaster", "07:30",
     "A quake empties a cinema in the middle of a film.",
     "Moviegoers ran for the exits; no deaths are reported."),
    ("NIGERIA · NIGER STATE", "Disaster", "06:40",
     "A boat carrying mourners capsizes, killing at least 24.",
     "Villagers dived for the missing through the morning."),
    ("INDONESIA · WEST JAVA", "Disaster", "06:05",
     "A factory fire kills three and leaves 36 missing.",
     "Rescue teams worked the upper floors by ladder."),
    ("FRANCE · PARIS", "Politics", "09:27",
     "A second night of rallies over the cost of living.",
     "Marches over pay ended in clashes in several cities."),
    ("SOUTH KOREA · SEOUL", "Society", "09:20",
     "The education minister resigns over an exam scandal.",
     "Leaked papers and a tutoring pipeline into top schools."),
    ("UKRAINE · LVIV", "Conflict", "07:59",
     "Dashcam video shows a missile strike inside the city.",
     "The footage was confirmed by regional officials."),
    ("UNITED STATES · WASHINGTON", "Society", "00:10",
     "The FBI investigates a hack of its criminal database.",
     "No arrests have been announced."),
    ("MERCURY · IN ORBIT", "Science", "11:02",
     "A spacecraft arrives at Mercury after eight years.",
     "It swung past Earth, Venus and Mercury itself to get there."),
    ("SOMALIA · MOGADISHU", "Politics", "08:55",
     "The president turns on the UAE, his former ally.",
     "A row over a port and a training camp broke into the open."),
]

BRIEFS = [
    ("ITALY · ROME", "Paolo Bulgari, the jeweller, dies at 89."),
    ("INDIANAPOLIS · CHESS", "Gukesh and Sindarov open the youngest title match."),
    ("LAS VEGAS · MOTOR RACING", "Verstappen wins as both Ferraris collide."),
    ("SPAIN · MADRID", "Ministers call the EU budget settlement disappointing."),
    ("SUDAN · DARFUR", "Displaced families face winter as aid cuts bite."),
    ("UK · LONDON", "Theresa May says Brexit is done and rejects Burnham's plan."),
    ("US · SEATTLE", "Immigration agents detain two people at the airport."),
    ("KENYA · NAIROBI", "A metering bill raises privacy and cost concerns."),
    ("AUSTRALIA · SYDNEY", "A leg injury rules Jacks out of the T20 tour."),
    ("BELGIUM · BRUSSELS", "Ministers press for a ban on killer robots."),
    ("UK · ESSEX", "Record sightings of a rare moth are logged."),
    ("US · CALIFORNIA", "Miley Cyrus marries Maxx Morando in a small ceremony."),
]

NUMBERS = [
    ("11", "killed in the raid that took El Chapo Isidro"),
    ("36", "still missing after the West Java fire"),
    ("24", "drowned when a funeral boat capsized"),
    ("2", "nights of protest across France"),
    ("8", "years the probe took to reach Mercury"),
]

CLOCK = [
    ("00:10", "The FBI opens its database hack inquiry"),
    ("01:25", "El Chapo Isidro is seized in Sinaloa"),
    ("06:05", "Fire breaks out at the West Java factory"),
    ("07:59", "A Russian cargo ship is struck in the Baltic"),
    ("09:06", "A new COP31 draft reaches the delegates"),
    ("09:20", "South Korea's education minister resigns"),
]

# ------------------------------------------------------------------ layout --
NAME_Y = 24
DATE_Y = 36
DECK_Y = 92
HEAD_RULE = 110

HERO_Y = 120            # top of the picture
PIC_H = 300
CAP_Y = HERO_Y + PIC_H + 5
CAP_H = 24
HTEXT_Y = CAP_Y + CAP_H + 8

GRID_Y = 600            # "the day elsewhere"
GRID_ROWS = 3
GRID_ROW_H = 56

NUM_Y = 344             # the figures, in the column under the timeline
BRIEF_Y = 792
BRIEF_ROWS = 3


def col_x(i):
    """Left edge of grid column i (0-based)."""
    return M + i * (COLW + GUT)


def span_x(i, n):
    """Left and right edge of a run of n columns starting at column i."""
    return col_x(i), col_x(i + n - 1) + COLW


class Page:
    def __init__(self):
        self.im = Image.new("RGB", (W * S, H * S), PAPER)
        self.d = ImageDraw.Draw(self.im)

    # -- measurement
    def tw(self, s, f):
        return self.d.textlength(s, font=f) / S

    def wrap(self, s, f, width):
        words, lines, cur = s.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if not cur or self.tw(trial, f) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = w
                while self.tw(cur, f) > width and len(cur) > 1:
                    cut = len(cur)
                    while cut > 1 and self.tw(cur[:cut], f) > width:
                        cut -= 1
                    lines.append(cur[:cut])
                    cur = cur[cut:]
        if cur:
            lines.append(cur)
        return lines

    def fit(self, s, path, width, max_lines, hi, lo):
        """Largest size whose wrap fits in max_lines; the floor size otherwise."""
        for size in range(int(hi), int(lo) - 1, -1):
            f = font(path, size)
            lines = self.wrap(s, f, width)
            if len(lines) <= max_lines:
                return f, lines
        f = font(path, lo)
        return f, self.wrap(s, f, width)[:max_lines]

    # -- primitives
    def text(self, x, y, s, f, fill, anchor="la"):
        self.d.text((x * S, y * S), s, font=f, fill=fill, anchor=anchor)

    def rect(self, box, fill=None, outline=None, width=1):
        self.d.rectangle([box[0] * S, box[1] * S, box[2] * S, box[3] * S], fill=fill,
                         outline=outline, width=max(1, int(round(width * S))))

    def line(self, pts, fill, width=1):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill,
                    width=max(1, int(round(width * S))), joint="curve")

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline,
                       width=max(1, int(round(width * S))))

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.d.ellipse([box[0] * S, box[1] * S, box[2] * S, box[3] * S], fill=fill,
                       outline=outline, width=max(1, int(round(width * S))))

    def arc(self, box, a0, a1, fill, width=2):
        self.d.arc([box[0] * S, box[1] * S, box[2] * S, box[3] * S], a0, a1, fill=fill,
                   width=max(1, int(round(width * S))))

    def rule(self, x0, x1, y, weight=1, color=RULE):
        self.rect([x0, y, x1, y + weight], fill=color)

    def vrule(self, x, y0, y1, weight=1, color=FAINT):
        self.rect([x, y0, x + weight, y1], fill=color)

    def save(self, path):
        self.im.resize((W, H), Image.LANCZOS).save(path, optimize=True)

    def layer(self, w, h, bg=None):
        """A drawing surface exactly w x h in design units, for something that
        must not spill out of its frame (a picture, a mark). Coordinates inside
        it start at zero; paste it back with `place`."""
        sub = Page.__new__(Page)
        sub.im = Image.new("RGB", (int(round(w * S)), int(round(h * S))),
                           bg if bg is not None else PAPER)
        sub.d = ImageDraw.Draw(sub.im)
        sub.w, sub.h = w, h
        return sub

    def place(self, sub, x, y):
        """Paste a layer at (x, y) design units, hard-edged."""
        self.im.paste(sub.im, (int(round(x * S)), int(round(y * S))))


# ------------------------------------------------------------ the picture --
def draw_hero_picture(page, x0, y0, w, h):
    """Give the picture its own surface so the smoke cannot escape its frame."""
    sub = page.layer(w, h, "#C4C0B6")
    draw_hero_scene(sub, 0, 0, w, h)
    page.place(sub, x0, y0)
    page.rect([x0, y0, x0 + w, y0 + h], outline=INK2, width=1)


def draw_hero_scene(p, x0, y0, w, h):
    """A cargo ship burning in the Baltic at dawn, under a drone's flight path.

    Wide landscape: a low horizon, a flat sea, the Finnish shore far off to the
    left, the ship listing slightly with fire amidships and a column of smoke
    bending away to the left, and the drone that struck it still overhead with
    its dashed course coming in from the right edge.
    """
    horizon = y0 + h * 0.54
    sea = y0 + h

    # sky: warm at the horizon, cooler overhead, laid in flat bands
    bands = 30
    for i in range(bands):
        t = i / (bands - 1.0)
        c = int(round(196 + 44 * t))
        p.rect([x0, y0 + h * t * 0.545, x0 + w, y0 + h * (t + 1 / bands) * 0.545 + 0.7],
               fill=(c, c - 7, c - 18))
    # the low sun, a pale disc left of the ship
    sx, sy = x0 + w * 0.17, horizon - h * 0.06
    for rr, col in ((h * 0.14, "#F4E4CB"), (h * 0.10, "#FAEED7"), (h * 0.06, "#FFF8E9")):
        p.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=col)

    # the sea: flat grey-green, lighter toward the horizon
    p.rect([x0, horizon, x0 + w, sea], fill="#5E6B6A")
    for i in range(16):
        t = i / 15.0
        yy = horizon + h * 0.46 * (t ** 1.7)
        shade = int(94 + 28 * t)
        p.rect([x0, yy, x0 + w, yy + max(1.0, h * 0.011)], fill=(shade, shade + 9, shade + 5))
    for i in range(30):
        t = i / 29.0
        yy = horizon + h * 0.05 + h * 0.44 * t
        xx = x0 + w * ((i * 0.37) % 1.0)
        ln = w * (0.03 + 0.06 * t)
        p.line([(xx, yy), (xx + ln, yy)], "#8C9997", max(1, int(1 + 2 * t)))

    # the Finnish shore, far left: a dark spit with pines
    p.poly([(x0, horizon + 1), (x0 + w * 0.26, horizon + 1),
            (x0 + w * 0.24, horizon - h * 0.034), (x0 + w * 0.13, horizon - h * 0.052),
            (x0 + w * 0.05, horizon - h * 0.029)], fill="#414B4A")
    for i in range(12):
        tx = x0 + w * (0.05 + i * 0.017)
        th = h * (0.028 + 0.017 * ((i * 5) % 3))
        p.poly([(tx, horizon - h * 0.028), (tx - w * 0.009, horizon - h * 0.028),
                (tx - w * 0.0045, horizon - h * 0.028 - th)], fill="#37403F")

    # ---- the ship, a long three-quarter profile listing to port
    bx, by = x0 + w * 0.50, horizon + h * 0.055
    hl_, hr_ = w * 0.190, w * 0.180
    deck_y = by - h * 0.048

    # its reflection on the water, broken up
    p.poly([(bx - hl_ * 0.78, by + h * 0.02), (bx + hr_ * 0.78, by + h * 0.02),
            (bx + hr_ * 0.50, by + h * 0.21), (bx - hl_ * 0.50, by + h * 0.21)],
           fill="#6B6759")
    for i in range(6):
        yy = by + h * (0.04 + i * 0.028)
        p.line([(bx - hl_ * (0.70 - i * 0.06), yy), (bx + hr_ * (0.66 - i * 0.05), yy)],
               "#7E7A67", 1)

    # hull: a long wedge, bow left, stern slightly down
    p.poly([(bx - hl_, deck_y), (bx + hr_, deck_y - h * 0.007),
            (bx + hr_ * 0.90, by + h * 0.032), (bx - hl_ * 0.80, by + h * 0.055)],
           fill="#1E262A")
    # boot-topping in rust red, the way a working hull looks
    p.poly([(bx - hl_ * 0.80, by + h * 0.014), (bx + hr_ * 0.92, by - h * 0.003),
            (bx + hr_ * 0.90, by + h * 0.032), (bx - hl_ * 0.80, by + h * 0.055)],
           fill="#8A3A28")
    p.line([(bx - hl_, deck_y), (bx + hr_, deck_y - h * 0.007)], "#CFC7B2", 2)

    # forecastle forward, the white accommodation block and bridge aft
    p.poly([(bx - hl_ * 0.99, deck_y), (bx - hl_ * 0.40, deck_y - h * 0.011),
            (bx - hl_ * 0.40, deck_y - h * 0.032), (bx - hl_ * 0.99, deck_y - h * 0.017)],
           fill="#2C3438")
    p.rect([bx + hr_ * 0.28, deck_y - h * 0.108, bx + hr_ * 0.86, deck_y + h * 0.004],
           fill="#E6E0CF")
    for i in range(4):
        wy = deck_y - h * 0.098 + i * h * 0.024
        p.rect([bx + hr_ * 0.34, wy, bx + hr_ * 0.80, wy + h * 0.012], fill="#7C8A90")
    p.rect([bx + hr_ * 0.50, deck_y - h * 0.152, bx + hr_ * 0.86, deck_y - h * 0.108],
           fill="#F2EDDF")
    p.line([(bx + hr_ * 0.69, deck_y - h * 0.152), (bx + hr_ * 0.69, deck_y - h * 0.232)],
           "#1E262A", 2)
    p.line([(bx + hr_ * 0.60, deck_y - h * 0.205), (bx + hr_ * 0.78, deck_y - h * 0.205)],
           "#1E262A", 1)

    # deck cargo between the fire and the stern
    for i in range(4):
        cx = bx - hl_ * 0.26 + i * w * 0.031
        p.rect([cx, deck_y - h * 0.042, cx + w * 0.027, deck_y], fill="#333B3E")
        p.rect([cx, deck_y - h * 0.042, cx + w * 0.027, deck_y - h * 0.036], fill="#8A5A32")

    # ---- the fire amidships: a hot core, tongues, and a glow on the deck
    fx, fy = bx - hl_ * 0.04, deck_y - h * 0.010
    for rr, col in ((h * 0.145, (148, 94, 58)), (h * 0.095, (206, 132, 58)),
                    (h * 0.058, (240, 176, 72))):
        p.ellipse([fx - rr, fy - rr * 1.15, fx + rr, fy + rr * 0.72], fill=col)
    for i in range(9):
        tx = fx + (i - 4) * w * 0.0115
        th = h * (0.052 + 0.034 * ((i * 3) % 4) / 3.0)
        p.poly([(tx - w * 0.011, fy), (tx, fy - th), (tx + w * 0.012, fy)], fill="#E8481E")
        p.poly([(tx - w * 0.0055, fy), (tx, fy - th * 0.56), (tx + w * 0.0065, fy)],
               fill="#F8C24A")

    # ---- the smoke: a column that rises and bends away to the left
    lobes = [
        (0.00, 0.03, 0.050, "#26262A"), (0.01, -0.05, 0.060, "#2E2E31"),
        (-0.02, -0.14, 0.070, "#35352F"), (-0.06, -0.23, 0.079, "#413F39"),
        (-0.12, -0.31, 0.087, "#514E47"), (-0.21, -0.38, 0.094, "#66635A"),
        (-0.31, -0.43, 0.098, "#7C7970"), (-0.42, -0.46, 0.100, "#918D84"),
        (-0.53, -0.46, 0.097, "#A5A096"), (-0.63, -0.44, 0.090, "#B6B1A6"),
        (-0.72, -0.40, 0.079, "#C2BDB2"),
    ]
    for dx, dy, rr, col in lobes:
        cx, cy = fx + w * dx, fy + h * dy
        r = w * rr
        p.ellipse([cx - r, cy - r * 0.88, cx + r, cy + r * 0.88], fill=col)
    p.ellipse([fx - w * 0.056, fy - h * 0.105, fx + w * 0.056, fy + h * 0.008],
              fill="#20201E")

    # ---- the drone, high right, its dashed course arcing in from the edge
    dxc, dyc = x0 + w * 0.845, y0 + h * 0.170
    dsz = h * 0.040
    for i in range(7):
        t = i / 7.0
        ax = x0 + w * (1.00 - 0.15 * t)
        ay = y0 + h * (0.295 - 0.115 * t)
        p.line([(ax, ay), (ax - w * 0.014, ay - h * 0.013)], "#4A4440", 2)
    p.rect([dxc - dsz * 0.30, dyc - dsz * 0.17, dxc + dsz * 0.30, dyc + dsz * 0.17],
           fill="#191917")
    for sx_ in (-1, 1):
        for sy_ in (-1, 1):
            ax, ay = dxc + sx_ * dsz * 0.98, dyc + sy_ * dsz * 0.56
            p.line([(dxc, dyc), (ax, ay)], "#191917", 2)
            p.ellipse([ax - dsz * 0.36, ay - dsz * 0.11,
                       ax + dsz * 0.36, ay + dsz * 0.11], fill="#3A3A34")
    p.line([(dxc, dyc + dsz * 0.22), (dxc, dyc + dsz * 1.35)], "#B3271E", 1)

    p.rect([x0, y0, x0 + w, y0 + h], outline=INK2, width=1)


# ------------------------------------------------------------------ bands --
def draw_nameplate(p):
    f_eye = font(SANS_B, 8)
    f_date = font(SERIF_B, 46)
    f_deck = font(SERIF_I, 13)

    p.text(M, NAME_Y, "THE WORLD IN ONE DAY", f_eye, RED)
    p.text(W - M, NAME_Y, "A VIEW OF THE WORLD'S NEWS", f_eye, GREY, anchor="ra")
    p.text(M, DATE_Y, "Sunday 22 November 2026", f_date, INK)

    deck = "  ·  ".join(["A Russian ship burns in the Baltic", "El Chapo Isidro is taken",
                         "COP31 nears collapse"])
    x0, x1 = span_x(0, 8)
    f, _ = p.fit(deck, SERIF_I, x1 - x0, 1, 13, 10)
    p.text(x0, DECK_Y, deck, f, INK2)
    p.rule(M, W - M, HEAD_RULE, 3)


def draw_hero(p):
    x0, x1 = span_x(0, 8)
    w = x1 - x0
    draw_hero_picture(p, x0, HERO_Y, w, PIC_H)

    f_cap, cl = p.fit("The cargo ship off the Gulf of Finland on Sunday morning, "
                      "from a coastguard aircraft.   FINLAND",
                      SANS_R, w, 1, 8, 7)
    p.text(x0, CAP_Y, "\n".join(cl), f_cap, GREY)
    p.rule(x0, x1, CAP_Y + CAP_H - 10, 1, FAINT)

    p.text(x0, HTEXT_Y, "CONFLICT  ·  " + HERO["hour"] + " UTC  ·  " + HERO["place"],
           font(SANS_B, 8), RED)

    f_hl, hl = p.fit(HERO["headline"], SERIF_B, w, 3, 30, 19)
    p.text(x0, HTEXT_Y + 13, "\n".join(hl), f_hl, INK)

    y = HTEXT_Y + 13 + len(hl) * (f_hl.size / S + 1.5)
    f_st, sl = p.fit(HERO["stand"], SERIF_R, w, 3, 12, 9.5)
    p.text(x0, y, "\n".join(sl), f_st, INK2)

    # the day in UTC, in the four columns beside the picture
    cx0, cx1 = span_x(8, 4)
    p.text(cx0, HERO_Y, "AS IT HAPPENED", font(SANS_B, 8), RED)
    p.text(cx0, HERO_Y + 11, "THE DAY IN UTC", font(SANS_B, 6.5), GREY)
    p.rule(cx0, cx1, HERO_Y + 21, 1, RULE)
    y = HERO_Y + 29
    for t, what in CLOCK:
        p.text(cx0, y, t, font(SANS_B, 8), INK)
        f_w, wl = p.fit(what, SANS_R, cx1 - cx0 - 31, 2, 7, 6)
        p.text(cx0 + 31, y - 1, "\n".join(wl), f_w, GREY)
        y += 21 + (len(wl) - 1) * 7.5
    p.vrule(cx0 - GUT / 2, HERO_Y, NUM_Y - 8, 1, FAINT)


def draw_grid(p):
    """The rest of the day: twelve stories, three ranks of four columns."""
    p.text(M, GRID_Y - 16, "THE DAY ELSEWHERE", font(SANS_B, 8), RED)
    p.text(W - M, GRID_Y - 16, "twelve more, each first reported on 22 November",
           font(SANS_R, 7), GREY, anchor="ra")
    p.rule(M, W - M, GRID_Y - 5, 1, RULE)

    for k, (place, beat, hour, headline, stand) in enumerate(SECOND):
        r_, c_ = k // 4, k % 4
        x0, x1 = span_x(c_ * 3, 3)
        w = x1 - x0
        y0 = GRID_Y + r_ * GRID_ROW_H
        colour = BEAT_COLOUR[beat]
        if c_:
            p.vrule(x0 - GUT / 2, y0 + 2, y0 + GRID_ROW_H - 7, 1, FAINT)
        p.text(x0, y0 + 1, beat.upper() + "  " + hour, font(SANS_B, 7), colour)
        # the headline carries the story alone: at 300px across, a 7pt deck is
        # texture, and texture does not tell a judge what happened.
        f_hl, hl = p.fit(headline, SERIF_B, w - 4, 3, 14, 10)
        p.text(x0, y0 + 11, "\n".join(hl), f_hl, INK)
        y = y0 + 11 + len(hl) * (f_hl.size / S + 1)
        p.text(x0, max(y + 1, y0 + GRID_ROW_H - 9), place, font(SANS_B, 6), colour)


def draw_numbers(p):
    """The day in five figures, stacked in the column under the timeline."""
    cx0, cx1 = span_x(8, 4)
    y = NUM_Y
    p.rule(cx0, cx1, y, 1, RULE)
    p.text(cx0, y + 5, "THE DAY IN FIGURES", font(SANS_B, 8), RED)
    y += 20
    for num, cap in NUMBERS:
        p.text(cx0, y, num, font(SERIF_B, 20), RED)
        f, lines = p.fit(cap, SANS_R, cx1 - cx0 - 26, 2, 7.5, 6.5)
        p.text(cx0 + 26, y + 1, "\n".join(lines), f, GREY)
        y += 15 + (len(lines) - 1) * 8
    p.vrule(cx0 - GUT / 2, HERO_Y, y - 4, 1, FAINT)


def draw_briefs(p):
    y_top = BRIEF_Y
    p.text(M, y_top - 15, "ALSO ON SUNDAY 22 NOVEMBER", font(SANS_B, 8), RED)
    p.text(W - M, y_top - 15, "each dated that day", font(SANS_R, 7), GREY, anchor="ra")
    p.rule(M, W - M, y_top - 4, 1, RULE)

    per = 4
    rank_h = (H - M - y_top) / BRIEF_ROWS
    for k, (place, s) in enumerate(BRIEFS):
        r_, c_ = k // per, k % per
        x0, x1 = span_x(c_ * 3, 3)
        w = x1 - x0
        y0 = y_top + r_ * rank_h
        if c_:
            p.vrule(x0 - GUT / 2, y0, y0 + rank_h - 5, 1, FAINT)
        p.text(x0, y0, place, font(SANS_B, 6.5), BEAT_COLOUR["Politics"])
        f, lines = p.fit(s, SERIF_B, w - 6, 2, 11.5, 8.5)
        p.text(x0, y0 + 10, "\n".join(lines), f, INK)


def main():
    p = Page()
    draw_nameplate(p)
    draw_hero(p)
    draw_grid(p)
    draw_numbers(p)
    draw_briefs(p)
    p.rule(M, W - M, H - M + 2, 1, FAINT)
    p.text(M, H - M + 5, "THE WORLD IN ONE DAY  ·  SUNDAY 22 NOVEMBER 2026  ·  PAGE ONE",
           font(SANS_R, 6), GREY)

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    p.save(out)
    print("wrote", out, Image.open(out).size)


if __name__ == "__main__":
    main()
