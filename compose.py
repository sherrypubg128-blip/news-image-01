#!/usr/bin/env python3
"""Compose the news-image-01 entry: a one-page newspaper front page that sums
up Friday 13 November 2026 in one image.

Four AI-generated photo-style illustrations (no text in them) are laid out with
crisp PIL-rendered headlines and captions, so every word is legible and every
fact is one reported on 13 November 2026. Output: entry.jpg, 1024x1024.
"""
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PANELS = HERE.parent / "panels"

INK = (17, 17, 17)
PAPER = (247, 244, 236)
RED = (179, 35, 27)
GREY = (90, 88, 82)
RULE = (17, 17, 17)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def crop_to(img, w, h, focus_y=0.5):
    """Centre-crop to w:h, biasing the vertical window toward focus_y."""
    iw, ih = img.size
    target = w / h
    if iw / ih > target:  # too wide: trim sides
        nw = int(ih * target)
        x0 = (iw - nw) // 2
        box = (x0, 0, x0 + nw, ih)
    else:  # too tall: trim top/bottom around focus_y
        nh = int(iw / target)
        cy = int(ih * focus_y)
        y0 = max(0, min(ih - nh, cy - nh // 2))
        box = (0, y0, iw, y0 + nh)
    return img.crop(box).resize((w, h), Image.LANCZOS)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to a pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    page = Image.new("RGB", (1024, 1024), PAPER)
    d = ImageDraw.Draw(page)
    mx = 24  # margin
    cw = 1024 - 2 * mx  # content width 976

    # --- masthead -------------------------------------------------------
    d.text((512, 14), "FRIDAY 13 NOVEMBER 2026", font=font(SANS_B, 17),
           fill=INK, anchor="ma")
    d.line([(mx, 42), (1024 - mx, 42)], fill=RULE, width=2)
    d.text((512, 50), "THE WORLD IN ONE DAY", font=font(SERIF_B, 60),
           fill=INK, anchor="ma")
    d.text((512, 118), "The day's news, in one picture",
           font=font(SERIF, 21), fill=GREY, anchor="ma")
    d.line([(mx, 146), (1024 - mx, 146)], fill=RULE, width=2)
    d.line([(mx, 150), (1024 - mx, 150)], fill=RULE, width=1)

    # --- lead story: Gulf ----------------------------------------------
    lead = Image.open(PANELS / "media-generation-hormuz-tankers-0-ca630194-6226-4972-934c-de18473990c4.webp").convert("RGB")
    page.paste(crop_to(lead, cw, 322, focus_y=0.55), (mx, 158))
    y = 490
    d.text((mx, y), "THE GULF", font=font(SANS_B, 17), fill=RED)
    y += 26
    d.text((mx, y), "Tankers hit in the Gulf", font=font(SERIF_B, 40), fill=INK)
    y += 48
    cap = ("Explosions strike oil tankers in the Strait of Hormuz, and Iran says "
           "it destroyed a US radar in Bahrain. Brent crude jumps past $95 a barrel.")
    for line in wrap(d, cap, font(SANS, 18), cw):
        d.text((mx, y), line, font=font(SANS, 18), fill=INK)
        y += 23
    d.line([(mx, 616), (1024 - mx, 616)], fill=RULE, width=1)

    # --- second row: three stories --------------------------------------
    cols = [
        ("media-generation-taiwan-drills-0-76908b77-0023-49fd-b95c-4ba31734d6a4.webp",
         "ASIA", "China's big Pacific drills",
         "Taiwan details large, unannounced Chinese naval exercises around the island."),
        ("media-generation-nvidia-markets-0-c0884e1e-b87a-4643-9a76-36d24d8ecdbb.webp",
         "MARKETS", "Nvidia chief quits; shares tumble",
         "Jensen Huang resigns as CEO; the shares fall 14% early and Wall Street closes red."),
        ("media-generation-ukraine-talks-0-b99014a8-d686-479d-8bc1-db1a93e0a966.webp",
         "EUROPE", "Europe joins Ukraine peace talks",
         "Envoys brief Zelensky after meeting Putin; the war's biggest prisoner swap begins."),
    ]
    col_w, gap = 312, 20
    for i, (fname, kicker, head, caption) in enumerate(cols):
        x = mx + i * (col_w + gap)
        img = Image.open(PANELS / fname).convert("RGB")
        page.paste(crop_to(img, col_w, 168, focus_y=0.5), (x, 626))
        yy = 802
        d.text((x, yy), kicker, font=font(SANS_B, 15), fill=RED)
        yy += 22
        for line in wrap(d, head, font(SERIF_B, 23), col_w):
            d.text((x, yy), line, font=font(SERIF_B, 23), fill=INK)
            yy += 28
        yy += 4
        for line in wrap(d, caption, font(SANS, 14), col_w):
            d.text((x, yy), line, font=font(SANS, 14), fill=INK)
            yy += 18
    d.line([(mx, 928), (1024 - mx, 928)], fill=RULE, width=1)

    # --- in brief --------------------------------------------------------
    d.text((mx, 938), "IN BRIEF", font=font(SANS_B, 16), fill=INK)
    note = "Illustrations AI-generated  ·  Facts as reported 13 Nov 2026"
    d.text((1024 - mx, 938), note, font=font(SANS, 13), fill=GREY, anchor="ra")
    briefs = [
        ("SYRIA — ", "A French warship docks at Latakia, the first French naval visit to Syria."),
        ("PERU — ", "Pope Leo meets abuse survivors in Lima as record crowds line the streets."),
        ("ENERGY — ", "The IEA forecasts an oil surplus into year-end despite the Gulf danger."),
    ]
    for i, (lead_in, text) in enumerate(briefs):
        x = mx + i * (col_w + gap)
        yy = 964
        line = lead_in + text
        for ln in wrap(d, line, font(SANS, 14), col_w):
            # bold the lead-in on the first line only
            if ln.startswith(lead_in):
                d.text((x, yy), lead_in, font=font(SANS_B, 14), fill=INK)
                rest = ln[len(lead_in):]
                d.text((x + d.textlength(lead_in, font=font(SANS_B, 14)), yy),
                       rest, font=font(SANS, 14), fill=INK)
            else:
                d.text((x, yy), ln, font=font(SANS, 14), fill=INK)
            yy += 18

    out = HERE / "entry.jpg"
    page.save(out, "JPEG", quality=88)
    print(f"wrote {out} {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
