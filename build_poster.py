#!/usr/bin/env python3
"""Compose the news-image-20261122 entry poster (1024x1024 PNG).

Layout: a full-width hero illustration on top, a crimson masthead strip
under it, one full-width lead story, then the remaining four stories in
a 2x2 grid of cards, and a sources footer. All text is drawn here with
DejaVu fonts so every label is crisp and legible.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
HERO = os.path.join(HERE, "hero.png")
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
CRIMSON = (122, 31, 43)
OCHRE = (232, 164, 32)
PAPER = (247, 243, 236)
CARD = (255, 255, 255)
CARD_LINE = (222, 216, 206)
INK = (24, 30, 38)
GREY = (92, 102, 116)
RED = (178, 44, 36)
BLUE = (31, 90, 150)
TEAL = (13, 110, 105)
BROWN = (176, 118, 8)
PURPLE = (88, 70, 140)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_DATE = font("DejaVuSans-Bold.ttf", 54)
F_KICK = font("DejaVuSans-Bold.ttf", 18)
F_LEAD_HEAD = font("DejaVuSans-Bold.ttf", 32)
F_LEAD_BODY = font("DejaVuSans.ttf", 20)
F_HEAD = font("DejaVuSans-Bold.ttf", 26)
F_BODY = font("DejaVuSans.ttf", 18)
F_FOOT = font("DejaVuSans.ttf", 17)
F_TAG = font("DejaVuSans-Bold.ttf", 15)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines fitting max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# Five verified 22 November 2026 stories (kicker, headline, summary, accent).
LEAD = (
    "MIDDLE EAST ESCALATES",
    "Iran hits tankers, Bahrain and Riyadh in one night",
    "3 tankers struck near Hormuz; Bahrain site ablaze, no injuries; 3 Houthi missiles downed over Riyadh",
    RED,
)
CARDS = [
    (
        "EL CHAPO ISIDRO CAUGHT",
        "FBI most-wanted cartel boss seized",
        "11 killed in Sinaloa battles \u2014 4 soldiers, 7 gunmen; fans flee a baseball game",
        BLUE,
    ),
    (
        "FUNERAL BOAT SINKS",
        "24 dead as boat capsizes in Nigeria",
        "Mourners bound for a burial in Bayelsa; 24 rescued, mechanical failure blamed",
        TEAL,
    ),
    (
        "TOXIC ALCOHOL",
        "11 dead from toxic alcohol in Manipur",
        "Tainted liquor hospitalises 180+; chief minister confirms the toll",
        BROWN,
    ),
    (
        "TRUMP'S RATE CAP",
        "President vows 10% credit-card cap",
        "Will work with Democrats; revives a stalled campaign promise",
        PURPLE,
    ),
]

poster = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(poster)

# --- Hero illustration, cropped to a wide band on top. ---
hero = Image.open(HERO).convert("RGB")
crop_h = int(hero.width * 320 / 1024)
top = max(0, (hero.height - crop_h) // 2 - 30)
hero = hero.crop((0, top, hero.width, top + crop_h))
hero = hero.resize((W, 320), Image.LANCZOS)
poster.paste(hero, (0, 0))

# --- Masthead strip under the hero. ---
d.rectangle([0, 320, W, 420], fill=CRIMSON)
d.text((40, 334), "THE WORLD IN ONE IMAGE", font=F_KICK, fill=OCHRE)
d.text((40, 358), "22 NOVEMBER 2026", font=F_DATE, fill=(255, 255, 255))
d.text((W - 40, 336), "SUNDAY", font=F_KICK, fill=(255, 255, 255), anchor="ra")
d.text((W - 40, 362), "WORLD NEWS", font=F_KICK, fill=(255, 255, 255), anchor="ra")
d.rectangle([0, 420, W, 424], fill=OCHRE)

# --- Lead story, full width. ---
kicker, head, body, accent = LEAD
d.rounded_rectangle([40, 442, 168, 470], radius=6, fill=accent)
d.text((104, 456), "LEAD STORY", font=F_TAG, fill=(255, 255, 255), anchor="mm")
d.text((188, 438), kicker, font=F_KICK, fill=accent)
d.text((40, 478), head, font=F_LEAD_HEAD, fill=INK)
lead_lines = wrap(d, body, F_LEAD_BODY, W - 80)
ly = 516
for line in lead_lines[:2]:
    d.text((40, ly), line, font=F_LEAD_BODY, fill=GREY)
    ly += 26
d.line([40, 566, W - 40, 566], fill=CARD_LINE, width=2)

# --- Four stories in a 2x2 grid of cards. ---
GRID_TOP = 580
GRID_LEFT = 40
CARD_W = 464
CARD_H = 182
GAP_X = 16
GAP_Y = 14
for i, (kicker, head, body, accent) in enumerate(CARDS):
    col, row = i % 2, i // 2
    x0 = GRID_LEFT + col * (CARD_W + GAP_X)
    y0 = GRID_TOP + row * (CARD_H + GAP_Y)
    x1, y1 = x0 + CARD_W, y0 + CARD_H
    d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=CARD, outline=CARD_LINE, width=2)
    d.rectangle([x0 + 10, y0, x1 - 10, y0 + 6], fill=accent)
    tx = x0 + 20
    d.text((tx, y0 + 22), kicker, font=F_KICK, fill=accent)
    head_lines = wrap(d, head, F_HEAD, CARD_W - 40)
    hy = y0 + 50
    for line in head_lines[:2]:
        d.text((tx, hy), line, font=F_HEAD, fill=INK)
        hy += 32
    body_lines = wrap(d, body, F_BODY, CARD_W - 40)
    by = hy + 6
    for line in body_lines[:2]:
        d.text((tx, by), line, font=F_BODY, fill=GREY)
        by += 24

# --- Footer: sources. ---
d.text(
    (40, 986),
    "Sources: Gulf News, CNN, AP, Al Jazeera, Economic Times  |  22 Nov 2026",
    font=F_FOOT,
    fill=GREY,
)

poster.save(OUT, "PNG", optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes", poster.size)
