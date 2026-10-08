"""Builds the Bambu-branded "Claude in Google Docs" starter kit (2 pages, US Letter).

Brand system (matches Groundwork.pdf and lead-magnet-AGENT.pdf):
  BLACK #18171d, NAVY #272e3a, TEAL #658686, YELLOW #ffe400, GREY #c8c4b6, CREAM #ebeaea
  Poppins Black (headlines), Libre Franklin (body), Playfair Display Italic (sparingly)

Usage: python3 build.py <fonts_dir> <logo_jpg> <out_pdf>
"""
import sys
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit, ImageReader

fonts_dir, logo_jpg, out_pdf = sys.argv[1:4]

BLACK = HexColor("#18171d")
NAVY = HexColor("#272e3a")
TEAL = HexColor("#658686")
YELLOW = HexColor("#ffe400")
GREY = HexColor("#c8c4b6")
CREAM = HexColor("#ebeaea")

pdfmetrics.registerFont(TTFont("Poppins-Black", f"{fonts_dir}/Poppins-Black.ttf"))
pdfmetrics.registerFont(TTFont("LF", f"{fonts_dir}/LibreFranklin-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LF-Semi", f"{fonts_dir}/LibreFranklin-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("LF-Bold", f"{fonts_dir}/LibreFranklin-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Playfair-Italic", f"{fonts_dir}/PlayfairDisplay-Italic.ttf"))

W, H = 612, 792
MX = 43  # side margin, same proportion as Groundwork

# ---- logo: crop the wordmark out of the square Bambu logo (background is exactly BLACK) ----
im = Image.open(logo_jpg).convert("RGB")
bg = im.getpixel((5, 5))
px = im.load()
xs, ys = [], []
for y in range(im.height):
    for x in range(im.width):
        r, g, b = px[x, y]
        if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > 90:
            xs.append(x)
            ys.append(y)
pad = 20
box = (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)
logo = im.crop(box).convert("RGBA")
# the source is a JPEG with a near-black box: make that box transparent so it blends into the footer
lp = logo.load()
for y in range(logo.height):
    for x in range(logo.width):
        r, g, b, _ = lp[x, y]
        dist = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
        lp[x, y] = (r, g, b, 0 if dist < 25 else min(255, int((dist - 25) * 255 / 65)))
LOGO_RATIO = logo.width / logo.height
logo_reader = ImageReader(logo)

# ---- copy (from the original draft, unchanged) ----
INTRO = (
    "Claude now sits in a sidebar inside Google Docs, Sheets, and Slides. It can read the file "
    "you have open and make edits right inside it. You approve each change one by one, so "
    "nothing slips in without you. It is in public beta now for paid Claude plans. Here are 10 "
    "prompts to copy, paste, and use in your real marketing work."
)
DOCS = [
    ("Rewrite this like I talk.", "Rewrite this draft in my voice. Keep it friendly, short sentences, no fancy words."),
    ("Turn my notes into an email.", "Turn these rough notes into a short email for my customers. Give it a subject line."),
    ("Cut this in half.", "Make this text half as long. Keep every key point. Drop the fluff."),
    ("Write 10 hooks for this idea.", "Give me 10 first-line hooks for this topic. Make each one a full sentence I can use."),
    ("Fix the tone before I send.", "Read this and tell me if it sounds friendly, bossy, or bored. Then fix it so it sounds friendly and confident."),
]
SHEETS = [
    ("Explain my spreadsheet in plain words.", "Look at this sheet and tell me what the numbers mean in three short sentences."),
    ("Find the messy data.", "Find duplicate rows, empty cells, and weird formatting in this sheet, and fix them."),
    ("Turn bullets into a slide.", "Turn these bullet points into clean slide text: one big headline, three short lines."),
    ("Describe this chart for me.", "Write one sentence that describes what this chart shows, in plain words a teen would understand."),
    ("Draft the follow-up note.", "After reading my meeting notes in this doc, draft a short follow-up message I can send."),
]
RULE_LEAD = "Claude drafts, you approve."
RULE_BODY = (
    "Every edit lands one by one, and you say yes to each one. Never publish something you did "
    "not read. Claude saves the typing time. You keep the final word."
)

FOOTER_H = 104


def tracked(c, x, y, text, font, size, space, color, align="left"):
    width = pdfmetrics.stringWidth(text, font, size) + space * len(text)
    if align == "center":
        x = x - width / 2
    c.saveState()  # keep the letter-spacing from leaking into later text
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(space)
    t.setFillColor(color)
    t.textOut(text)
    c.drawText(t)
    c.restoreState()


def flag(c):
    c.setFillColor(YELLOW)
    p = c.beginPath()
    p.moveTo(W - 52, H)
    p.lineTo(W, H)
    p.lineTo(W, H - 52)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def header(c, title_lines, subtitle, height=168):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(BLACK)
    c.rect(0, H - height, W, height, stroke=0, fill=1)
    flag(c)
    top = H - 36
    tracked(c, MX, top, "BAMBU MARKETING CO.  ·  FREE GUIDE", "LF-Bold", 9.5, 2.4, TEAL)
    y = top - 40
    for line in title_lines:
        c.setFillColor(YELLOW)
        c.setFont("Poppins-Black", 34)
        c.drawString(MX, y, line)
        y -= 40
    c.setFillColor(GREY)
    c.setFont("Playfair-Italic", 14)
    c.drawString(MX, y - 4, subtitle)
    return H - height


def footer(c):
    c.setFillColor(BLACK)
    c.rect(0, 0, W, FOOTER_H, stroke=0, fill=1)
    c.setFillColor(CREAM)
    c.setFont("Playfair-Italic", 14)
    c.drawCentredString(W / 2, FOOTER_H - 28, "your marketing matters. let's go.")
    lh = 30
    c.drawImage(logo_reader, W / 2 - lh * LOGO_RATIO / 2, FOOTER_H - 28 - 14 - lh, width=lh * LOGO_RATIO, height=lh, mask="auto")
    c.setFillColor(GREY)
    c.setFont("LF-Semi", 9)
    c.drawCentredString(W / 2, 14, "Bambu Marketing Co.  ·  @bambumarketingco  ·  day 10 of 90")


def card(c, y_top, num, title, body, w=W - 2 * MX, x=MX):
    text_x = x + 62
    avail = w - 62 - 20
    lines = simpleSplit(body, "LF", 10.5, avail)
    h = 14 + 15 + 5 + 14.5 * len(lines) + 12
    c.setFillColor(white)
    c.roundRect(x, y_top - h, w, h, 6, stroke=0, fill=1)
    # numbered chip: black rounded square, yellow numeral (same as the AGENT checklist)
    chip = 30
    c.setFillColor(BLACK)
    c.roundRect(x + 18, y_top - 14 - chip + 2, chip, chip, 6, stroke=0, fill=1)
    c.setFillColor(YELLOW)
    c.setFont("Poppins-Black", 13 if num < 10 else 11.5)
    c.drawCentredString(x + 18 + chip / 2, y_top - 14 - chip + 2 + 10.5, str(num))
    c.setFillColor(BLACK)
    c.setFont("Poppins-Black", 12)
    c.drawString(text_x, y_top - 14 - 10, title)
    c.setFillColor(NAVY)
    c.setFont("LF", 10.5)
    ty = y_top - 14 - 15 - 5 - 8
    for ln in lines:
        c.drawString(text_x, ty, ln)
        ty -= 14.5
    return y_top - h


def cards(c, y, items, start_num, gap=9):
    for i, (t, b) in enumerate(items):
        y = card(c, y, start_num + i, t, b) - gap
    return y + gap


def paragraph(c, x, y, text, font, size, leading, width, color):
    c.setFillColor(color)
    c.setFont(font, size)
    for ln in simpleSplit(text, font, size, width):
        c.drawString(x, y, ln)
        y -= leading
    return y + leading


c = canvas.Canvas(out_pdf, pagesize=(W, H))
c.setTitle("Meet Your Helper. Inside Your Files.")
c.setAuthor("Bambu Marketing Co.")
c.setSubject("Claude in Google Docs, Sheets, and Slides: 10 prompts to copy and paste")

# ---------------- page 1 ----------------
y = header(c, ["Meet your helper.", "Inside your files."], "claude just moved into your google docs")
y = paragraph(c, MX, y - 30, INTRO, "LF", 11, 17, W - 2 * MX, NAVY)
y = cards(c, y - 28, DOCS, 1, gap=17)
assert y > FOOTER_H + 12, f"page 1 content runs into footer: {y}"
footer(c)
print("page 1 content bottom", round(y), "footer top", FOOTER_H)
c.showPage()

# ---------------- page 2 ----------------
y = header(c, ["Sheets. Slides.", "Sorted."], "5 more prompts for sheets and slides")
y = cards(c, y - 20, SHEETS, 6, gap=7)

# callout: black box, yellow left bar (same as Groundwork's closing line)
cw = W - 2 * MX
body_lines = simpleSplit(RULE_BODY, "LF", 11, cw - 48)
ch = 20 + 10 + 24 + 8 + 16.5 * len(body_lines) + 20
cy_top = y - 18
c.setFillColor(BLACK)
c.rect(MX, cy_top - ch, cw, ch, stroke=0, fill=1)
c.setFillColor(YELLOW)
c.rect(MX, cy_top - ch, 5, ch, stroke=0, fill=1)
tracked(c, MX + 24, cy_top - 28, "THE RULE TO REMEMBER", "LF-Bold", 9, 2.2, TEAL)
c.setFillColor(YELLOW)
c.setFont("Poppins-Black", 18)
c.drawString(MX + 24, cy_top - 54, RULE_LEAD)
c.setFillColor(white)
c.setFont("LF", 11)
ty = cy_top - 54 - 24
for ln in body_lines:
    c.drawString(MX + 24, ty, ln)
    ty -= 16.5
bottom = cy_top - ch
assert bottom > FOOTER_H + 12, f"page 2 content runs into footer: {bottom}"
footer(c)
print("page 2 content bottom", round(bottom), "footer top", FOOTER_H)
c.showPage()
c.save()
print("wrote", out_pdf)
