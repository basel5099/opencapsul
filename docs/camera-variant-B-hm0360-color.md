# Camera Variant B — HM0360, Bayer RGB variant (native color)

Single-sensor native color: the **Himax HM0360** is the HM01B0's bigger sibling in the
same "always-on vision" family, and its datasheet lists **both Bayer RGB and
monochrome CFA variants**. With the color variant, one flash + one capture per frame —
no fusion, no fringing.

```
white flash → [HM0360 Bayer frame] → demosaic (Apollo/Helium) → JPEG → CC1310
```

---

## 1. Why it fits

| Requirement | HM0360 (official figures) |
|---|---|
| Power at our operating point | **~140 µA @ QVGA 2 fps** (!) — lower than HM01B0's budget line |
| Binned low-power mode | < 500 µW @ 3 fps |
| Full VGA 60 fps | 14.5 mW (we never need this) |
| Resolution | 640×480, windowable — run a **320×240 QVGA window** to match the project |
| Interface | Same Himax style as HM01B0: I²C control + 8/4-bit video port ⇒ the ported SparkFun-driver approach carries over |
| Extra gifts | Internal self-oscillator (**no MCLK needed** from the Apollo — one timer freed), <2 ms frame trigger, auto-wake, context switching — built for pulsed duty cycling like ours |

## 2. Sourcing — the one real hurdle

Hobby modules (Arducam HM0360 for RP2040, Arduino ecosystem) ship the **monochrome**
variant. For color you must explicitly order the **Bayer-CFA part** through a
distributor (Mouser/DigiKey/Himax rep) — likely as a bare CSP sensor for the Phase-3
camera board rather than a ready module.

Practical path:
1. **Bring-up on the mono module** (cheap, available) — driver, timing, power FSM.
2. **Swap to the Bayer part on the custom board** — same registers, same interface;
   only the demosaic step in firmware turns on.

Rails: same class as HM01B0 (2.8 V analog + 1.8 V-class I/O — reuse the TPS7A02 LDO
plan; verify exact min/max in the datasheet DC tables when ordering).

## 3. Firmware pipeline on the Apollo510

Process **per 8-line strip**, not per frame — memory stays tiny and the JPEG encoder
wants 8-line MCU rows anyway:

```
capture Bayer strip (320×8 = 2.5 KB)
  → bilinear demosaic (Helium-vectorized, ~few cycles/px)
  → simple gray-world AWB (running per-channel means)
  → RGB→YCbCr, 4:2:0 subsample
  → JPEG-encode strip → chunk → CC1310 (READY-gated)
```

- Bayer QVGA frame = 77 KB; strip pipeline needs **< 10 KB working RAM** — the
  3.75 MB SRAM then serves frame history / triage CNN instead.
- Demosaic + JPEG at QVGA is a few ms per frame at 96 MHz — the duty-cycle math in
  [architecture-apollo510.md](architecture-apollo510.md) §4.4 is unchanged (~2.3 mA
  system average @ 1 fps → comfortably inside the 4.5 mA battery budget ✅).

## 4. Illumination

Keep the **4× white LED** ring from the baseline design (the Bayer filters do the
color separation). The boost-rail note from Variant A still applies to white LEDs
near battery end-of-life — share that rail design between both variants.

## 5. Pros / cons summary

| ✅ | ❌ |
|---|---|
| True single-shot color — no fringing, normal color science | Color CFA part must be special-ordered (bare sensor, assembly service) |
| Even lower sensor power than HM01B0 at 2 fps | Demosaic firmware to write (strip pipeline above) |
| Internal oscillator simplifies the Apollo side | Slightly larger die/module than HM01B0 |
| Mono module = riskless bring-up path | White LEDs only exercise half the illumination lesson |

## 6. Choosing between Variant A and B

| If you want… | Pick |
|---|---|
| Cheapest parts, everything hand-solderable, illumination/fusion lessons | **A** (HM01B0 + RGB) |
| Best image quality, single-shot color, closest to the commercial capsule | **B** (HM0360 Bayer) |
| The full curriculum | Build **A first** (all-module hardware), then **B** on the Phase-3 custom board — the LED ring, power rails, Apollo driver, and CC1310 modem carry over unchanged |

Both variants speak the same `cap_chunk_t` wire format — the receiver and viewer never
know which camera produced the frame.

## References

- HM0360 product page: <https://www.himax.com.tw/products/cmos-image-sensor/always-on-vision-sensors/hm0360/>
- HM0360 datasheet (UCTronics mirror): <https://www.uctronics.com/download/Datasheet/HM0360-image-sensor-datasheet.pdf>
- Launch PR with power figures (140 µA @ QVGA 2 fps, 14.5 mW @ VGA 60 fps): <https://www.globenewswire.com/news-release/2020/01/22/1973570/0/en/Himax-Launches-HM0360-1-6-VGA-Ultra-Low-Power-CMOS-Image-Sensor-for-AIoT-and-Computer-Vision-Applications.html>
- Arducam HM0360 module (monochrome — bring-up only): <https://www.arducam.com/product/arducam-hm0360-vga-cmos-mocochrome-camera-module-for-rp2040-arduino/>
