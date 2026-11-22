#!/usr/bin/env python3
"""Compose the 22 November 2026 world-news poster (1024 x 1024).

Reads hero.png (a cartoon flat-vector Strait of Hormuz at dusk, two
tankers) and lays out a newspaper-style front page in a bright cartoon
look: a hero illustration band, a vivid red masthead, one full-width
lead story, a 2x2 grid of story cards, and a sources footer.
Writes entry.png to MAKEFUN_OUTPUT_DIR when that environment variable
is set (the grader mounts the repo read-only and names a writable
output directory there), otherwise next to this script.

The build is deterministic: fixed fonts, fixed geometry, no timestamps
and no randomness, so repeated runs produce byte-identical PNG output.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
HERO_PATH = HERE / "hero.png"
# The grader mounts the repository read-only and names a writable output
# directory in MAKEFUN_OUTPUT_DIR; honour it when set so the poster can
# be written there, and default to the script's own directory for local
# runs (which still produce entry.png in the repo, exactly as before).
_out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
OUT_PATH = (Path(_out_dir) if _out_dir else HERE) / "entry.png"

W, H = 1024, 1024

# --- palette (cartoon: bright, saturated, playful) ----------------------
CREAM = (255, 248, 233)        # page background, warm bright cream
CRIMSON = (214, 48, 63)        # masthead band + lead badge, vivid cherry red
GOLD = (255, 176, 32)          # masthead eyebrow + rule, sunny amber
INK = (26, 26, 26)             # headlines
GREY = (92, 92, 92)            # standfirsts / card decks
FOOT_GREY = (112, 112, 112)    # footer
CARD_EDGE = (233, 221, 196)    # card outline
RULE = (216, 200, 168)         # divider under the lead
WHITE = (255, 255, 255)

ACCENT_BLUE = (24, 120, 220)
ACCENT_TEAL = (0, 168, 150)
ACCENT_OCHRE = (245, 158, 11)
ACCENT_PURPLE = (139, 92, 246)

# --- fonts ---------------------------------------------------------------
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SANS_B = "DejaVuSans-Bold.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


# --- layout --------------------------------------------------------------
MARGIN = 40
RIGHT = W - MARGIN                 # 984, right edge of the text column
CONTENT_W = W - 2 * MARGIN         # 944

HERO_H = 292
MAST_TOP = HERO_H
MAST_H = 104
MAST_BOT = MAST_TOP + MAST_H       # 396

LEAD_BADGE_Y = 414
LEAD_HEAD_Y = 452
LEAD_SUB_Y = 508
DIVIDER_Y = 578

CARD_W = 462
CARD_H = 180
CARD_GAP_X = 20
CARD_GAP_Y = 16
CARD_TOP1 = 596
CARD_TOP2 = CARD_TOP1 + CARD_H + CARD_GAP_Y   # 792
CARD_X1 = MARGIN
CARD_X2 = MARGIN + CARD_W + CARD_GAP_X        # 522
CARD_R = 14
CARD_BAR_H = 9
CARD_PAD = 20

FOOT_Y = 988


# --- text helpers --------------------------------------------------------
def wrap(draw: ImageDraw.ImageDraw, text: str,
         font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Greedy word wrap; returns lines that fit within max_w pixels."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
               font: ImageFont.FreeTypeFont, fill: tuple[int, int, int],
               max_w: int, leading: int) -> int:
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(draw, text, font, max_w)
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=font, fill=fill)
    return y + len(lines) * leading


# --- card ----------------------------------------------------------------
def make_card_base(w: int, h: int, accent: tuple[int, int, int]) -> Image.Image:
    """White rounded card with a coloured bar across the top.

    Drawn on its own RGBA layer and clipped to the rounded outline so the
    bar's square corners never poke outside the card's rounded corners.
    """
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=CARD_R,
                        fill=WHITE + (255,))
    d.rectangle([0, 0, w - 1, CARD_BAR_H], fill=accent + (255,))
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, w - 1, h - 1], radius=CARD_R, fill=255)
    alpha = Image.composite(layer.getchannel("A"),
                            Image.new("L", (w, h), 0), mask)
    layer.putalpha(alpha)
    return layer


def draw_card(img: Image.Image, draw: ImageDraw.ImageDraw,
              x: int, y: int, accent: tuple[int, int, int],
              kicker: str, headline: str, deck: str) -> None:
    """Paste one story card and lay out its kicker, headline and deck."""
    base = make_card_base(CARD_W, CARD_H, accent)
    img.paste(base, (x, y), base)
    draw.rounded_rectangle([x, y, x + CARD_W - 1, y + CARD_H - 1],
                           radius=CARD_R, outline=CARD_EDGE, width=1)
    tx = x + CARD_PAD
    inner_w = CARD_W - 2 * CARD_PAD
    f_kick = load_font(SANS_B, 17)
    draw.text((tx, y + 16), kicker, font=f_kick, fill=accent)
    f_head = load_font(SERIF_B, 27)
    draw_lines(draw, tx, y + 46, headline, f_head, INK, inner_w, 33)
    f_deck = load_font(SANS, 16)
    draw_lines(draw, tx, y + 118, deck, f_deck, GREY, inner_w, 21)


# --- hero ----------------------------------------------------------------
def hero_band() -> Image.Image:
    """Resize hero.png to cover the 1024 x HERO_H band (centre crop)."""
    src = Image.open(HERO_PATH).convert("RGB")
    sw, sh = src.size
    scale = max(W / sw, HERO_H / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    resized = src.resize((nw, nh), Image.LANCZOS)
    top = (nh - HERO_H) // 2
    return resized.crop((0, top, W, top + HERO_H))


# --- build ---------------------------------------------------------------
def build() -> Path:
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Hero cartoon illustration across the top.
    img.paste(hero_band(), (0, 0))

    # Vivid red masthead.
    draw.rectangle([0, MAST_TOP, W - 1, MAST_BOT - 1], fill=CRIMSON)
    f_eye = load_font(SANS_B, 20)
    draw.text((MARGIN, MAST_TOP + 14), "THE WORLD IN ONE IMAGE",
              font=f_eye, fill=GOLD)
    f_date = load_font(SANS_B, 52)
    draw.text((MARGIN, MAST_TOP + 38), "22 NOVEMBER 2026",
              font=f_date, fill=WHITE)
    f_side = load_font(SANS_B, 20)
    for i, line in enumerate(["SUNDAY", "WORLD NEWS"]):
        lw = draw.textlength(line, font=f_side)
        draw.text((RIGHT - lw, MAST_TOP + 16 + i * 26), line,
                  font=f_side, fill=WHITE)
    draw.rectangle([0, MAST_BOT - 4, W - 1, MAST_BOT - 1], fill=GOLD)

    # Lead story, full width.
    f_badge = load_font(SANS_B, 16)
    badge_text = "LEAD STORY"
    bw = int(draw.textlength(badge_text, font=f_badge)) + 32
    draw.rounded_rectangle([MARGIN, LEAD_BADGE_Y,
                            MARGIN + bw, LEAD_BADGE_Y + 30],
                           radius=6, fill=CRIMSON)
    draw.text((MARGIN + 16, LEAD_BADGE_Y + 6), badge_text,
              font=f_badge, fill=WHITE)
    f_kick = load_font(SANS_B, 21)
    draw.text((MARGIN + bw + 14, LEAD_BADGE_Y + 4),
              "MIDDLE EAST ESCALATES", font=f_kick, fill=CRIMSON)
    f_head = load_font(SERIF_B, 33)
    draw_lines(draw, MARGIN, LEAD_HEAD_Y,
               "Iran hits tankers, Bahrain and Riyadh in one night",
               f_head, INK, CONTENT_W, 42)
    f_sub = load_font(SANS, 20)
    draw_lines(draw, MARGIN, LEAD_SUB_Y,
               "3 tankers struck near Hormuz; Bahrain site ablaze, no "
               "injuries; 3 Houthi missiles downed over Riyadh",
               f_sub, GREY, CONTENT_W, 26)
    draw.line([(MARGIN, DIVIDER_Y), (RIGHT, DIVIDER_Y)], fill=RULE, width=1)

    # 2 x 2 story cards.
    cards = [
        (CARD_X1, CARD_TOP1, ACCENT_BLUE, "EL CHAPO ISIDRO CAUGHT",
         "FBI most-wanted cartel boss seized",
         "11 killed in Sinaloa battles \u2014 4 soldiers, 7 gunmen; "
         "fans flee a baseball game"),
        (CARD_X2, CARD_TOP1, ACCENT_TEAL, "FUNERAL BOAT SINKS",
         "24 dead as boat capsizes in Nigeria",
         "Mourners bound for a burial in Bayelsa; 24 rescued, "
         "mechanical failure blamed"),
        (CARD_X1, CARD_TOP2, ACCENT_OCHRE, "TOXIC ALCOHOL",
         "11 dead from toxic alcohol in Manipur",
         "Tainted liquor hospitalises 180+; chief minister confirms "
         "the toll"),
        (CARD_X2, CARD_TOP2, ACCENT_PURPLE, "TRUMP'S RATE CAP",
         "President vows 10% credit-card cap",
         "Will work with Democrats; revives a stalled campaign promise"),
    ]
    for x, y, accent, kicker, headline, deck in cards:
        draw_card(img, draw, x, y, accent, kicker, headline, deck)

    # Sources footer.
    f_foot = load_font(SANS, 17)
    draw.text((MARGIN, FOOT_Y),
              "Sources: Gulf News, CNN, AP, Al Jazeera, Economic Times "
              "| 22 Nov 2026",
              font=f_foot, fill=FOOT_GREY)

    img.save(OUT_PATH, format="PNG")
    return OUT_PATH


def main() -> None:
    out = build()
    data = out.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {out}  {len(data)} bytes  sha256={digest}")


if __name__ == "__main__":
    main()
