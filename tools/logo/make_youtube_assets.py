"""Generate YouTube channel assets into docs/media/youtube/.

  avatar-800.png       800x800   channel profile picture
  banner-2048x1152.png           channel art; all critical content inside the
                                 1235x338 center safe area (visible on all devices)
  watermark-150.png    150x150   video watermark (Customization > Branding)
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from make_logo import draw_capsule, canvas, fnt, BG, TXT, DIM, TEAL
from PIL import Image, ImageDraw

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO_ROOT, "docs", "media", "youtube")
os.makedirs(OUT, exist_ok=True)

def save(im, ss, name):
    im = im.resize((im.width // ss, im.height // ss), Image.LANCZOS)
    im.save(os.path.join(OUT, name))
    print(name, im.size)

# 1) avatar 800x800 — dark disc bg so it reads well as a circle crop
im, d, ss = canvas(800, 800, (0, 0, 0, 0))
d.ellipse([0, 0, 800 * ss, 800 * ss], fill=BG)
draw_capsule(d, 400, 400, 2.1, ss)
save(im, ss, "avatar-800.png")

# 2) banner 2048x1152, safe area 1235x338 centered (x 406..1641, y 407..745)
im, d, ss = canvas(2048, 1152, BG)
# subtle full-bleed decoration outside safe area: faint oversized capsule
draw_capsule(d, 1780, 200, 2.6, ss)
# safe-area content
draw_capsule(d, 620, 576, 1.5, ss)
d.text((810 * ss, 545 * ss), "OpenCapsule-EDU", font=fnt(74 * ss), fill=TXT, anchor="lm")
d.text((812 * ss, 625 * ss), "how swallowable cameras work — teardown, electronics, RF",
       font=fnt(28 * ss, bold=False), fill=DIM, anchor="lm")
d.text((812 * ss, 678 * ss), "github.com/basel5099/opencapsul",
       font=fnt(26 * ss, bold=False), fill=TEAL, anchor="lm")
save(im, ss, "banner-2048x1152.png")

# 3) watermark 150x150
im, d, ss = canvas(150, 150, (0, 0, 0, 0))
draw_capsule(d, 75, 75, 0.42, ss)
save(im, ss, "watermark-150.png")
print("DONE ->", OUT)
