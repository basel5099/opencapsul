# Bill of Materials — phased

Prices are rough 2026 street prices; check current availability. Parts are chosen so
Phase 1 needs **zero soldering**.

> **Architecture update:** the project adopted the **Ambiq Apollo510** as the processing
> unit between camera and radio — see [docs/architecture-apollo510.md](../docs/architecture-apollo510.md)
> for the rationale, dev boards, and full wiring plan. The Phase 1 list below still
> stands for the radio-link-only start; add the Apollo hardware (Phase 1B) when the
> link works.

## Phase 1 — Working radio + camera link (~$100–170)

| # | Part | Qty | ~Price | Role | Notes |
|---|---|---|---|---|---|
| 1 | TI **LAUNCHXL-CC1310** LaunchPad | 2 | $30 ea | TX ("capsule") + RX (receiver) | Same silicon as the real capsule. If unavailable, LAUNCHXL-CC1312R7 works with minor SDK changes |
| 2 | **Arducam Mega 3 MP** (SPI) | 1 | $40 | Camera + built-in JPEG | Stands in for sensor + compression ASIC; 5 MP version also fine |
| 3 | Jumper wires / headers | — | $5 | SPI hookup | Camera SPI ≤ 4 MHz to match CC1310 SSI |
| 4 | **Nordic PPK2** power profiler | 1 | $100 | Current measurement | *Strongly* recommended — the learning multiplier. Optional but budget for it |

## Phase 1B — Add the "brain" (Apollo510) (~$255)

| # | Part | Qty | ~Price | Role | Notes |
|---|---|---|---|---|---|
| 1 | **Ambiq AP510EVB** (Apollo510 EVB Rev 2.2) | 1 | $245 | Processing unit dev board | On-board J-Link, USB-C, MikroBUS socket for camera SPI; Zephyr-supported |
| 2 | **TXB0104** level-shifter breakout | 2 | $3 ea | EVB (≤2.2 V IO) ↔ LaunchPad (3.3 V) and ↔ Mega (3.3 V) | Dropped in Phase 3 (shared 2.0 V rail) |

## Phase 2 — Protocol & power discipline (no new hardware)

Firmware-only phase: duty cycling, chunked frames, CRC, loss-tolerant viewer.
Optional: 10 Ω shunt + scope if no PPK2.

## Phase 3 — Miniaturized round-board stack (~$60–120 in parts + PCB run)

Round 25 mm 2-layer PCBs (hand-solderable with hot air), stacked on 1.27 mm headers
inside the 3D-printed demo pill.

### Radio board

| Part | Example | Role |
|---|---|---|
| Wireless MCU | **CC1310F128RHB** (VQFN-32, 5×5) | Same as teardown unit |
| 24 MHz crystal | Epson FA-238 24.0000MB or similar, ±10 ppm | X24M_N/P; load caps are on-chip (datasheet §6.8) |
| RF front end | **Johanson 0868BM15A0001** (868 MHz) or **0896BM15A0001** (915 MHz) integrated balun-filter *matched to CC13xx* | Replaces the discrete LC balun cluster of the original — one part, datasheet-matched |
| DC/DC inductor | 6.8 µH 0603/0805, per TI reference design | DCDC_SW pin |
| Antenna | Meandered PCB trace (TI DN024 / SWRA416 as guides) or 868/915 chip antenna | Tune with NanoVNA (~$60, shared lab tool) |
| Decoupling set | Per TI CC1310EM reference BOM | Copy the reference design religiously |
| Programming | **cJTAG 2-wire** via XDS110 on a LaunchPad (jumper wires to TMSC/TCKC pads) | No extra debugger needed |

### Processor ("brain") board

| Part | Example | Role |
|---|---|---|
| SoC | **Ambiq Apollo510** (AP510NFA-CCR, WLCSP 4.9×4.7) | Camera driver + JPEG/AI triage + power FSM (see docs/architecture-apollo510.md) |
| SIMO buck inductor | Murata **DFE201210U-2R2M=P2** 2.2 µH 0805 | Required by datasheet §30.2.2 |
| Crystals | 48 MHz + 32.768 kHz | Apollo clock sources |
| Bypass set | Per datasheet Table 36/37 (10 µF VDDP, 2.2 µF VDDH…) | Copy exactly |
| Note | WLCSP/BGA — **assembly service required** (JLCPCB/PCBWay), not hand-solderable | |

### Camera board — two color variants (pick one, or build A then B)

**Variant A — HM01B0 mono + sequential RGB flash** (see [docs/camera-variant-A-hm01b0-rgb-fusion.md](../docs/camera-variant-A-hm01b0-rgb-fusion.md))

| Part | Example | Role |
|---|---|---|
| Sensor module | **SparkFun HM01B0 (SEN-15570)** or Arducam HM01B0 for Pico | Proven Apollo-family driver exists (SparkFun Edge) |
| AVDD LDO | TI **TPS7A02-28** (1.0×1.0 mm) | 2.8 V analog rail from battery |
| LEDs | 2× red + 2× green + 2× blue, 0603 | Sequential illumination (replaces white ring) |
| Channel switches | 3× DMN2075U SOT-23 N-FET | One GPIO per color from Apollo510 |
| LED boost | TI **TLV61046A** (SOT-563), ~3.6 V | Green/blue Vf exceeds battery near end-of-life |

**Variant B — HM0360 Bayer (native color)** (see [docs/camera-variant-B-hm0360-color.md](../docs/camera-variant-B-hm0360-color.md))

| Part | Example | Role |
|---|---|---|
| Bring-up module | Arducam HM0360 for RP2040 (**monochrome**) | Driver + timing development, riskless |
| Production sensor | **HM0360 Bayer-CFA variant** (special-order via distributor/Himax rep, bare CSP) | Native single-shot color; ~140 µA @ QVGA 2 fps |
| AVDD LDO | TPS7A02-28 | Same rail plan as Variant A |
| LEDs | 4× white 0603 (baseline ring) + TLV61046A boost | Bayer filters do the color separation |

Both variants keep the Arducam Mega as the Phase 1–2 bench camera.

### Power board

| Part | Example | Role |
|---|---|---|
| Buck regulator | **TI TPS62740** (360 nA Iq) | Sensor/logic rails; teaches quiescent-current thinking |
| Bulk caps | 2–4× 100–220 µF tantalum/MLCC | Pulse reservoir — size from power-budget doc |
| Magnetic switch | **SI7201** Hall-effect or MK24 reed | Keep-off-in-package, like the real capsule |
| Battery holders | 2× Keystone 3001 (SR927/LR927 size) or 1× CR2032 holder for cheap runs | **Holders, never solder to cells** |
| Cells (demo) | 2× SR927 / LR927 | LR927 (alkaline) is a cheap stand-in for bring-up; SR927 for the "real" discharge-curve experiment |

### LED ring board

| Part | Example | Role |
|---|---|---|
| White LEDs | 4× 0603 white, ~120° viewing angle | Pulsed via MOSFET from a GPIO |
| Photodiode (optional) | VEMD5060X01 | Auto-exposure experiment |
| N-FET | DMN2075U or similar SOT-23 | LED flash switch |

## Phase 3 mechanical

| Item | Notes |
|---|---|
| Demo pill shell, 30 × 70 mm | 3D-printed in two halves + clear resin dome; **intentionally not swallowable** (see SAFETY doc) |
| Standoffs / 1.27 mm stack headers | Board stacking |

## Receiver side (all phases)

Second LaunchPad + USB. Optional upgrade: RF explorer or SDR dongle (~$30) to *see*
your bursts and verify duty cycle/occupied bandwidth.

## Sourcing notes

- CC1310F128RHB: Mouser/DigiKey, ~$4–6 @ qty 1.
- Johanson baluns: ~$0.50 — the single best part-for-part shortcut in this project.
- Murata micro-battery business transferred to **Maxell** (March 2026) — search both
  brands for SR927/SR927R availability.
