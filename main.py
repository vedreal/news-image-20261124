# news-image-20261124: a one-day newspaper front page for Tuesday, 24 November 2026.
# The program draws the whole page itself (no network, no downloaded assets) and
# writes it to /output/entry.png. Deterministic: same bytes on every run.
# Part 1: 5x7 bitmap font, canvas, drawing primitives and the PNG encoder.

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (251, 247, 236)
INK = (17, 17, 17)
RED = (163, 22, 33)
GREEN = (30, 122, 52)
GREY = (112, 108, 100)
LIGHT = (233, 227, 211)
WHITE = (255, 255, 255)

# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    'A': (".###.", "#...#", "#####", "#...#", "#...#"),
    'B': ("####.", "#...#", "####.", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "####.", "#....", "#####"),
    'F': ("#####", "#....", "####.", "#....", "#...."),
    'G': (".####", "#....", "#.###", "#...#", ".###."),
    'H': ("#...#", "#...#", "#####", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", ".##.."),
    'K': ("#...#", "#..#.", "##...", "#.#..", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "####.", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#.#.#", ".##.#"),
    'R': ("####.", "#...#", "####.", "#.#..", "#...#"),
    'S': (".####", "#....", ".###.", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'Y': ("#...#", ".#.#.", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", "#####"),
    'a': (".....", ".###.", "....#", ".####", ".####"),
    'b': ("#....", "####.", "#...#", "#...#", "####."),
    'c': (".....", ".####", "#....", "#....", ".####"),
    'd': ("....#", ".####", "#...#", "#...#", ".####"),
    'e': (".....", ".###.", "#####", "#....", ".###."),
    'f': ("..##.", ".#...", "####.", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", ".####", ".###."),
    'h': ("#....", "####.", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "##..."),
    'k': ("#....", "#..#.", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", "##.#.", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", "####.", "#...#", "#...#", "#...#"),
    'o': (".....", ".###.", "#...#", "#...#", ".###."),
    'p': (".....", "####.", "#...#", "####.", "#...."),
    'q': (".....", ".####", "#...#", ".####", "....#"),
    'r': (".....", "#.##.", "##..#", "#....", "#...."),
    's': (".....", ".####", ".###.", "....#", "####."),
    't': (".#...", "####.", ".#...", ".#...", "..##."),
    'u': (".....", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", "#...#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", "#...#", ".#.#.", ".#.#.", "#...#"),
    'y': (".....", "#...#", "#...#", ".####", ".###."),
    'z': (".....", "#####", "...#.", "..#..", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "...#.", "..#..", "#####"),
    '3': ("####.", "....#", ".###.", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#####", "...#."),
    '5': ("#####", "#....", "####.", "....#", ".###."),
    '6': (".###.", "#....", "####.", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#.."),
    '8': (".###.", "#...#", ".###.", "#...#", ".###."),
    '9': (".###.", "#...#", ".####", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".##.."),
    ',': (".....", ".....", ".....", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", "....."),
    ':': (".....", ".##..", ".....", ".##..", "....."),
    ';': (".....", ".##..", ".....", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "...#.", ".....", "..#.."),
    '-': (".....", ".....", ".###.", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", "..#.."),
    ')': (".#...", "..#..", "...#.", "...#.", "..#.."),
    '/': ("....#", "...#.", "..#..", ".#...", "#...."),
    '$': ("..#..", ".####", "#.#..", ".###.", "####."),
    '%': ("#...#", "#..#.", "...#.", ".#...", "#..#."),
    '&': (".###.", "#...#", "#.#..", ".#...", ".##.#"),
    '+': (".....", "..#..", "#####", "..#..", "....."),
    '=': (".....", "#####", ".....", "#####", "....."),
    '*': (".....", ".#.#.", "..#..", ".#.#.", "....."),
    '#': ("#.#.#", "#.#.#", "#####", "#.#.#", "#.#.#"),
    '[': (".###.", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", ".###."),
    '•': (".....", "..#..", ".###.", ".###.", "..#.."),
}


def _glyph(ch):
    # Normalise curly quotes and dashes to the ASCII glyphs we carry.
    if ch in "\u2019\u2018":
        ch = "'"
    if ch in "\u2013\u2014":
        ch = "-"
    if ch == "\u00b7":
        ch = "•"
    return FONT.get(ch, FONT["?"])


class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3] = bg[0]
            self.px[i * 3 + 1] = bg[1]
            self.px[i * 3 + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, thick=1):
        self.rect(x, y, w, thick, c)

    def vline(self, x, y, h, c, thick=1):
        self.rect(x, y, thick, h, c)

    def border(self, x, y, w, h, c, thick=1):
        self.hline(x, y, w, c, thick)
        self.hline(x, y + h - thick, w, c, thick)
        self.vline(x, y, h, c, thick)
        self.vline(x + w - thick, y, h, c, thick)

    def line(self, x0, y0, x1, y1, c, thick=1):
        # Bresenham's line algorithm.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            rows = _glyph(ch)
            for ry in range(5):
                row = rows[ry]
                for rx in range(5):
                    if row[rx] == '#':
                        self.rect(cx + rx * scale, y + ry * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centred(self, cx, y, s, scale, c):
        w = self.text_w(s, scale)
        return self.text(cx - w // 2, y, s, scale, c)

    def wrap(self, s, max_w, scale):
        # Greedy word wrap; returns a list of lines that fit max_w pixels.
        words = s.split(" ")
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, max_w, scale, c, leading=None):
        if leading is None:
            leading = 7 * scale + 4
        for ln in self.wrap(s, max_w, scale):
            self.text(x, y, ln, scale, c)
            y += leading
        return y


def _chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png(canvas):
    raw = bytearray()
    row_len = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * row_len:(y + 1) * row_len]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + _chunk(b"IEND", b"")
    )
    return png

# ---- part 2: layout, stories and main ----

def build():
    c = Canvas()
    c.border(8, 8, 1008, 1008, INK, 3)

    # Masthead.
    c.text_centred(512, 28, "THE WORLD TODAY", 7, INK)
    c.hline(28, 74, 968, INK, 4)
    c.hline(28, 82, 968, INK, 1)
    c.text_centred(512, 92, "TUESDAY, 24 NOVEMBER 2026", 4, RED)
    c.text_centred(512, 120, "THE DAY'S WORLD NEWS IN ONE PAGE", 2, GREY)
    c.hline(28, 140, 968, INK, 1)

    # Main story: Nvidia.
    c.text(28, 150, "MARKETS • TECHNOLOGY", 2, RED)
    c.text(28, 166, "Huang back at Nvidia", 5, INK)
    c.text(28, 208, "as shares soar 31%", 5, INK)
    c.para(
        28,
        256,
        "Chipmaker adds about $950bn in value - the biggest one-day gain in "
        "history - as Wall Street's AI rally roars back. The Nasdaq jumps "
        "6.5%, the S&P 500 4.7% and the Dow 1,448 points.",
        968,
        2,
        INK,
    )

    # Chart panel: the rally, as a rising line.
    c.rect(28, 322, 968, 178, WHITE)
    c.border(28, 322, 968, 178, INK, 1)
    for gy in (362, 402, 442, 482):
        c.hline(40, gy, 944, LIGHT, 1)
    c.text(44, 334, "NASDAQ +6.5%", 2, INK)
    c.text(44, 352, "S&P 500 +4.7%", 2, GREY)
    pts = [(60, 470), (200, 456), (350, 461), (500, 441),
           (650, 431), (800, 401), (940, 351)]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], GREEN, 4)
    c.rect(934, 345, 12, 12, GREEN)
    c.text(800, 312, "NVDA +31%", 3, GREEN)
    c.text(44, 478, "Wall Street, Monday: the AI rally roars back", 2, GREY)

    # Divider above the supporting stories.
    c.hline(28, 512, 968, INK, 3)
    c.vline(512, 524, 420, GREY, 1)

    stories_left = [
        ("EUROPE",
         "EU targets banks, crypto and Russian flag",
         "The 22nd package bars Russian teams from competing under their "
         "flag at EU sports events. All 27 must agree."),
        ("UKRAINE",
         "Abu Dhabi talks end with no breakthrough",
         "US envoys Witkoff and Kushner head to Moscow after two days of "
         "talks; gaps are narrowing, Washington says."),
        ("ASIA",
         "Seoul names first woman spy chief in reshuffle",
         "Lee picks Kang Kum-sil to lead intelligence, Lim Woong-soon as "
         "foreign minister, Hong Ik-pyo for unification."),
    ]
    stories_right = [
        ("PORTUGAL",
         "Portugal votes on budget today as unions rally",
         "Final vote on the 2027 budget in Lisbon as the CGTP rallies "
         "outside parliament over wages and prices."),
        ("INDIA-NEPAL",
         "First Ayodhya-Janakpur train reaches Nepal today",
         "The Saryu-Kamala Express inaugural run ends in Janakpur this "
         "morning; weekly service starts 28 November."),
    ]

    def story(x, y, kicker, headline, deck):
        c.text(x, y, kicker, 2, RED)
        y += 16
        for ln in c.wrap(headline, 472, 3):
            c.text(x, y, ln, 3, INK)
            y += 26
        y += 4
        c.para(x, y, deck, 472, 2, INK)

    y = 524
    for kicker, headline, deck in stories_left:
        story(28, y, kicker, headline, deck)
        y += 140
    y = 524
    for kicker, headline, deck in stories_right:
        story(524, y, kicker, headline, deck)
        y += 140

    # Markets box in the right column's third slot.
    c.rect(524, 804, 472, 128, WHITE)
    c.border(524, 804, 472, 128, INK, 1)
    c.text(540, 816, "MARKETS", 2, RED)
    c.text(540, 840, "NASDAQ +6.5%", 2, INK)
    c.text(540, 862, "S&P 500 +4.7%", 2, INK)
    c.text(540, 884, "DOW +3.0% (+1,448)", 2, INK)
    c.text(540, 906, "NVIDIA +31%", 2, GREEN)

    # Footer.
    c.hline(28, 966, 968, INK, 1)
    c.text_centred(512, 974, "THE WORLD TODAY - TUESDAY, 24 NOVEMBER 2026", 2, GREY)
    return encode_png(c)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = build()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
