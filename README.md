# OpenCapsule-EDU 💊📡

**An open educational platform for learning how wireless capsule endoscopes work — built on the bench, never in a body.**

> ⚠️ **THIS IS NOT A MEDICAL DEVICE.** This project is a bench-top learning replica of the *electronics architecture* of a capsule endoscope. It must **never be swallowed, implanted, or used on humans or animals** in any way. Read [SAFETY_AND_LEGAL.md](SAFETY_AND_LEGAL.md) before doing anything else.

---

## ملخص بالعربية

هذا مشروع تعليمي مفتوح المصدر يشرح ويعيد بناء البنية الإلكترونية لكبسولة المنظار اللاسلكية (كاميرا + ضغط صور + إرسال لاسلكي دون 1 جيجاهرتز + إدارة طاقة من خلايا زر) كنموذج مختبري على الطاولة، **للتعلم فقط وليس للاستخدام الطبي إطلاقاً**. المشروع مبني على تشريح كامل لكبسولة تجارية حقيقية (موثّق في [docs/teardown-analysis.md](docs/teardown-analysis.md)) ويقود المتعلم عبر مراحل عملية: من لوحات التطوير الجاهزة إلى تصميم لوحات دائرية مصغّرة، مع حسابات ميزانية الطاقة والبروتوكول اللاسلكي كاملة.

---

## Why this project exists

Commercial capsule endoscopes (PillCam, MiroCam, OMOM, ANKON…) are marvels of extreme
low-power embedded design: a camera, an image-compression engine, a sub-1 GHz radio,
and a power system that runs 8–12 hours — all inside an 11 × 26 mm swallowable shell
powered by two watch batteries.

Almost nothing about how they *actually* work is documented publicly. This repository
changes that, in two ways:

1. **A full teardown analysis** of a real commercial capsule, component by component,
   cross-checked against manufacturer datasheets → [docs/teardown-analysis.md](docs/teardown-analysis.md)
2. **A reproducible bench-top replica** of the same architecture that any student or
   hobbyist can build from off-the-shelf parts, then progressively miniaturize.

**Learning outcomes:** ultra-low-power firmware design, pulsed power budgeting,
sub-GHz RF links, image transport over constrained radios, coin-cell chemistry,
rigid-flex mechanical design, and the regulatory landscape around medical RF devices.

---

## The architecture we are replicating

This is the signal chain found in the real capsule (see the teardown doc for evidence):

```
                        ┌──────────────────── 11 × 26 mm capsule ────────────────────┐
                        │                                                             │
  light pulse           │  [4× white LEDs]                                            │
  ~140° optics          │  [wide-angle lens + CMOS sensor ~320×320, chip-on-board]    │
  HW compression        │  [custom ASIC "LJ215C" + frame memory + own crystal]        │
  power                 │  [PMU board: regulators, bulk caps, magnetic ON/OFF switch] │
  energy                │  [2× Murata SR927R silver-oxide, 3.1 V, 45 mAh, high-drain] │
  radio                 │  [TI CC1310F128 (RHB 5×5) + 24 MHz XTAL + balun/filter]     │
  antenna               │  [meandered flex-PCB antenna, rolled into the rear shell]   │
                        │                                                             │
                        └─────────────────────────────────────────────────────────────┘
                                                   │  sub-1 GHz RF burst
                                                   ▼
                        [on-body receiver belt] → [recorder] → [physician workstation]
```

Key design insight from the teardown — **everything is pulsed**: LEDs flash only during
exposure, the radio transmits in short bursts, and bulk capacitors + a high-drain
battery variant absorb the 40–50 mA peaks while the *average* current stays under
~5 mA. That single idea is what makes 45 mAh last 10 hours.

---

## Our educational replica — design mapping

We deliberately substitute parts that are impossible for hobbyists (custom ASIC,
chip-on-board sensor, 10 mm rigid-flex) with accessible equivalents that preserve
the *architecture*:

| Function | Real capsule | OpenCapsule-EDU | Why |
|---|---|---|---|
| MCU + radio | TI **CC1310F128** (RHB) | Same family: **CC1310 LaunchPad** (Phase 1) → CC1310F128RHB on custom PCB (Phase 3) | Identical firmware, datasheet-faithful |
| Image sensor + compression | Bare CMOS die + custom ASIC (LJ215C) | Bench: **Arducam Mega SPI** (JPEG in-module). Battery build, two color variants: **A)** HM01B0 mono + sequential RGB flash + fusion, **B)** HM0360 Bayer native color — see `docs/camera-variant-A/B` | Processing runs on an **Ambiq Apollo510** (`docs/architecture-apollo510.md`) — the modern stand-in for the custom ASIC |
| Battery | 2× Murata SR927R (45 mAh, high-drain) | Bench PSU / 2× AAA (Phase 1) → 2× SR927/LR927 in holders (Phase 3, demo only) | Safe, measurable; silver-oxide math still taught in [docs/power-budget.md](docs/power-budget.md) |
| Power management | Custom PMU board, bulk caps, magnetic switch | TPS62740 buck + bulk caps + Hall-effect switch (SI7201) | Same three-layer pulse strategy |
| Antenna | Meandered flex antenna | Wire monopole (Phase 1) → meandered PCB antenna (Phase 3) | Progressive difficulty |
| Shell | 11 × 26 mm medical shell | **3D-printed 30 × 70 mm demo pill** (intentionally too big to swallow) | Safety by design |
| Receiver | Body-worn sensor belt | Second CC1310 LaunchPad + Python viewer on PC | Full link, visible results |

---

## Project phases

**Phase 0 — Paper (done, this repo):** teardown analysis, power budget, architecture.
Deliverables: [docs/teardown-analysis.md](docs/teardown-analysis.md), [docs/power-budget.md](docs/power-budget.md).

**Phase 1 — Two LaunchPads (~$100):** establish the sub-GHz link. Stream test
patterns, then real JPEGs from the Arducam over SPI → radio → PC viewer.
Measure everything with a power profiler. *This phase alone teaches 70 % of the system.*

**Phase 2 — Protocol + power discipline:** implement the pulsed duty cycle
(sleep → wake → capture → compress → burst → sleep), frame chunking with CRC + sequence
numbers, loss-tolerant viewer, average-current target < 10 mA.

**Phase 3 — Miniaturization:** custom round 25 mm PCBs (CC1310F128RHB, integrated-balun
front end, TPS62740, coin-cell holders), stacked with board-to-board headers inside the
3D-printed demo pill. Meandered PCB antenna tuned with a NanoVNA.

**Phase 4 — Community stretch goals:** phantom-tissue propagation experiments
(RF through saline/gelatin — classic and safe lab exercise), FEC on the link,
frame-rate/quality auto-adaptation, receiver diversity with two LaunchPads.

---

## Repository layout

```
opencapsule-edu/
├── README.md                  ← you are here
├── SAFETY_AND_LEGAL.md        ← read this FIRST
├── LICENSE                    ← MIT (code); hardware docs CC-BY-SA 4.0
├── docs/
│   ├── teardown-analysis.md   ← full commercial-capsule teardown, with evidence
│   ├── power-budget.md        ← the 45 mAh / 10 h math, pulse analysis, how to measure
│   ├── architecture-apollo510.md            ← processing-unit choice + full wiring plan
│   ├── camera-variant-A-hm01b0-rgb-fusion.md ← color via mono sensor + RGB flash
│   └── camera-variant-B-hm0360-color.md      ← color via Bayer HM0360
├── hardware/
│   └── BOM.md                 ← phased bill of materials with prices and sources
├── firmware/
│   └── README.md              ← toolchain, TX/RX architecture, packet format, viewer
└── tools/
    └── rgb_fusion.py          ← host-side RGB fusion prototype (Variant A)
```

---

## Quick start (Phase 1)

1. Read [SAFETY_AND_LEGAL.md](SAFETY_AND_LEGAL.md) — especially the RF-band table for your country.
2. Buy the Phase 1 parts: [hardware/BOM.md](hardware/BOM.md) (2× LAUNCHXL-CC1310, 1× Arducam Mega, 1× Nordic PPK2 recommended).
3. Follow [firmware/README.md](firmware/README.md) to flash the TX and RX examples and run the Python viewer.
4. First milestone: a JPEG photographed by the "capsule", radioed across the room at 868/915 MHz, appearing on your screen — with a current-consumption trace to analyze.

---

## Contributing

Issues and PRs are welcome: better antenna designs, cleaner power measurements,
translations (an Arabic translation of the docs is a stated goal — ملاحظة: الترجمة
العربية الكاملة للوثائق هدف معلن للمشروع), phantom-tissue experiment writeups.
Please keep every contribution within the safety rules — anything that moves the
project toward ingestion or clinical use will be rejected.

## Acknowledgements & references

- TI **CC1310** datasheet SWRS181D — pinout, application circuit, clock system: <https://www.ti.com/lit/ds/symlink/cc1310.pdf>
- Murata **SR927R** high-drain silver-oxide cell: <https://www.murata.com/en-us/products/productdetail?partno=SR927R>
- Khan & Wahid, *Design of a Lossless Image Compression System for Video Capsule Endoscopy*, Sensors 2014: <https://pmc.ncbi.nlm.nih.gov/articles/PMC4279511/>
- Xie et al., *A Wireless Capsule Endoscope System With Low-Power Controlling and Processing ASIC*: <https://pubmed.ncbi.nlm.nih.gov/23853159/>
- The anonymous commercial capsule that gave its life for the teardown 🔬
