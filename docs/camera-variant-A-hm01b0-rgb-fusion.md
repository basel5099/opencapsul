# Camera Variant A — HM01B0 (mono) + sequential RGB flash + fusion

Color imaging from a monochrome sensor: flash the scene **red**, capture a frame,
flash **green**, capture, flash **blue**, capture — then fuse the three grayscale
frames into one RGB image on the Apollo510. This is **field-sequential color (FSC)**,
a real technique used in early color TV and in some medical endoscopy systems.

```
        flash R          flash G          flash B
          │                │                │
   [mono frame 1]   [mono frame 2]   [mono frame 3]
          └────────────────┴────────────────┘
                           ▼
              fuse → RGB image → JPEG → CC1310
```

Why it fits this project: the sensor stays the ultra-low-power HM01B0 (< 2 mW, with
the proven SparkFun/Ambiq driver), and the only hardware change is on a board we
fully control anyway — the LED ring.

---

## 1. Hardware changes (LED ring board only)

Replace the 4 white LEDs with **6 LEDs in 3 switched channels**, opposite pairs for
symmetric illumination:

```
        [R]                 ring layout: R–G–B–R–G–B at 60° spacing,
     [B]   [G]              each color = 2 opposing LEDs
     [G]   [B]              → every channel illuminates symmetrically,
        [R]                 no color-dependent shadowing
```

| Item | Part example | Notes |
|---|---|---|
| 2× red 0603 LED | Vf ≈ 2.0 V | easy on any rail |
| 2× green 0603 LED | Vf ≈ 2.9–3.2 V | ⚠ see rail note |
| 2× blue 0603 LED | Vf ≈ 2.7–3.1 V | ⚠ see rail note |
| 3× N-FET SOT-23 (or 1× triple-channel driver) | DMN2075U ×3 | one GPIO per color channel from the Apollo510 |
| Series resistors | set for ~20 mA/LED pulse | per channel |

**⚠ The LED-rail problem (applies to the white-LED build too):** green/blue Vf can
exceed the battery voltage once the SR927R stack sags toward end-of-life (~2.4–2.6 V).
Drive the LED rail from a tiny **boost converter** (e.g., TI TLV61046A, SOT-563, set
~3.6 V) switched on only around the flash window. This also makes flash brightness
independent of battery state — which matters for color balance (§3).

**Spectral honesty:** a mono sensor + R/G/B LEDs samples three narrow bands rather
than broad Bayer curves; colors are "LED-true", not colorimetric. Good enough to see
red vs. pale tissue in a phantom — document it, don't oversell it.

## 2. Capture sequence (Apollo510 firmware FSM)

```
DEEP_SLEEP
  └─ RTC tick (1 color-frame period)
WAKE
  ├─ boost rail ON, HM01B0 out of standby
  ├─ for ch in [R, G, B]:
  │     ├─ LED[ch] ON
  │     ├─ trigger exposure, read frame ch into SRAM (100 KB × 3 — fits easily)
  │     └─ LED[ch] OFF
  ├─ boost rail OFF, sensor to standby
  ├─ FUSE (§3) → RGB, optional triage CNN ("send/skip")
  ├─ JPEG encode (4:2:0), chunk, stream to CC1310 (READY-gated)
  └─ back to DEEP_SLEEP
```

Timing: HM01B0 does 60 fps ⇒ 16.7 ms/frame ⇒ the 3 captures span ~50 ms. The capsule
scene moves slowly, so fringing is rare — but during fast motion (peristalsis in the
real device, shaking the demo pill here) the three exposures see different scenes and
edges show **color fringes**. That artifact *is* the lesson of this variant.

## 3. Fusion algorithm

Naive fusion is one line per pixel — the channels are already spatially aligned
(same sensor, same optics):

```c
// gains calibrated once against a gray card (§3.1)
out.r = clamp(g_r * frameR[i]);
out.g = clamp(g_g * frameG[i]);
out.b = clamp(g_b * frameB[i]);
```

### 3.1 White balance calibration
LED radiant flux and sensor quantum efficiency differ per band. Calibrate once:
photograph a neutral gray target, compute mean of each frame, set
`g_ch = target_level / mean_ch`. Store the three gains in flash. Re-check when LED
batch changes.

### 3.2 Motion de-fringing (stretch goal)
Estimate a global shift between frame R and frame B (±2 px search, SAD on a 4×-decimated
copy — cheap on Helium) and shift channels before fusing. Skip per-pixel optical flow;
it is not worth the power.

### 3.3 Host-side prototype
[`tools/rgb_fusion.py`](../tools/rgb_fusion.py) fuses three grayscale captures on the
PC so you can validate gains and fringing behavior **before** writing a line of
firmware. Feed it three frames dumped over UART from Milestone M2.

## 4. Power cost vs. mono

Per color frame ≈ 3 mono captures + fusion:

| Item | Cost |
|---|---|
| 3× flash pulses (2 LEDs × ~20 mA × ~5 ms) | ~0.6 mJ-class per frame |
| 3× sensor frames | < 1 mJ (HM01B0 is ~2 mW *continuous* at 30 fps) |
| Fusion + JPEG on Apollo (few ms @ 96 MHz, ~1.9 mA) | negligible |
| Boost converter overhead | ~10 % on the flash energy only |

At **1 color-fps** the whole camera+illumination subsystem stays ≈ **0.3–0.5 mA
average** — the radio still dominates the budget (see §4.4 of
[architecture-apollo510.md](architecture-apollo510.md)). Battery verdict: unchanged, ✅.

## 5. Pros / cons summary

| ✅ | ❌ |
|---|---|
| Proven sensor + proven Apollo-family driver | 3× capture time → motion fringes |
| Cheapest color path (LEDs + FETs, ~$2) | LED-band colors, not colorimetric |
| Teaches illumination engineering & WB calibration | Needs boost rail (but white build wants it too) |
| Mono sensor stays available in hobby modules | Fusion firmware to write (host prototype provided) |
