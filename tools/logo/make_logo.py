"""Generate the OpenCapsule-EDU logo PNGs and the GitHub social-preview card.

The SVG source of truth is docs/media/logo.svg — this script re-draws the same
geometry with PIL (no SVG renderer needed) and exports:
  docs/media/logo.png            512x512  transparent, icon only
  docs/media/logo-wordmark.png   1200x400 transparent, icon + name
  docs/media/social-preview.png  1280x640 dark card for GitHub Settings > Social preview
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

BODY  = (235, 238, 240, 255)
DOME  = (28, 36, 44, 255)
RIM   = (170, 200, 215, 255)
LENS  = (10, 10, 12, 255)
LED   = (255, 179, 71, 255)
BG    = (13, 17, 23, 255)
TXT   = (230, 237, 243, 255)
DIM   = (139, 148, 158, 255)
TEAL  = (57, 197, 207, 255)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO_ROOT, "docs", "media")

def fnt(size, bold=True):
    p = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    try:
        return ImageFont.truetype(p, size)
    except OSError:
        return ImageFont.load_default(size)

def draw_capsule(d, cx, cy, scale, ss=1):
    """Same geometry as the video engine's capsule_icon. ss = supersample factor."""
    L, R = 260 * scale * ss, 62 * scale * ss
    x0, y0 = cx * ss - L / 2, cy * ss
    d.rounded_rectangle([x0, y0 - R, x0 + L, y0 + R], radius=R, fill=BODY)
    dr = R * 0.94
    d.ellipse([x0 - dr * 0.25, y0 - dr, x0 + dr * 1.75, y0 + dr],
              fill=DOME, outline=RIM, width=max(2, int(4 * scale * ss)))
    lens_r = R * 0.30
    lx = x0 + dr * 0.72
    d.ellipse([lx - lens_r, y0 - lens_r, lx + lens_r, y0 + lens_r], fill=LENS)
    for ang in (90, 210, 330):
        a = math.radians(ang)
        px, py = lx + math.cos(a) * R * 0.62, y0 + math.sin(a) * R * 0.62
        rr = R * 0.12
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=LED)

def canvas(w, h, bg, ss=4):
    im = Image.new("RGBA", (w * ss, h * ss), bg)
    return im, ImageDraw.Draw(im), ss

def save(im, ss, name):
    im = im.resize((im.width // ss, im.height // ss), Image.LANCZOS)
    im.save(os.path.join(OUT, name))
    print(name, im.size)

# 1) square icon, transparent
im, d, ss = canvas(512, 512, (0, 0, 0, 0))
draw_capsule(d, 256, 256, 1.55, ss)
save(im, ss, "logo.png")

# 2) wordmark, transparent
im, d, ss = canvas(1200, 400, (0, 0, 0, 0))
draw_capsule(d, 330, 190, 1.7, ss)
d.text((620 * ss, 190 * ss), "OpenCapsule", font=fnt(96 * ss), fill=TXT, anchor="lm")
d.text((620 * ss, 268 * ss), "EDU  ·  learn how capsule endoscopes work",
       font=fnt(34 * ss, bold=False), fill=DIM, anchor="lm")
save(im, ss, "logo-wordmark.png")

# 3) GitHub social preview 1280x640
im, d, ss = canvas(1280, 640, BG)
draw_capsule(d, 640, 230, 1.9, ss)
d.text((640 * ss, 420 * ss), "OpenCapsule-EDU", font=fnt(84 * ss), fill=TXT, anchor="mm")
d.text((640 * ss, 500 * ss), "capsule-endoscope teardown  ·  ultra-low-power electronics  ·  sub-1 GHz RF",
       font=fnt(30 * ss, bold=False), fill=DIM, anchor="mm")
d.text((640 * ss, 560 * ss), "educational bench replica — not a medical device",
       font=fnt(24 * ss, bold=False), fill=TEAL, anchor="mm")
save(im, ss, "social-preview.png")
print("DONE")
