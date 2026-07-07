"""All scenes for the OpenCapsule-EDU technical explainer. Run: python scenes.py"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.join(os.path.dirname(__file__)))
from engine import *

# ---------------------------------------------------------------- S01 title
def s01(fr, t):
    fr.capsule_icon(W/2, 470, scale=1.6, alpha=rev(t, 0.2, 1.0),
                    leds_on=(math.sin(t*3) > -0.4))
    fr.text((W/2, 680), "OpenCapsule-EDU", 84, TXT, rev(t, 0.8), bold=True, anchor="mm")
    fr.text((W/2, 760), "Technical overview — how the system works, block by block",
            34, DIM, rev(t, 1.4), anchor="mm")
    fr.text((W/2, 850), "Based on a real capsule-endoscope teardown, rebuilt with 2026 parts",
            26, TEAL, rev(t, 2.0), anchor="mm")

# ---------------------------------------------------------------- S02 stack
STACK = [  # (h, fill, label, sublabel)
    (44,  (28, 36, 44),    "Transparent dome",            "protects the optics"),
    (34,  (46, 110, 66),   "LED ring board",              "4 x white LEDs — pulsed, not continuous"),
    (44,  (46, 110, 66),   "Lens + CMOS sensor",          "wide-angle, ~320 x 320 px"),
    (34,  (46, 110, 66),   "Compression ASIC",            "custom chip (LJ215C) — hardware JPEG-class"),
    (56,  (185, 190, 196), "2 x SR927R batteries",        "silver-oxide, 3.1 V, 45 mAh, high-drain"),
    (34,  (46, 110, 66),   "Radio board — TI CC1310",     "sub-1 GHz MCU + 24 MHz crystal + balun"),
    (40,  (196, 128, 62),  "Meandered flex antenna",      "rolled into the rear shell"),
]
def s02(fr, t):
    fr.title("Inside a real capsule", t, "seven layers in 11 x 26 mm — one folded rigid-flex assembly")
    x, w = 560, 330
    y = 240
    for i, (h, fill, lab, sub) in enumerate(STACK):
        a = rev(t, 1.0 + i * 1.6, 0.8)
        hh = h * 1.9
        if i == 0 and a > 0:
            fr.d.pieslice([x, y, x + w, y + hh * 2.4], 180, 360,
                          fill=col_a(fill, a), outline=col_a((170, 200, 215), a), width=3)
        else:
            fr.box(x, y, w, hh, a, fill=fill, edge=(90, 96, 104), r=10)
        fr.text((x + w + 60, y + hh / 2 - 14), lab, 30, TXT, a, bold=True)
        fr.text((x + w + 60, y + hh / 2 + 22), sub, 23, DIM, a)
        fr.line([(x + w + 14, y + hh / 2), (x + w + 48, y + hh / 2)], TEAL, 3, a)
        y += hh + 16
    fr.text((x - 340, 500), "found in the teardown:", 24, DIM, rev(t, 0.6), anchor="mm")
    fr.text((x - 340, 545), "every layer earns", 24, DIM, rev(t, 0.6), anchor="mm")
    fr.text((x - 340, 580), "its micrometers", 24, DIM, rev(t, 0.6), anchor="mm")

# ---------------------------------------------------------------- S03 chain
def s03(fr, t):
    fr.title("The signal chain", t, "from photons to the doctor's screen")
    y = 420
    boxes = [
        (120,  260, "CMOS sensor",   "raw pixels"),
        (470,  260, "ASIC",          "compress ~10:1"),
        (820,  260, "CC1310",        "radio MCU"),
        (1170, 200, "Antenna",       "meandered flex"),
    ]
    for i, (x, w, lab, sub) in enumerate(boxes):
        a = rev(t, 0.8 + i * 0.9)
        fr.chip(x, y, w, 130, lab, sub, a, edge=TEAL if i < 3 else AMBER)
    labels = ["parallel pixel bus", "SPI  <= 4 Mbps", "RF_P / RF_N + balun"]
    for i in range(3):
        x1 = boxes[i][0] + boxes[i][1]
        x2 = boxes[i + 1][0]
        a = rev(t, 1.3 + i * 0.9)
        fr.arrow([(x1, y + 65), (x2, y + 65)], BLUE, 4, a, rev(t, 1.3 + i * 0.9, 1.0),
                 label=labels[i], lab_dy=-34, lab_size=22)
    # body + receiver
    a_body = rev(t, 4.6)
    bx = 1450
    fr.d.ellipse([bx, y - 60, bx + 210, y + 250], outline=col_a(PURPLE, a_body * 0.9), width=4)
    fr.text((bx + 105, y - 90), "~30 cm of tissue", 24, PURPLE, a_body, anchor="mm")
    fr.text((bx + 105, y + 290), "sub-1 GHz crosses it —\n2.4 GHz would be absorbed", 22, DIM, a_body, anchor="ma")
    if t > 5.2:
        fr.wave(1395, y + 65, t, TEAL, alpha=rev(t, 5.2))
    a_rx = rev(t, 5.8)
    fr.chip(1700, y, 180, 130, "Receiver", "on-body patches", a_rx, edge=GREEN)
    fr.line([(bx + 210, y + 65), (1700, y + 65)], GREEN, 4, a_rx, rev(t, 5.8, 1.0), dash=(10, 8))
    # animated packets across the whole path
    if t > 7:
        path = [(380, y + 65), (820, y + 65), (1170, y + 65), (1700, y + 65)]
        for k in range(3):
            fr.packet(path, (t - 7) / 6 + k * 0.33, AMBER, alpha=min(1, t - 7))
    fr.text((W/2, 800), "Peak radio rate 4 Mbps — exactly the CC1310's SPI subordinate limit. The pipe is matched end-to-end.",
            26, DIM, rev(t, 9.0), anchor="mm")
    fr.text((W/2, 850), "A few compressed frames per second, sent as short bursts — the radio sleeps in between.",
            26, DIM, rev(t, 12.0), anchor="mm")

# ---------------------------------------------------------------- S04 wiring
def s04(fr, t):
    fr.title("Our bench replica — wiring", t, "camera  ->  Apollo510 'brain'  ->  CC1310 'modem'")
    cam_x, cam_y, cam_w, cam_h = 140, 380, 300, 240
    ap_x,  ap_y,  ap_w,  ap_h  = 700, 300, 420, 420
    cc_x,  cc_y,  cc_w,  cc_h  = 1420, 340, 330, 330
    fr.chip(cam_x, cam_y, cam_w, cam_h, "Camera", "Arducam Mega / HM01B0", rev(t, 0.6), edge=GREEN, pins=4)
    fr.chip(ap_x, ap_y, ap_w, ap_h, "Ambiq Apollo510", "Cortex-M55 + Helium - 3.75 MB SRAM", rev(t, 1.2), edge=TEAL, pins=6)
    fr.chip(cc_x, cc_y, cc_w, cc_h, "TI CC1310", "sub-1 GHz radio MCU", rev(t, 1.8), edge=AMBER, pins=5)
    cam_pins = ["SCLK", "MOSI", "MISO", "CS"]
    for i, p in enumerate(cam_pins):
        yy = cam_y + cam_h * (i + 1) / 5
        a = rev(t, 2.6 + i * 0.55)
        rev_dir = (p == "MISO")
        pts = [(cam_x + cam_w + 10, yy), (ap_x - 10, yy)]
        fr.arrow(pts[::-1] if rev_dir else pts, BLUE, 3, a, a, label=None)
        fr.text(((cam_x + cam_w + ap_x) / 2, yy - 22), p, 21, BLUE, a, anchor="mm")
    fr.text(((cam_x + cam_w + ap_x) / 2, cam_y - 40), "IOM1 - SPI 8 MHz", 24, DIM, rev(t, 2.6), anchor="mm")
    cc_pins = [("SCLK", "DIO_10", False), ("MOSI", "DIO_9", False), ("MISO", "DIO_8", True),
               ("CS", "DIO_11", False), ("READY", "DIO_12", True)]
    for i, (p, dio, rev_dir) in enumerate(cc_pins):
        yy = cc_y + cc_h * (i + 1) / 6
        a = rev(t, 5.2 + i * 0.55)
        pts = [(ap_x + ap_w + 10, yy), (cc_x - 10, yy)]
        color = PURPLE if p == "READY" else BLUE
        fr.arrow(pts[::-1] if rev_dir else pts, color, 3, a, a)
        fr.text(((ap_x + ap_w + cc_x) / 2, yy - 22), f"{p}  ->  {dio}", 21, color, a, anchor="mm")
    fr.text(((ap_x + ap_w + cc_x) / 2, cc_y - 80), "IOM0 - SPI 4 MHz (CC1310 SSI limit)", 24, DIM, rev(t, 5.2), anchor="mm")
    ant = [(cc_x + cc_w + 10, cc_y + 60), (cc_x + cc_w + 60, cc_y + 60), (cc_x + cc_w + 60, cc_y + 20),
           (cc_x + cc_w + 110, cc_y + 20), (cc_x + cc_w + 110, cc_y + 60), (cc_x + cc_w + 160, cc_y + 60)]
    fr.line(ant, AMBER, 4, rev(t, 8.2), rev(t, 8.2, 1.0))
    fr.text((cc_x + cc_w + 85, cc_y - 16), "antenna", 21, AMBER, rev(t, 8.6), anchor="mm")
    fr.text((W/2, 810), "READY (DIO_12) is flow control: the CC1310 de-asserts it while its radio queue is full.",
            26, DIM, rev(t, 10.5), anchor="mm")
    fr.text((W/2, 860), "Roles: Apollo510 owns capture, compression and power; CC1310 is a dumb, reliable radio modem.",
            26, DIM, rev(t, 13.0), anchor="mm")
    fr.text((W/2, 910), "Everything runs on ONE shared 2.0 V rail -> zero level shifters.",
            26, TEAL, rev(t, 16.0), anchor="mm")

# ---------------------------------------------------------------- S05 power
def s05(fr, t):
    fr.title("The power tree", t, "everything negotiates with two watch batteries")
    bx, by = 170, 420
    for i in range(2):
        a = rev(t, 0.6)
        fr.d.ellipse([bx, by + i * 74, bx + 150, by + 60 + i * 74],
                     fill=col_a((188, 193, 199), a), outline=col_a((120, 126, 133), a), width=3)
    fr.text((bx + 75, by + 170), "2 x SR927R", 26, TXT, rev(t, 0.6), bold=True, anchor="mm")
    fr.text((bx + 75, by + 205), "3.1 V - 45 mAh", 22, DIM, rev(t, 0.6), anchor="mm")
    fr.chip(520, 390, 300, 120, "TPS62740", "buck - Iq 360 nA", rev(t, 1.6), edge=TEAL)
    fr.arrow([(bx + 150, by + 65), (520, 450)], DIM, 4, rev(t, 1.2), rev(t, 1.2, 0.8))
    railx1, railx2, raily = 880, 1760, 450
    fr.line([(820, 450), (railx1, raily)], TEAL, 6, rev(t, 2.4), rev(t, 2.4))
    fr.line([(railx1, raily), (railx2, raily)], TEAL, 6, rev(t, 2.6), rev(t, 2.6, 1.0))
    fr.text(((railx1 + railx2) / 2, raily - 36), "shared 2.0 V rail", 28, TEAL, rev(t, 3.0), bold=True, anchor="mm")
    loads = [("Apollo510", "1.71-2.2 V OK", 940), ("CC1310", "1.8-3.8 V OK", 1240), ("HM01B0 I/O", "1.5-2.8 V OK", 1540)]
    for i, (lab, sub, lx) in enumerate(loads):
        a = rev(t, 3.4 + i * 0.8)
        fr.line([(lx + 90, raily), (lx + 90, 540)], TEAL, 4, a, a)
        fr.chip(lx, 540, 180, 110, lab, sub, a, edge=EDGE)
    fr.chip(520, 700, 300, 120, "TLV61046A", "boost -> 3.6 V LED rail", rev(t, 6.4), edge=AMBER)
    fr.arrow([(bx + 150, by + 100), (400, 760), (520, 760)], DIM, 4, rev(t, 6.0), rev(t, 6.0, 0.8))
    fr.arrow([(820, 760), (1000, 760)], AMBER, 4, rev(t, 7.0), rev(t, 7.0, 0.8))
    for ang in range(4):
        a = rev(t, 7.4)
        px = 1050 + ang * 46
        on = (math.sin(t * 6 + ang) > 0.3)
        fr.d.ellipse([px, 740, px + 34, 774], fill=col_a(AMBER if on else PANEL, a),
                     outline=col_a(EDGE, a), width=2)
    fr.text((1290, 757), "LED flash ring", 24, DIM, rev(t, 7.6), anchor="lm")
    fr.text((W/2, 900), "Why boost? Near end-of-life the stack sags to ~2.4 V — below a green/blue LED's forward voltage.",
            25, DIM, rev(t, 9.0), anchor="mm")
    fr.text((W/2, 950), "Plus one grain-of-rice LDO (TPS7A02) for the sensor's clean 2.8 V analog rail.",
            25, DIM, rev(t, 12.0), anchor="mm")

# ---------------------------------------------------------------- S06 pulse
SEGS = [("SLEEP", 0.30, DIM), ("WAKE", 0.06, BLUE), ("FLASH + EXPOSE", 0.14, AMBER),
        ("COMPRESS", 0.16, TEAL), ("RF BURST", 0.14, RED), ("SLEEP", 0.20, DIM)]
def s06(fr, t):
    fr.title("One frame, one heartbeat", t, "the pulse power strategy that makes 45 mAh last 10 hours")
    x0, x1, y0 = 200, 1720, 280
    tot = sum(wd for _, wd, _ in SEGS)
    xx = x0
    for i, (lab, wd, cc) in enumerate(SEGS):
        w = (x1 - x0) * wd / tot
        a = rev(t, 0.8 + i * 0.5)
        fr.box(xx, y0, w - 6, 64, a, fill=(cc[0]//3 + 10, cc[1]//3 + 10, cc[2]//3 + 12), edge=cc, r=8)
        fr.text((xx + w/2 - 3, y0 + 32), lab, 20, TXT, a, anchor="mm")
        xx += w
    gx0, gx1, gy0, gy1 = x0, x1, 460, 800
    a_ax = rev(t, 3.5)
    fr.line([(gx0, gy0), (gx0, gy1), (gx1, gy1)], DIM, 3, a_ax, a_ax)
    fr.text((gx0 - 20, gy0), "50 mA", 22, DIM, a_ax, anchor="rm")
    fr.text((gx0 - 20, gy1 - 130), "10 mA", 22, DIM, a_ax, anchor="rm")
    fr.text((gx0 - 20, gy1), "~ uA", 22, DIM, a_ax, anchor="rm")
    prof = [(0.00, 0.004), (0.30, 0.004), (0.30, 0.10), (0.36, 0.10), (0.36, 0.95),
            (0.50, 0.95), (0.50, 0.30), (0.66, 0.30), (0.66, 0.75), (0.80, 0.75), (0.80, 0.004), (1.00, 0.004)]
    pts = [(gx0 + p * (gx1 - gx0), gy1 - v * (gy1 - gy0 - 40)) for p, v in prof]
    fr.line(pts, GREEN, 5, rev(t, 4.0), rev(t, 4.0, 5.0))
    fr.text((gx0 + 0.43 * (gx1 - gx0), gy0 + 10), "flash + expose: ~45 mA", 22, AMBER, rev(t, 6.5), anchor="mm")
    fr.text((gx0 + 0.73 * (gx1 - gx0), gy0 + 105), "radio burst: ~11 mA (0 dBm)", 22, RED, rev(t, 8.0), anchor="mm")
    fr.text((gx0 + 0.15 * (gx1 - gx0), gy1 - 40), "sleep floor: microamps", 22, DIM, rev(t, 9.0), anchor="mm")
    fr.text((W/2, 880), "Average < 5 mA even though peaks hit 50 mA — high-drain cells + bulk capacitors absorb the spikes.",
            26, DIM, rev(t, 11.0), anchor="mm")
    fr.text((W/2, 930), "45 mAh / ~4.5 mA  =  ~10 hours of mission time. Every design choice serves this equation.",
            26, TEAL, rev(t, 14.0), anchor="mm")

# ---------------------------------------------------------------- S07 packet
FIELDS = [("magic", 2, TEAL), ("frame", 2, BLUE), ("chunk", 2, BLUE), ("n_chunks", 2, BLUE),
          ("flags", 1, PURPLE), ("len", 1, PURPLE), ("data", 110, GREEN), ("crc16", 2, RED)]
def s07(fr, t):
    fr.title("The wire format", t, "122-byte chunks — dumb, debuggable, loss-tolerant")
    x0, x1, y0 = 160, 1760, 300
    total = sum(b for _, b, _ in FIELDS)
    xx = x0
    for i, (lab, b, cc) in enumerate(FIELDS):
        w = (x1 - x0) * (b / total if lab != "data" else 0.42)
        if lab != "data":
            w = max(w, 95)
        a = rev(t, 0.8 + i * 0.5)
        fr.box(xx, y0, w - 4, 70, a, fill=(cc[0]//4 + 12, cc[1]//4 + 12, cc[2]//4 + 14), edge=cc, r=8)
        fr.text((xx + w/2 - 2, y0 + 24), lab, 22, TXT, a, anchor="mm")
        fr.text((xx + w/2 - 2, y0 + 52), f"{b} B", 18, DIM, a, anchor="mm")
        xx += w
    fr.text((x1 + 10, y0 + 35), "= 122 B", 24, DIM, rev(t, 4.8), anchor="lm")
    txx, txy = 260, 560
    fr.chip(txx, txy, 200, 110, "TX", "capsule", rev(t, 5.5), edge=AMBER)
    fr.chip(1460, txy, 200, 110, "RX", "LaunchPad + PC", rev(t, 5.5), edge=GREEN)
    fr.line([(txx + 200, txy + 55), (1460, txy + 55)], DIM, 3, rev(t, 5.8), rev(t, 5.8), dash=(12, 10))
    if t > 6.3:
        for k in range(4):
            fr.packet([(txx + 200, txy + 55), (1460, txy + 55)], (t - 6.3) / 3.2 + k * 0.25, AMBER)
    gx, gy, cell = 1700, 520, 44
    got = int(max(0, (t - 6.8)) * 2.2)
    for i in range(16):
        a = 1.0 if i < got else 0.15
        cx, cy = gx + (i % 4) * cell, gy + (i // 4) * cell
        fr.box(cx, cy, cell - 6, cell - 6, min(a, rev(t, 6.5)), fill=(40, 90, 60) if i < got else PANEL, edge=EDGE, r=6)
    fr.text((gx + 2 * cell - 3, gy - 30), "frame reassembly", 20, DIM, rev(t, 6.5), anchor="mm")
    fr.text((W/2, 800), "Sequence numbers + CRC16. A lost chunk just drops that frame — the next one arrives in half a second.",
            26, DIM, rev(t, 9.5), anchor="mm")
    fr.text((W/2, 850), "Same format for every camera variant, so the receiver and viewer never change.",
            26, DIM, rev(t, 12.0), anchor="mm")

# ---------------------------------------------------------------- S08 variants
def s08(fr, t):
    fr.title("Two ways to get color", t, "both fit the same power budget and wire format")
    for side, x0 in ((0, 120), (1, 1000)):
        a = rev(t, 0.6 + side * 0.4)
        fr.box(x0, 220, 800, 560, a, fill=(18, 23, 30), edge=TEAL if side == 0 else AMBER, r=18, ew=3)
    fr.text((520, 270), "Variant A — HM01B0 (mono) + RGB flash", 30, TEAL, rev(t, 1.0), bold=True, anchor="mm")
    cols = [(RED, "R"), (GREEN, "G"), (BLUE, "B")]
    for i, (cc, lab) in enumerate(cols):
        a = rev(t, 1.6 + i * 1.2)
        on = ((t - 1.6 - i * 1.2) % 3.6) < 1.2 if t > 1.6 else False
        px = 250 + i * 90
        fr.d.ellipse([px, 330, px + 60, 390], fill=col_a(cc if on else PANEL, a), outline=col_a(cc, a), width=3)
        fr.text((px + 30, 420), lab + " flash", 20, DIM, a, anchor="mm")
        fy = 470
        fr.box(215 + i * 95, fy, 85, 64, rev(t, 2.0 + i * 1.2), fill=(60, 60, 64), edge=EDGE, r=6)
        fr.text((257 + i * 95, fy + 32), "frame", 17, DIM, rev(t, 2.0 + i * 1.2), anchor="mm")
    fr.arrow([(520, 560), (520, 620)], DIM, 3, rev(t, 5.4), rev(t, 5.4))
    fr.box(430, 630, 180, 90, rev(t, 5.8), fill=(50, 80, 60), edge=GREEN, r=8)
    fr.text((520, 675), "fused color", 22, TXT, rev(t, 5.8), anchor="mm")
    fr.text((520, 755), "3 mono captures + software fusion - sensor stays < 2 mW", 21, DIM, rev(t, 6.4), anchor="mm")
    fr.text((1400, 270), "Variant B — HM0360 (native Bayer)", 30, AMBER, rev(t, 1.4), bold=True, anchor="mm")
    bx, by, c = 1180, 330, 40
    bayer = [GREEN, RED, BLUE, GREEN]
    for i in range(16):
        a = rev(t, 2.0 + (i % 4) * 0.2)
        cc = bayer[(i % 2) + 2 * ((i // 4) % 2)]
        fr.box(bx + (i % 4) * c, by + (i // 4) * c, c - 4, c - 4, a,
               fill=(cc[0]//2, cc[1]//2, cc[2]//2), edge=EDGE, r=4)
    fr.text((bx + 2 * c, by + 4 * c + 30), "Bayer mosaic - one shot", 20, DIM, rev(t, 3.0), anchor="mm")
    fr.arrow([(bx + 4 * c + 40, by + 2 * c), (bx + 4 * c + 180, by + 2 * c)], DIM, 3, rev(t, 3.6), rev(t, 3.6),
             label="demosaic on Apollo510", lab_dy=-30, lab_size=20)
    fr.box(bx + 4 * c + 200, by + c - 10, 180, 120, rev(t, 4.2), fill=(50, 80, 60), edge=GREEN, r=8)
    fr.text((bx + 4 * c + 290, by + c + 50), "color frame", 22, TXT, rev(t, 4.2), anchor="mm")
    fr.text((1400, 560), "~140 uA @ QVGA 2 fps — lower than the mono HM01B0!", 22, DIM, rev(t, 5.0), anchor="mm")
    fr.text((1400, 610), "caveat: color CFA variant is special-order;", 21, DIM, rev(t, 6.0), anchor="mm")
    fr.text((1400, 645), "hobby modules ship monochrome", 21, DIM, rev(t, 6.0), anchor="mm")
    fr.text((W/2, 860), "Build A first (all hand-solderable), then B on the custom board — LED ring, rails and firmware carry over.",
            26, DIM, rev(t, 8.5), anchor="mm")

# ---------------------------------------------------------------- S09 roadmap
PHASES = [("Phase 0", "Teardown + docs", True), ("Phase 1", "Two LaunchPads + camera link", False),
          ("Phase 2", "Protocol + power discipline", False), ("Phase 3", "25 mm round boards + demo pill", False),
          ("Phase 4", "Phantom-tissue RF experiments", False)]
def s09(fr, t):
    fr.title("The roadmap", t, "each phase is a self-contained learning milestone")
    for i, (ph, desc, done) in enumerate(PHASES):
        a = rev(t, 0.8 + i * 0.9)
        x = 160 + i * 330
        fr.box(x, 380, 290, 240, a, fill=(18, 23, 30), edge=GREEN if done else EDGE, r=14, ew=3)
        fr.text((x + 145, 430), ph, 32, GREEN if done else TXT, a, bold=True, anchor="mm")
        fr.text((x + 145, 500), desc, 23, DIM, a, anchor="mm", maxw=250)
        if done:
            fr.text((x + 145, 570), "DONE", 26, GREEN, a, bold=True, anchor="mm")
        if i < 4:
            fr.arrow([(x + 292, 500), (x + 328, 500)], DIM, 3, rev(t, 1.2 + i * 0.9), rev(t, 1.2 + i * 0.9))
    fr.text((W/2, 730), "Phase 1 needs ~$100 and zero soldering. The whole curriculum: hardware, firmware, RF, and power engineering.",
            26, DIM, rev(t, 6.0), anchor="mm")
    fr.text((W/2, 790), "Contributions welcome — antennas, measurements, translations, experiments.",
            26, TEAL, rev(t, 8.0), anchor="mm")

# ---------------------------------------------------------------- S10 outro
def s10(fr, t):
    pulse = 0.75 + 0.25 * math.sin(t * 2.4)
    fr.capsule_icon(W/2, 420, scale=1.3, alpha=rev(t, 0.2, 1.0), leds_on=(pulse > 0.72))
    fr.text((W/2, 610), "OpenCapsule-EDU", 72, TXT, rev(t, 0.8), bold=True, anchor="mm")
    fr.text((W/2, 690), "github.com/basel5099/opencapsul", 40, (126, 200, 227), rev(t, 1.5), anchor="mm")
    fr.text((W/2, 770), "Educational bench replica — NOT a medical device. Never ingest electronics.",
            26, DIM, rev(t, 2.2), anchor="mm")
    fr.text((W/2, 850), "Read the full teardown, power math, and wiring plans in the repo.",
            24, DIM, rev(t, 3.0), anchor="mm")

SCENES = [("s01", 8, s01), ("s02", 18, s02), ("s03", 20, s03), ("s04", 22, s04), ("s05", 18, s05),
          ("s06", 20, s06), ("s07", 16, s07), ("s08", 16, s08), ("s09", 12, s09), ("s10", 10, s10)]

if __name__ == "__main__":
    only = sys.argv[1:] or None
    for name, secs, fn in SCENES:
        if only and name not in only: continue
        render_scene(name, secs, fn)
    print("ALL SCENES RENDERED")
