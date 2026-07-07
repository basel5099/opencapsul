"""Tiny diagram-animation engine: PIL frames -> ffmpeg scenes. Dark GitHub-style theme."""
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FPS = 30

BG      = (13, 17, 23)      # github dark
PANEL   = (22, 27, 34)
EDGE    = (48, 54, 61)
TXT     = (230, 237, 243)
DIM     = (139, 148, 158)
TEAL    = (57, 197, 207)
AMBER   = (255, 179, 71)
GREEN   = (63, 185, 80)
RED     = (248, 81, 73)
BLUE    = (88, 166, 255)
PURPLE  = (188, 140, 255)

_FONTS = {}
def font(size, bold=False):
    key = (size, bold)
    if key not in _FONTS:
        path = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
        _FONTS[key] = ImageFont.truetype(path, size)
    return _FONTS[key]

def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def rev(t, start, dur=0.6):
    """Reveal progress 0..1 for an element that starts at `start` seconds."""
    return ease((t - start) / dur)

def lerp(a, b, p):
    return a + (b - a) * p

def col_a(c, alpha):
    return (c[0], c[1], c[2], int(255 * max(0, min(1, alpha))))

class Frame:
    def __init__(self):
        self.im = Image.new("RGB", (W, H), BG)
        self.ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.ov)

    def text(self, xy, s, size=34, color=TXT, alpha=1.0, bold=False, anchor="la", maxw=None):
        if alpha <= 0: return
        f = font(size, bold)
        if maxw:  # simple wrap
            words, lines, cur = s.split(), [], ""
            for w_ in words:
                trial = (cur + " " + w_).strip()
                if self.d.textlength(trial, font=f) <= maxw: cur = trial
                else: lines.append(cur); cur = w_
            lines.append(cur)
            y = xy[1]
            for ln in lines:
                self.d.text((xy[0], y), ln, font=f, fill=col_a(color, alpha), anchor=anchor)
                y += size * 1.35
            return
        self.d.text(xy, s, font=f, fill=col_a(color, alpha), anchor=anchor)

    def box(self, x, y, w, h, alpha=1.0, fill=PANEL, edge=EDGE, r=14, ew=2):
        if alpha <= 0: return
        self.d.rounded_rectangle([x, y, x + w, y + h], radius=r,
                                 fill=col_a(fill, alpha), outline=col_a(edge, alpha), width=ew)

    def chip(self, x, y, w, h, title, sub=None, alpha=1.0, edge=TEAL, pins=0):
        if alpha <= 0: return
        self.box(x, y, w, h, alpha, fill=PANEL, edge=edge, r=12, ew=3)
        cy = y + h / 2 - (14 if sub else 0)
        self.text((x + w / 2, cy), title, 30, TXT, alpha, bold=True, anchor="mm")
        if sub:
            self.text((x + w / 2, cy + 34), sub, 22, DIM, alpha, anchor="mm")
        for i in range(pins):  # decorative pins left+right
            py = y + h * (i + 1) / (pins + 1)
            self.d.rectangle([x - 10, py - 3, x, py + 3], fill=col_a(edge, alpha * 0.8))
            self.d.rectangle([x + w, py - 3, x + w + 10, py + 3], fill=col_a(edge, alpha * 0.8))

    def line(self, pts, color=DIM, width=4, alpha=1.0, progress=1.0, dash=None):
        """Polyline drawn up to `progress` of its length. dash=(on,off) for dashed."""
        if alpha <= 0 or progress <= 0: return
        segs, total = [], 0.0
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            L = math.hypot(x2 - x1, y2 - y1)
            segs.append((x1, y1, x2, y2, L)); total += L
        drawn = total * ease(progress)
        for x1, y1, x2, y2, L in segs:
            if drawn <= 0: break
            frac = min(1.0, drawn / L)
            ex, ey = lerp(x1, x2, frac), lerp(y1, y2, frac)
            if dash:
                on, off = dash
                n = int(L * frac / (on + off)) + 1
                for k in range(n):
                    s0 = k * (on + off); s1 = min(s0 + on, L * frac)
                    if s0 >= L * frac: break
                    self.d.line([lerp(x1, x2, s0 / L), lerp(y1, y2, s0 / L),
                                 lerp(x1, x2, s1 / L), lerp(y1, y2, s1 / L)],
                                fill=col_a(color, alpha), width=width)
            else:
                self.d.line([x1, y1, ex, ey], fill=col_a(color, alpha), width=width)
            drawn -= L

    def arrow(self, pts, color=DIM, width=4, alpha=1.0, progress=1.0, label=None, lab_dy=-30, lab_size=22):
        self.line(pts, color, width, alpha, progress)
        if progress >= 0.999 and alpha > 0:
            (x1, y1), (x2, y2) = pts[-2], pts[-1]
            ang = math.atan2(y2 - y1, x2 - x1)
            for s in (2.6, 2.6):
                pass
            a1, a2 = ang + 2.6, ang - 2.6
            hl = 16
            self.d.polygon([(x2, y2),
                            (x2 + hl * math.cos(a1), y2 + hl * math.sin(a1)),
                            (x2 + hl * math.cos(a2), y2 + hl * math.sin(a2))],
                           fill=col_a(color, alpha))
        if label and alpha > 0 and progress > 0.5:
            mx = sum(p[0] for p in pts) / len(pts)
            my = sum(p[1] for p in pts) / len(pts)
            self.text((mx, my + lab_dy), label, lab_size, color, alpha * min(1, (progress - 0.5) * 4), anchor="mm")

    def packet(self, pts, phase, color=AMBER, r=9, alpha=1.0):
        """Glowing dot at `phase` (0..1, wraps) along polyline."""
        if alpha <= 0: return
        phase %= 1.0
        segs, total = [], 0.0
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            L = math.hypot(x2 - x1, y2 - y1)
            segs.append((x1, y1, x2, y2, L)); total += L
        target = total * phase
        for x1, y1, x2, y2, L in segs:
            if target <= L:
                x, y = lerp(x1, x2, target / L), lerp(y1, y2, target / L)
                for rr, aa in ((r * 2.2, 0.25), (r * 1.5, 0.5), (r, 1.0)):
                    self.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col_a(color, alpha * aa))
                return
            target -= L

    def wave(self, cx, cy, t, color=TEAL, n=3, alpha=1.0, rmax=90, gap=0.8):
        """Expanding ripple arcs (radio waves)."""
        if alpha <= 0: return
        for k in range(n):
            ph = (t / gap - k * 0.33) % 1.0
            r = 18 + ph * rmax
            a = alpha * (1 - ph) * 0.9
            if a <= 0: continue
            self.d.arc([cx - r, cy - r, cx + r, cy + r], start=-55, end=55, fill=col_a(color, a), width=5)

    def capsule_icon(self, cx, cy, scale=1.0, alpha=1.0, leds_on=True):
        """Side-view capsule with dome on the left."""
        if alpha <= 0: return
        L, R_ = 260 * scale, 62 * scale
        x0, y0 = cx - L / 2, cy
        body = col_a((235, 238, 240), alpha)
        self.d.rounded_rectangle([x0, y0 - R_, x0 + L, y0 + R_], radius=R_, fill=body)
        dr = R_ * 0.94
        self.d.ellipse([x0 - dr * 0.25, y0 - dr, x0 + dr * 1.75, y0 + dr],
                       outline=col_a((170, 200, 215), alpha), width=max(2, int(4 * scale)),
                       fill=col_a((28, 36, 44), alpha))
        lens_r = R_ * 0.30
        lx = x0 + dr * 0.72
        self.d.ellipse([lx - lens_r, y0 - lens_r, lx + lens_r, y0 + lens_r], fill=col_a((10, 10, 12), alpha))
        if leds_on:
            for ang in (90, 210, 330):
                a = math.radians(ang)
                px, py = lx + math.cos(a) * R_ * 0.62, y0 + math.sin(a) * R_ * 0.62
                rr = R_ * 0.12
                self.d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col_a(AMBER, alpha))

    def footer(self, alpha=0.8):
        self.text((W / 2, H - 34), "OpenCapsule-EDU  ·  github.com/basel5099/opencapsul  ·  educational bench replica — not a medical device",
                  20, DIM, alpha, anchor="mm")

    def title(self, s, t, sub=None):
        self.text((W / 2, 78), s, 52, TXT, rev(t, 0.1), bold=True, anchor="mm")
        if sub:
            self.text((W / 2, 132), sub, 27, DIM, rev(t, 0.5), anchor="mm")

    def render(self):
        self.im.paste(self.ov, (0, 0), self.ov)
        return self.im

def render_scene(name, seconds, draw_fn, outdir="."):
    """draw_fn(fr: Frame, t: seconds) -> None. Writes <outdir>/<name>.mp4"""
    import subprocess, shutil
    fdir = os.path.join(outdir, "frames_" + name)
    os.makedirs(fdir, exist_ok=True)
    n = int(seconds * FPS)
    for i in range(n):
        fr = Frame()
        draw_fn(fr, i / FPS)
        fr.footer()
        fr.render().save(os.path.join(fdir, f"{i:05d}.png"))
    out = os.path.join(outdir, name + ".mp4")
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(fdir, "%05d.png"),
                    "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p", out],
                   check=True, capture_output=True)
    shutil.rmtree(fdir)
    print("scene", name, f"{seconds:.0f}s OK")
    return out
